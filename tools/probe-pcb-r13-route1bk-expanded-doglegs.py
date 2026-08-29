#!/usr/bin/env python3
"""Read-only Manhattan dogleg screening for ordinary route-1bg ratsnest pairs."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bj"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bj-r13.kicad_pcb"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bj.json"

WIDTH = 0.30
RULE = 0.10
MAX_ENDPOINT_DISTANCE = 18.0
GRID = 0.05
LANE_MARGIN = 6.0
EPS = 1e-9

EXCLUDED_REFS = {
    "U1", "J3", "J5", "J6", "J7",
    "C7", "C8", "C9", "C10", "C11", "C12", "C401",
}
EXCLUDED_NETS = {
    "RF_A", "RF_B", "RF_ANT", "RF_MCU", "NRF_DECA_RF", "NRF_DECD",
    "BIO_SW", "DISP_SW", "CHG_5V", "LDO2_IN",
    "PMIC_SW1", "PMIC_SW2", "PVSS1_LOCAL", "SYS_I2C_SCL",
}
EXCLUDED_NET_PREFIXES = ("NRF_XC", "NRF_XL")

PAD_RE = re.compile(r"^Pad\s+(\S+)\s+\[([^\]]+)\]\s+of\s+(\S+)\s+on\s+Top_layer$")
NET_RE = re.compile(r"\[([^\]]+)\]")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mm(value: int) -> float:
    return float(pcbnew.ToMM(value))


def xy(v) -> tuple[float, float]:
    return (round(mm(v.x), 6), round(mm(v.y), 6))


def bbox(item) -> tuple[float, float, float, float]:
    b = item.GetBoundingBox()
    return (mm(b.GetX()), mm(b.GetY()), mm(b.GetRight()), mm(b.GetBottom()))


def orient(a, b, c) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def on_segment(a, b, p) -> bool:
    return (
        min(a[0], b[0]) - EPS <= p[0] <= max(a[0], b[0]) + EPS
        and min(a[1], b[1]) - EPS <= p[1] <= max(a[1], b[1]) + EPS
        and abs(orient(a, b, p)) <= EPS
    )


def segments_intersect(a, b, c, d) -> bool:
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    if ((o1 > EPS and o2 < -EPS) or (o1 < -EPS and o2 > EPS)) and (
        (o3 > EPS and o4 < -EPS) or (o3 < -EPS and o4 > EPS)
    ):
        return True
    return (
        on_segment(a, b, c)
        or on_segment(a, b, d)
        or on_segment(c, d, a)
        or on_segment(c, d, b)
    )


def point_segment_distance(p, a, b) -> float:
    vx, vy = b[0] - a[0], b[1] - a[1]
    wx, wy = p[0] - a[0], p[1] - a[1]
    vv = vx * vx + vy * vy
    if vv <= EPS:
        return math.dist(p, a)
    t = max(0.0, min(1.0, (wx * vx + wy * vy) / vv))
    q = (a[0] + t * vx, a[1] + t * vy)
    return math.dist(p, q)


def segment_segment_distance(a, b, c, d) -> float:
    if segments_intersect(a, b, c, d):
        return 0.0
    return min(
        point_segment_distance(a, c, d),
        point_segment_distance(b, c, d),
        point_segment_distance(c, a, b),
        point_segment_distance(d, a, b),
    )


def point_in_rect(p, r) -> bool:
    return r[0] - EPS <= p[0] <= r[2] + EPS and r[1] - EPS <= p[1] <= r[3] + EPS


def point_rect_distance(p, r) -> float:
    dx = max(r[0] - p[0], 0.0, p[0] - r[2])
    dy = max(r[1] - p[1], 0.0, p[1] - r[3])
    return math.hypot(dx, dy)


def segment_rect_distance(a, b, r) -> float:
    if point_in_rect(a, r) or point_in_rect(b, r):
        return 0.0
    corners = [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    if any(segments_intersect(a, b, c, d) for c, d in zip(corners, corners[1:] + corners[:1])):
        return 0.0
    return min(
        point_rect_distance(a, r),
        point_rect_distance(b, r),
        *(point_segment_distance(c, a, b) for c in corners),
    )


def endpoint(desc: str, pos: dict) -> dict:
    m = PAD_RE.match(desc)
    if m:
        return {
            "kind": "pad",
            "pad": m.group(1),
            "net": m.group(2),
            "ref": m.group(3),
            "description": desc,
            "pos": [pos["x"], pos["y"]],
        }
    nm = NET_RE.search(desc)
    return {
        "kind": "track" if desc.startswith("Track ") else "other",
        "pad": None,
        "net": nm.group(1) if nm else None,
        "ref": None,
        "description": desc,
        "pos": [pos["x"], pos["y"]],
    }


def exclusion_reason(candidate: dict) -> str | None:
    a, b, net = candidate["a"], candidate["b"], candidate["net"]
    if net in EXCLUDED_NETS or any(net.startswith(prefix) for prefix in EXCLUDED_NET_PREFIXES):
        return "excluded_net"
    if a["ref"] in EXCLUDED_REFS or b["ref"] in EXCLUDED_REFS:
        return "excluded_ref"
    if a["kind"] == "other" or b["kind"] == "other":
        return "unsupported_endpoint"
    if "Top_layer" not in a["description"] or "Top_layer" not in b["description"]:
        return "non_top_layer"
    if a["ref"] and b["ref"] and a["ref"] == b["ref"] and a["pad"] == b["pad"]:
        return "duplicate_terminal_same_component"
    if candidate["endpoint_distance_mm"] > MAX_ENDPOINT_DISTANCE:
        return "too_long"
    return None


def frange(start: float, stop: float, step: float) -> list[float]:
    first = math.floor(start / step) * step
    last = math.ceil(stop / step) * step
    count = int(round((last - first) / step))
    return [round(first + i * step, 6) for i in range(count + 1)]


def normalize_path(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for p in points:
        q = (round(float(p[0]), 6), round(float(p[1]), 6))
        if not out or math.dist(out[-1], q) > EPS:
            out.append(q)
    return out


def path_length(points: list[tuple[float, float]]) -> float:
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def endpoint_semantic_rank(c: dict) -> int:
    kinds = (c["a"]["kind"], c["b"]["kind"])
    if kinds == ("pad", "pad"):
        return 0
    if "pad" in kinds and "track" in kinds:
        return 1
    return 2


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--route1bj-drc-json", required=True)
    ap.add_argument("--route1bj-pin-net-audit", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    report = load_json(SRC_REPORT)
    src_sha = sha256(SRC_PCB)
    if report.get("output_sha256") != src_sha:
        raise SystemExit("route1bk dogleg source SHA gate failed")

    drc = load_json(Path(args.route1bj_drc_json))
    audit = load_json(Path(args.route1bj_pin_net_audit))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 114:
        raise SystemExit("route1bk dogleg DRC source gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bk dogleg audit source gate failed")

    raw: list[dict] = []
    for idx, unconn in enumerate(drc["unconnected_items"]):
        if len(unconn.get("items", [])) != 2:
            continue
        x, y = unconn["items"]
        a = endpoint(x["description"], x["pos"])
        b = endpoint(y["description"], y["pos"])
        if not a["net"] or a["net"] != b["net"]:
            continue
        c = {
            "drc_index": idx,
            "net": a["net"],
            "a": a,
            "b": b,
            "endpoint_distance_mm": round(math.dist(a["pos"], b["pos"]), 6),
        }
        c["exclusion_reason"] = exclusion_reason(c)
        raw.append(c)

    board = pcbnew.LoadBoard(str(SRC_PCB))
    pads: list[dict] = []
    tracks: list[dict] = []
    vias: list[dict] = []

    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.IsOnLayer(pcbnew.F_Cu):
                pads.append({
                    "reference": fp.GetReference(),
                    "pad": str(p.GetNumber()),
                    "net": p.GetNetname(),
                    "bbox": bbox(p),
                })

    for item in board.GetTracks():
        net = item.GetNetname() if hasattr(item, "GetNetname") else ""
        if isinstance(item, pcbnew.PCB_VIA):
            r = bbox(item)
            vias.append({
                "net": net,
                "pos": xy(item.GetPosition()),
                "radius": max(r[2] - r[0], r[3] - r[1]) / 2.0,
            })
        elif item.GetLayer() == pcbnew.F_Cu:
            tracks.append({
                "net": net,
                "start": xy(item.GetStart()),
                "end": xy(item.GetEnd()),
                "width": mm(item.GetWidth()),
            })

    def evaluate_path(net: str, points: list[tuple[float, float]]) -> dict:
        segs = list(zip(points, points[1:]))
        if not segs:
            return {"clearance_mm": -999.0, "nearest": None}

        best_clearance = float("inf")
        nearest = None
        half = WIDTH / 2.0

        def consider(clearance: float, item: dict) -> None:
            nonlocal best_clearance, nearest
            if clearance < best_clearance:
                best_clearance = clearance
                nearest = item

        for p in pads:
            if p["net"] == net:
                continue
            clearance = min(segment_rect_distance(a, b, p["bbox"]) - half for a, b in segs)
            consider(clearance, {
                "kind": "pad",
                "reference": p["reference"],
                "pad": p["pad"],
                "net": p["net"],
            })

        for t in tracks:
            if t["net"] == net:
                continue
            clearance = min(
                segment_segment_distance(a, b, t["start"], t["end"]) - half - t["width"] / 2.0
                for a, b in segs
            )
            consider(clearance, {
                "kind": "track",
                "net": t["net"],
                "start_mm": list(t["start"]),
                "end_mm": list(t["end"]),
                "width_mm": round(t["width"], 6),
            })

        for v in vias:
            if v["net"] == net:
                continue
            clearance = min(point_segment_distance(v["pos"], a, b) - v["radius"] - half for a, b in segs)
            consider(clearance, {
                "kind": "via",
                "net": v["net"],
                "position_mm": list(v["pos"]),
            })

        return {
            "clearance_mm": round(best_clearance, 6),
            "nearest": nearest,
        }

    evaluated: list[dict] = []
    for c in raw:
        if c["exclusion_reason"]:
            continue

        A = (float(c["a"]["pos"][0]), float(c["a"]["pos"][1]))
        B = (float(c["b"]["pos"][0]), float(c["b"]["pos"][1]))

        candidates: list[dict] = []

        def add_path(kind: str, pts: list[tuple[float, float]], lane: float | None = None) -> None:
            pts = normalize_path(pts)
            if len(pts) < 2 or len(pts) > 4:
                return
            length = path_length(pts)
            if length > max(24.0, c["endpoint_distance_mm"] * 2.5):
                return
            e = evaluate_path(c["net"], pts)
            candidates.append({
                "path_family": kind,
                "lane_mm": lane,
                "points_mm": [[p[0], p[1]] for p in pts],
                "segment_count": len(pts) - 1,
                "path_length_mm": round(length, 6),
                "minimum_conservative_clearance_mm": e["clearance_mm"],
                "nearest_unrelated_copper": e["nearest"],
                "rule_pass": e["clearance_mm"] + 1e-6 >= RULE,
            })

        add_path("L-HV", [A, (B[0], A[1]), B])
        add_path("L-VH", [A, (A[0], B[1]), B])

        for lane_x in frange(min(A[0], B[0]) - LANE_MARGIN, max(A[0], B[0]) + LANE_MARGIN, GRID):
            add_path("HVH", [A, (lane_x, A[1]), (lane_x, B[1]), B], lane_x)

        for lane_y in frange(min(A[1], B[1]) - LANE_MARGIN, max(A[1], B[1]) + LANE_MARGIN, GRID):
            add_path("VHV", [A, (A[0], lane_y), (B[0], lane_y), B], lane_y)

        unique: dict[tuple, dict] = {}
        for p in candidates:
            key = tuple(tuple(x) for x in p["points_mm"])
            old = unique.get(key)
            if old is None or p["minimum_conservative_clearance_mm"] > old["minimum_conservative_clearance_mm"]:
                unique[key] = p
        candidates = list(unique.values())

        passing = [p for p in candidates if p["rule_pass"]]
        passing.sort(key=lambda p: (
            p["segment_count"],
            p["path_length_mm"],
            -p["minimum_conservative_clearance_mm"],
        ))

        best = passing[0] if passing else None
        evaluated.append({
            **c,
            "endpoint_semantic_rank": endpoint_semantic_rank(c),
            "path_count": len(candidates),
            "passing_path_count": len(passing),
            "best_passing_path": best,
            "top_passing_paths": passing[:5],
        })

    passing_candidates = [c for c in evaluated if c["best_passing_path"] is not None]
    passing_candidates.sort(key=lambda c: (
        c["endpoint_semantic_rank"],
        c["best_passing_path"]["segment_count"],
        c["best_passing_path"]["path_length_mm"],
        -c["best_passing_path"]["minimum_conservative_clearance_mm"],
        c["endpoint_distance_mm"],
    ))

    excluded = [c for c in raw if c["exclusion_reason"]]
    exclusion_summary: dict[str, int] = {}
    for c in excluded:
        reason = c["exclusion_reason"]
        exclusion_summary[reason] = exclusion_summary.get(reason, 0) + 1

    out = {
        "revision": "r13-route1bk-expanded-manhattan-dogleg-screen",
        "source_route1bj_sha256": src_sha,
        "source_gate": {
            "rule_violations": 0,
            "unconnected_items": 114,
            "pin_net_audit": "PASS",
            "audited_nodes": 268,
        },
        "board_modified": False,
        "track_width_mm": WIDTH,
        "rule_clearance_mm": RULE,
        "grid_mm": GRID,
        "lane_margin_mm": LANE_MARGIN,
        "max_endpoint_distance_mm": MAX_ENDPOINT_DISTANCE,
        "raw_pair_count": len(raw),
        "evaluated_candidate_count": len(evaluated),
        "passing_candidate_count": len(passing_candidates),
        "passing_candidates": passing_candidates,
        "nonpassing_candidates": [c for c in evaluated if c["best_passing_path"] is None],
        "exclusion_summary": exclusion_summary,
        "release_status": "NOT_FOR_GERBER",
    }

    Path(args.output).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "source_gate": out["source_gate"],
        "evaluated_candidate_count": out["evaluated_candidate_count"],
        "passing_candidate_count": out["passing_candidate_count"],
        "passing": [
            {
                "drc_index": c["drc_index"],
                "net": c["net"],
                "a": c["a"]["description"],
                "b": c["b"]["description"],
                "endpoint_semantic_rank": c["endpoint_semantic_rank"],
                "endpoint_distance_mm": c["endpoint_distance_mm"],
                "best_path": c["best_passing_path"],
            }
            for c in passing_candidates[:20]
        ],
        "exclusions": exclusion_summary,
    }, indent=2))

    if out["board_modified"] is not False or out["raw_pair_count"] < 100:
        raise SystemExit("route1bk expanded dogleg state gate failed")


if __name__ == "__main__":
    main()
