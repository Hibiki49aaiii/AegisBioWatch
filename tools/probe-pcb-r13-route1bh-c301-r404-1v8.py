#!/usr/bin/env python3
"""Read-only route-1bh geometry/clearance probe for C301.1 -> R404.1."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bg"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bg-r13.kicad_pcb"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bg.json"

START = (13.755, 23.725)
END = (15.755, 26.725)
TRACK_WIDTH = 0.30
RULE_CLEARANCE = 0.10
EPS = 1e-9


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
    return (
        round(mm(b.GetX()), 6),
        round(mm(b.GetY()), 6),
        round(mm(b.GetRight()), 6),
        round(mm(b.GetBottom()), 6),
    )


def pad(fp, number: str):
    ps = [p for p in fp.Pads() if str(p.GetNumber()) == str(number)]
    if len(ps) != 1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(ps)}")
    return ps[0]


def point_segment_distance(p, a, b) -> float:
    px, py = p
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    vv = vx * vx + vy * vy
    if vv <= EPS:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (wx * vx + wy * vy) / vv))
    qx, qy = ax + t * vx, ay + t * vy
    return math.hypot(px - qx, py - qy)


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
    if (o1 > EPS and o2 < -EPS or o1 < -EPS and o2 > EPS) and (
        o3 > EPS and o4 < -EPS or o3 < -EPS and o4 > EPS
    ):
        return True
    return (
        on_segment(a, b, c)
        or on_segment(a, b, d)
        or on_segment(c, d, a)
        or on_segment(c, d, b)
    )


def segment_segment_distance(a, b, c, d) -> float:
    if segments_intersect(a, b, c, d):
        return 0.0
    return min(
        point_segment_distance(a, c, d),
        point_segment_distance(b, c, d),
        point_segment_distance(c, a, b),
        point_segment_distance(d, a, b),
    )


def point_rect_distance(p, r) -> float:
    x, y = p
    x0, y0, x1, y1 = r
    dx = max(x0 - x, 0.0, x - x1)
    dy = max(y0 - y, 0.0, y - y1)
    return math.hypot(dx, dy)


def point_in_rect(p, r) -> bool:
    return r[0] - EPS <= p[0] <= r[2] + EPS and r[1] - EPS <= p[1] <= r[3] + EPS


def segment_rect_distance(a, b, r) -> float:
    if point_in_rect(a, r) or point_in_rect(b, r):
        return 0.0
    x0, y0, x1, y1 = r
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    edges = list(zip(corners, corners[1:] + corners[:1]))
    if any(segments_intersect(a, b, c, d) for c, d in edges):
        return 0.0
    return min(
        point_rect_distance(a, r),
        point_rect_distance(b, r),
        *(point_segment_distance(c, a, b) for c in corners),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--route1bg-drc-json", required=True)
    ap.add_argument("--route1bg-pin-net-audit", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    report = load_json(SRC_REPORT)
    source_sha = sha256(SRC_PCB)
    if report.get("output_sha256") != source_sha:
        raise SystemExit("route1bh probe route1bg report/PCB SHA mismatch")

    drc = load_json(Path(args.route1bg_drc_json))
    audit = load_json(Path(args.route1bg_pin_net_audit))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 116:
        raise SystemExit("route1bh probe route1bg DRC gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bh probe route1bg pin/net gate failed")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    c301, r404 = fps.get("C301"), fps.get("R404")
    if c301 is None or r404 is None:
        raise SystemExit("route1bh probe missing C301/R404")
    if c301.GetValue() != "100nF" or r404.GetValue() != "4.7k PU PROV":
        raise SystemExit(f"route1bh value gate failed C301={c301.GetValue()!r} R404={r404.GetValue()!r}")

    c1, c2, r1, r2 = pad(c301, "1"), pad(c301, "2"), pad(r404, "1"), pad(r404, "2")
    observed = {
        "C301.1": {"net": c1.GetNetname(), "position_mm": list(xy(c1.GetPosition())), "bbox_mm": list(bbox(c1))},
        "C301.2": {"net": c2.GetNetname(), "position_mm": list(xy(c2.GetPosition())), "bbox_mm": list(bbox(c2))},
        "R404.1": {"net": r1.GetNetname(), "position_mm": list(xy(r1.GetPosition())), "bbox_mm": list(bbox(r1))},
        "R404.2": {"net": r2.GetNetname(), "position_mm": list(xy(r2.GetPosition())), "bbox_mm": list(bbox(r2))},
    }
    expected = {
        "C301.1": ("+1V8", [13.755, 23.725]),
        "C301.2": ("GND", [14.395, 23.725]),
        "R404.1": ("+1V8", [15.755, 26.725]),
        "R404.2": ("SYS_I2C_SCL", [16.395, 26.725]),
    }
    for key, (net, pos) in expected.items():
        if observed[key]["net"] != net or observed[key]["position_mm"] != pos:
            raise SystemExit(f"route1bh endpoint/net gate failed {key}: {observed[key]}")

    target_pads = {("C301", "1"), ("R404", "1")}
    unrelated = []
    same_net_context = []
    min_clearance = float("inf")

    def record(rec: dict, clearance: float, same_net: bool) -> None:
        nonlocal min_clearance
        rec["conservative_clearance_mm"] = round(clearance, 6)
        if same_net:
            same_net_context.append(rec)
            return
        unrelated.append(rec)
        min_clearance = min(min_clearance, clearance)

    candidate_half = TRACK_WIDTH / 2.0

    for fp in board.GetFootprints():
        for p in fp.Pads():
            if not p.IsOnLayer(pcbnew.F_Cu):
                continue
            key = (fp.GetReference(), str(p.GetNumber()))
            if key in target_pads:
                continue
            pb = bbox(p)
            center_to_copper = segment_rect_distance(START, END, pb)
            clearance = center_to_copper - candidate_half
            record(
                {
                    "kind": "pad",
                    "reference": fp.GetReference(),
                    "pad": str(p.GetNumber()),
                    "net": p.GetNetname(),
                    "bbox_mm": list(pb),
                },
                clearance,
                p.GetNetname() == "+1V8",
            )

    for item in board.GetTracks():
        net = item.GetNetname() if hasattr(item, "GetNetname") else ""
        if isinstance(item, pcbnew.PCB_VIA):
            pos = xy(item.GetPosition())
            b = bbox(item)
            radius = max(b[2] - b[0], b[3] - b[1]) / 2.0
            clearance = point_segment_distance(pos, START, END) - radius - candidate_half
            record(
                {"kind": "via", "net": net, "position_mm": list(pos), "bbox_mm": list(b)},
                clearance,
                net == "+1V8",
            )
        else:
            if item.GetLayer() != pcbnew.F_Cu:
                continue
            a = xy(item.GetStart())
            b = xy(item.GetEnd())
            width = mm(item.GetWidth())
            clearance = segment_segment_distance(START, END, a, b) - width / 2.0 - candidate_half
            record(
                {
                    "kind": "track",
                    "net": net,
                    "start_mm": list(a),
                    "end_mm": list(b),
                    "width_mm": round(width, 6),
                },
                clearance,
                net == "+1V8",
            )

    unrelated.sort(key=lambda x: x["conservative_clearance_mm"])
    same_net_context.sort(key=lambda x: x["conservative_clearance_mm"])
    nearest_unrelated = unrelated[:12]
    nearest_same_net = same_net_context[:8]

    if min_clearance == float("inf"):
        raise SystemExit("route1bh probe found no unrelated F.Cu copper; unexpected geometry state")

    out = {
        "revision": "r13-route1bh-c301-r404-1v8-clearance-probe",
        "source_route1bg_sha256": source_sha,
        "source_gate": {"rule_violations": 0, "unconnected_items": 116, "pin_net_audit": "PASS", "audited_nodes": 268},
        "board_modified": False,
        "C301_value": c301.GetValue(),
        "R404_value": r404.GetValue(),
        "pads": observed,
        "candidate": {
            "start_mm": list(START),
            "end_mm": list(END),
            "track_width_mm": TRACK_WIDTH,
            "length_mm": round(math.dist(START, END), 6),
            "rule_clearance_mm": RULE_CLEARANCE,
        },
        "minimum_conservative_unrelated_clearance_mm": round(min_clearance, 6),
        "nearest_unrelated_copper": nearest_unrelated,
        "nearest_same_net_context": nearest_same_net,
        "release_status": "NOT_FOR_GERBER",
    }
    Path(args.output).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))

    if min_clearance + 1e-6 < RULE_CLEARANCE:
        raise SystemExit(
            f"route1bh probe clearance gate failed: {min_clearance:.6f} < {RULE_CLEARANCE:.6f}"
        )


if __name__ == "__main__":
    main()
