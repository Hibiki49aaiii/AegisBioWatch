#!/usr/bin/env python3
"""Read-only 0.05 mm local refine for Issue #19 route-1bm R305.2 -> U4.10 VSYS_HAPTIC."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bl"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bl-r13.kicad_pcb"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bl.json"
PHASE_A2 = ROOT / "docs/pcb-route-r13-1bm-screen-phase-a2.json"

WIDTH = 0.30
RULE = 0.10
GRID = 0.05
X_MIN = 24.00
X_MAX = 26.00
Y_MIN = 16.50
Y_MAX = 18.00
MAX_PATH_LENGTH = 16.0
EPS = 1e-9

TARGET_NET = "VSYS_HAPTIC"
R305_PAD2 = (31.315, 18.595)
U4_PAD10 = (23.005, 13.400)
COARSE_X = 25.000
COARSE_Y = 17.500
BYPASS_BEND = (16.005, 21.650)
BYPASS_POINTS = [
    (6.805, 22.335),
    (6.805, 21.650),
    (16.005, 21.650),
    (16.005, 23.725),
]


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


def frange(start: float, stop: float, step: float) -> list[float]:
    first = math.floor(start / step) * step
    last = math.ceil(stop / step) * step
    count = int(round((last - first) / step))
    return [round(first + i * step, 6) for i in range(count + 1)]


def normalize(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for p in points:
        q = (round(float(p[0]), 6), round(float(p[1]), 6))
        if not out or math.dist(out[-1], q) > EPS:
            out.append(q)
    return out


def path_length(points: list[tuple[float, float]]) -> float:
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def get_pad(fp, number: str):
    pads = [p for p in fp.Pads() if str(p.GetNumber()) == str(number)]
    if len(pads) != 1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(pads)}")
    return pads[0]


def near(a: tuple[float, float], b: tuple[float, float], tol: float = 0.002) -> bool:
    return math.dist(a, b) <= tol


def item_pos(item: dict) -> tuple[float, float]:
    p = item.get("pos", {})
    return (float(p.get("x", 1e9)), float(p.get("y", 1e9)))


def has_pad(item: dict, ref: str, pad: str) -> bool:
    d = item.get("description", "")
    return d == f"Pad {pad} [{TARGET_NET}] of {ref} on Top_layer"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--route1bl-drc-json", required=True)
    ap.add_argument("--route1bl-pin-net-audit", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    report = load_json(SRC_REPORT)
    src_sha = sha256(SRC_PCB)
    if report.get("output_sha256") != src_sha:
        raise SystemExit("route1bm refine source report/PCB SHA gate failed")

    drc = load_json(Path(args.route1bl_drc_json))
    audit = load_json(Path(args.route1bl_pin_net_audit))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 112:
        raise SystemExit("route1bm refine DRC source gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bm refine audit source gate failed")

    phase_a2 = load_json(PHASE_A2)
    passes = {int(c["drc_index"]): c for c in phase_a2.get("passing_candidates", [])}
    c111 = passes.get(111)
    c110 = passes.get(110)
    if c111 is None or c110 is None:
        raise SystemExit("route1bm refine Phase A2 VSYS_HAPTIC candidate gate failed")
    if (
        c111.get("net") != TARGET_NET
        or c111.get("from") != "R305.2/VSYS_HAPTIC @ (31.315,18.595)"
        or c111.get("to") != "U4.10/VSYS_HAPTIC @ (23.005,13.400)"
        or c111.get("coarse_path_family") != "VHVH"
    ):
        raise SystemExit("route1bm refine preferred coarse candidate changed")
    if c110.get("from") != "VSYS_HAPTIC track endpoint @ (16.004999,21.650)":
        raise SystemExit("route1bm refine alternate coarse candidate changed")

    r305_u4_matches = []
    bypass_u4_matches = []
    for idx, u in enumerate(drc.get("unconnected_items", [])):
        items = u.get("items", [])
        if len(items) != 2:
            continue
        if any(has_pad(x, "R305", "2") for x in items) and any(has_pad(x, "U4", "10") for x in items):
            r305_u4_matches.append(idx)
        has_u4 = any(has_pad(x, "U4", "10") for x in items)
        has_bypass_track = any(
            x.get("description", "").startswith(f"Track [{TARGET_NET}]")
            and near(item_pos(x), BYPASS_BEND)
            for x in items
        )
        if has_u4 and has_bypass_track:
            bypass_u4_matches.append(idx)

    if len(r305_u4_matches) != 1:
        raise SystemExit(f"route1bm refine R305/U4 topology cardinality failed: {r305_u4_matches}")
    if len(bypass_u4_matches) != 1:
        raise SystemExit(f"route1bm refine bypass/U4 topology cardinality failed: {bypass_u4_matches}")
    if r305_u4_matches[0] == bypass_u4_matches[0]:
        raise SystemExit("route1bm refine expected distinct VSYS_HAPTIC unconnected representatives")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    r305 = fps.get("R305")
    u4 = fps.get("U4")
    c305 = fps.get("C305")
    c304 = fps.get("C304")
    if None in (r305, u4, c305, c304):
        raise SystemExit("route1bm refine missing haptic supply components")
    if r305.GetValue() != "0R / FB OPTION" or u4.GetValue() != "DRV2605LDGSR":
        raise SystemExit("route1bm refine R305/U4 identity gate failed")
    if c305.GetValue() != "1uF" or c304.GetValue() != "100nF":
        raise SystemExit("route1bm refine C305/C304 identity gate failed")

    r305p2 = get_pad(r305, "2")
    u4p10 = get_pad(u4, "10")
    c305p1 = get_pad(c305, "1")
    c304p1 = get_pad(c304, "1")
    if (r305p2.GetNetname(), xy(r305p2.GetPosition())) != (TARGET_NET, R305_PAD2):
        raise SystemExit("route1bm refine R305.2 gate failed")
    if (u4p10.GetNetname(), xy(u4p10.GetPosition())) != (TARGET_NET, U4_PAD10):
        raise SystemExit("route1bm refine U4.10 gate failed")
    if (c305p1.GetNetname(), xy(c305p1.GetPosition())) != (TARGET_NET, BYPASS_POINTS[0]):
        raise SystemExit("route1bm refine C305.1 gate failed")
    if (c304p1.GetNetname(), xy(c304p1.GetPosition())) != (TARGET_NET, BYPASS_POINTS[-1]):
        raise SystemExit("route1bm refine C304.1 gate failed")

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

    bypass_segment_hits = []
    r305_touching_tracks = []
    u4_touching_tracks = []
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
            start, end = xy(item.GetStart()), xy(item.GetEnd())
            width = mm(item.GetWidth())
            tracks.append({"net": net, "start": start, "end": end, "width": width})
            if net == TARGET_NET and abs(width - WIDTH) < 1e-6:
                for a, b in zip(BYPASS_POINTS, BYPASS_POINTS[1:]):
                    if {start, end} == {a, b}:
                        bypass_segment_hits.append((a, b))
                if start == R305_PAD2 or end == R305_PAD2:
                    r305_touching_tracks.append((start, end))
                if start == U4_PAD10 or end == U4_PAD10:
                    u4_touching_tracks.append((start, end))

    if len(bypass_segment_hits) != 3:
        raise SystemExit(f"route1bm refine accepted bypass geometry gate failed: {bypass_segment_hits}")
    if r305_touching_tracks:
        raise SystemExit(f"route1bm refine R305.2 unexpectedly already routed: {r305_touching_tracks}")
    if u4_touching_tracks:
        raise SystemExit(f"route1bm refine U4.10 unexpectedly already routed: {u4_touching_tracks}")

    def evaluate(points: list[tuple[float, float]]) -> tuple[float, dict | None]:
        segs = list(zip(points, points[1:]))
        best = float("inf")
        nearest = None
        half = WIDTH / 2.0

        def consider(clearance: float, item: dict) -> None:
            nonlocal best, nearest
            if clearance < best:
                best = clearance
                nearest = item

        for p in pads:
            if p["net"] == TARGET_NET:
                continue
            clearance = min(segment_rect_distance(a, b, p["bbox"]) - half for a, b in segs)
            consider(clearance, {
                "kind": "pad",
                "reference": p["reference"],
                "pad": p["pad"],
                "net": p["net"],
            })

        for t in tracks:
            if t["net"] == TARGET_NET:
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
            if v["net"] == TARGET_NET:
                continue
            clearance = min(point_segment_distance(v["pos"], a, b) - v["radius"] - half for a, b in segs)
            consider(clearance, {
                "kind": "via",
                "net": v["net"],
                "position_mm": list(v["pos"]),
            })

        return round(best, 6), nearest

    raw: list[dict] = []
    for lane_x in frange(X_MIN, X_MAX, GRID):
        for lane_y in frange(Y_MIN, Y_MAX, GRID):
            points = normalize([
                R305_PAD2,
                (R305_PAD2[0], lane_y),
                (lane_x, lane_y),
                (lane_x, U4_PAD10[1]),
                U4_PAD10,
            ])
            if len(points) != 5:
                continue
            length = path_length(points)
            if length > MAX_PATH_LENGTH + EPS:
                continue
            clearance, nearest = evaluate(points)
            raw.append({
                "path_family": "VHVH",
                "lane_x_mm": lane_x,
                "lane_y_mm": lane_y,
                "points_mm": [list(p) for p in points],
                "segment_count": 4,
                "path_length_mm": round(length, 6),
                "minimum_conservative_clearance_mm": clearance,
                "nearest_unrelated_copper": nearest,
                "rule_pass": clearance + 1e-6 >= RULE,
            })

    passing = [p for p in raw if p["rule_pass"]]
    raw.sort(key=lambda p: (-p["minimum_conservative_clearance_mm"], p["path_length_mm"], p["points_mm"]))
    passing.sort(key=lambda p: (-p["minimum_conservative_clearance_mm"], p["path_length_mm"], p["points_mm"]))

    coarse_anchor = [
        list(R305_PAD2),
        [R305_PAD2[0], COARSE_Y],
        [COARSE_X, COARSE_Y],
        [COARSE_X, U4_PAD10[1]],
        list(U4_PAD10),
    ]
    anchor_results = [p for p in raw if p["points_mm"] == coarse_anchor]
    if len(anchor_results) != 1:
        raise SystemExit("route1bm refine coarse-anchor cardinality gate failed")

    out = {
        "revision": "r13-route1bm-r305-u4-vsys-haptic-local-refine",
        "issue": 19,
        "source_route1bl_sha256": src_sha,
        "source_gate": {
            "rule_violations": 0,
            "unconnected_items": 112,
            "pin_net_audit": "PASS",
            "audited_nodes": 268,
        },
        "board_modified": False,
        "semantic_topology_review": {
            "preferred_family": "R305.2/VSYS_HAPTIC -> U4.10/VSYS_HAPTIC",
            "preferred_reason": "exact pad-to-pad landing; avoids T-junction materialization into accepted route-1bk bypass copper; shorter coarse path than the track-to-pad alternate",
            "r305_u4_drc_indices": r305_u4_matches,
            "bypass_u4_drc_indices": bypass_u4_matches,
            "distinct_unconnected_representatives": True,
            "accepted_bypass_segment_count": len(bypass_segment_hits),
            "r305_touching_vsys_haptic_track_count": len(r305_touching_tracks),
            "u4_touching_vsys_haptic_track_count": len(u4_touching_tracks),
            "alternate_family_status": "HOLD_NOT_SELECTED",
            "candidate_selected_for_materialization": False,
        },
        "net": TARGET_NET,
        "R305_value": r305.GetValue(),
        "U4_value": u4.GetValue(),
        "C305_value": c305.GetValue(),
        "C304_value": c304.GetValue(),
        "from_pad": {"reference": "R305", "pad": "2", "position_mm": list(R305_PAD2), "net": TARGET_NET},
        "to_pad": {"reference": "U4", "pad": "10", "position_mm": list(U4_PAD10), "net": TARGET_NET},
        "track_width_mm": WIDTH,
        "rule_clearance_mm": RULE,
        "grid_mm": GRID,
        "x_range_mm": [X_MIN, X_MAX],
        "y_range_mm": [Y_MIN, Y_MAX],
        "max_segments": 4,
        "max_path_length_mm": MAX_PATH_LENGTH,
        "candidate_path_count": len(raw),
        "passing_path_count": len(passing),
        "coarse_anchor_result": anchor_results[0],
        "best_passing_path": passing[0] if passing else None,
        "top_passing_paths": passing[:20],
        "top_clearance_paths": raw[:20],
        "decision_state": {
            "refine_complete": True,
            "candidate_selected_for_phase_b": False,
            "phase_b_started": False,
            "accepted_authority_changed": False,
            "next_action": "Review refined winner and only then create exact Phase B probe/materializer for one path.",
        },
        "release_status": "NOT_FOR_GERBER",
    }
    Path(args.output).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))

    if not passing:
        raise SystemExit("route1bm refine found no legal R305.2 -> U4.10 VHVH path")


if __name__ == "__main__":
    main()
