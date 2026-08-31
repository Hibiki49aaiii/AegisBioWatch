#!/usr/bin/env python3
"""Read-only exact Phase B probe for Issue #20 route-1bn +1V8 source track -> R403.1."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bm"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bm-r13.kicad_pcb"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bm.json"
PHASE_A2 = ROOT / "docs/pcb-route-r13-1bn-r403-refine-phase-a2.json"

TARGET_NET = "+1V8"
WIDTH = 0.30
RULE = 0.10
EXPECTED_CLEARANCE = 0.26
SOURCE_ENDPOINT = (41.005, 14.975)
SOURCE_TRACK_LENGTH_MM = 4.6628
R403_PAD1 = (40.255, 25.975)
R403_PAD2 = (40.895, 25.975)
POINTS = [
    SOURCE_ENDPOINT,
    (41.005, 15.650),
    (39.600, 15.650),
    (39.600, 25.975),
    R403_PAD1,
]
SEGMENT_LENGTHS = [0.675, 1.405, 10.325, 0.655]
TOTAL_LENGTH = 13.06
EPS = 1e-9


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mm(v) -> float:
    return float(pcbnew.ToMM(v))


def xy(v) -> tuple[float, float]:
    return (round(mm(v.x), 6), round(mm(v.y), 6))


def bbox(item) -> tuple[float, float, float, float]:
    b = item.GetBoundingBox()
    return (mm(b.GetX()), mm(b.GetY()), mm(b.GetRight()), mm(b.GetBottom()))


def get_pad(fp, number: str):
    pads = [p for p in fp.Pads() if str(p.GetNumber()) == str(number)]
    if len(pads) != 1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(pads)}")
    return pads[0]


def near(a, b, tol: float = 0.002) -> bool:
    return math.dist(a, b) <= tol


def orient(a, b, c) -> float:
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def on_segment(a, b, p) -> bool:
    return (
        min(a[0], b[0])-EPS <= p[0] <= max(a[0], b[0])+EPS
        and min(a[1], b[1])-EPS <= p[1] <= max(a[1], b[1])+EPS
        and abs(orient(a, b, p)) <= EPS
    )


def segments_intersect(a, b, c, d) -> bool:
    o1, o2, o3, o4 = orient(a,b,c), orient(a,b,d), orient(c,d,a), orient(c,d,b)
    if ((o1 > EPS and o2 < -EPS) or (o1 < -EPS and o2 > EPS)) and (
        (o3 > EPS and o4 < -EPS) or (o3 < -EPS and o4 > EPS)
    ):
        return True
    return on_segment(a,b,c) or on_segment(a,b,d) or on_segment(c,d,a) or on_segment(c,d,b)


def point_segment_distance(p, a, b) -> float:
    vx, vy = b[0]-a[0], b[1]-a[1]
    wx, wy = p[0]-a[0], p[1]-a[1]
    vv = vx*vx + vy*vy
    if vv <= EPS:
        return math.dist(p, a)
    t = max(0.0, min(1.0, (wx*vx+wy*vy)/vv))
    q = (a[0]+t*vx, a[1]+t*vy)
    return math.dist(p, q)


def segment_segment_distance(a,b,c,d) -> float:
    if segments_intersect(a,b,c,d):
        return 0.0
    return min(
        point_segment_distance(a,c,d),
        point_segment_distance(b,c,d),
        point_segment_distance(c,a,b),
        point_segment_distance(d,a,b),
    )


def point_in_rect(p,r) -> bool:
    return r[0]-EPS <= p[0] <= r[2]+EPS and r[1]-EPS <= p[1] <= r[3]+EPS


def point_rect_distance(p,r) -> float:
    dx = max(r[0]-p[0], 0.0, p[0]-r[2])
    dy = max(r[1]-p[1], 0.0, p[1]-r[3])
    return math.hypot(dx,dy)


def segment_rect_distance(a,b,r) -> float:
    if point_in_rect(a,r) or point_in_rect(b,r):
        return 0.0
    corners=[(r[0],r[1]),(r[2],r[1]),(r[2],r[3]),(r[0],r[3])]
    if any(segments_intersect(a,b,c,d) for c,d in zip(corners,corners[1:]+corners[:1])):
        return 0.0
    return min(
        point_rect_distance(a,r),
        point_rect_distance(b,r),
        *(point_segment_distance(c,a,b) for c in corners),
    )


def item_pos(item: dict) -> tuple[float, float]:
    p = item.get("pos", {})
    return (float(p.get("x", 1e9)), float(p.get("y", 1e9)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--route1bm-drc-json", required=True)
    ap.add_argument("--route1bm-pin-net-audit", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    source_report = load_json(SRC_REPORT)
    source_sha = sha256(SRC_PCB)
    if source_report.get("output_sha256") != source_sha:
        raise SystemExit("route1bn exact probe source report/PCB SHA mismatch")

    drc = load_json(Path(args.route1bm_drc_json))
    audit = load_json(Path(args.route1bm_pin_net_audit))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 111:
        raise SystemExit("route1bn exact probe source DRC gate failed")
    if (
        audit.get("result") != "PASS"
        or audit.get("audited_present_source_nodes") != 268
        or audit.get("mismatches", []) != []
        or audit.get("unexpected_pad_nets", []) != []
    ):
        raise SystemExit("route1bn exact probe source audit gate failed")

    phase = load_json(PHASE_A2)
    selected = phase.get("selected_phase_b_path", {})
    if phase.get("status") != "PHASE_A2_LOCAL_REFINE_COMPLETE":
        raise SystemExit("route1bn exact probe Phase A2 status gate failed")
    if phase.get("base", {}).get("accepted_authority") != "route-1bm":
        raise SystemExit("route1bn exact probe Phase A2 authority gate failed")
    if phase.get("semantic_decision", {}).get("candidate_selected_for_phase_b") is not True:
        raise SystemExit("route1bn exact probe semantic selection gate failed")
    if selected.get("points_mm") != [list(p) for p in POINTS]:
        raise SystemExit("route1bn exact probe selected path changed")
    if selected.get("path_family") != "VHVH" or selected.get("segment_count") != 4:
        raise SystemExit("route1bn exact probe selected scope gate failed")
    if abs(float(selected.get("path_length_mm", -1)) - TOTAL_LENGTH) > 1e-6:
        raise SystemExit("route1bn exact probe selected length gate failed")
    if abs(float(selected.get("minimum_conservative_clearance_mm", -1)) - EXPECTED_CLEARANCE) > 1e-6:
        raise SystemExit("route1bn exact probe selected clearance provenance gate failed")

    matches = []
    for idx, u in enumerate(drc.get("unconnected_items", [])):
        items = u.get("items", [])
        if len(items) != 2:
            continue
        has_source = any(
            x.get("description", "").startswith("Track [+1V8] on Top_layer")
            and near(item_pos(x), SOURCE_ENDPOINT)
            for x in items
        )
        has_target = any(
            x.get("description", "") == "Pad 1 [+1V8] of R403 on Top_layer"
            and near(item_pos(x), R403_PAD1)
            for x in items
        )
        if has_source and has_target:
            matches.append(idx)
    if len(matches) != 1:
        raise SystemExit(f"route1bn exact ratsnest identity gate failed: {matches}")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    r403, c4 = fps.get("R403"), fps.get("C4")
    if r403 is None or r403.GetValue() != "4.7k PU PROV":
        raise SystemExit("route1bn R403 identity gate failed")
    if c4 is None or c4.GetValue() != "100nF":
        raise SystemExit("route1bn C4 identity gate failed")
    p1, p2 = get_pad(r403, "1"), get_pad(r403, "2")
    c4p2 = get_pad(c4, "2")
    if (p1.GetNetname(), xy(p1.GetPosition())) != (TARGET_NET, R403_PAD1):
        raise SystemExit("route1bn R403.1 gate failed")
    if (p2.GetNetname(), xy(p2.GetPosition())) != ("SYS_I2C_SDA", R403_PAD2):
        raise SystemExit("route1bn R403.2 preservation gate failed")
    if (c4p2.GetNetname(), xy(c4p2.GetPosition())) != ("GND", (41.645, 14.975)):
        raise SystemExit("route1bn C4.2 limiting-pad identity gate failed")

    source_tracks = []
    pads, tracks, vias = [], [], []
    candidate_existing = []
    r403_touch = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.IsOnLayer(pcbnew.F_Cu):
                pads.append({"reference":fp.GetReference(),"pad":str(p.GetNumber()),"net":p.GetNetname(),"bbox":bbox(p)})
    for item in board.GetTracks():
        net = item.GetNetname() if hasattr(item, "GetNetname") else ""
        if isinstance(item, pcbnew.PCB_VIA):
            r = bbox(item)
            vias.append({"net":net,"pos":xy(item.GetPosition()),"radius":max(r[2]-r[0],r[3]-r[1])/2.0})
            continue
        if item.GetLayer() != pcbnew.F_Cu:
            continue
        a, b = xy(item.GetStart()), xy(item.GetEnd())
        w = mm(item.GetWidth())
        tracks.append({"net":net,"start":a,"end":b,"width":w})
        if net == TARGET_NET and (near(a,SOURCE_ENDPOINT) or near(b,SOURCE_ENDPOINT)) and abs(mm(item.GetLength())-SOURCE_TRACK_LENGTH_MM) <= 0.002:
            source_tracks.append({"start_mm":list(a),"end_mm":list(b),"length_mm":round(mm(item.GetLength()),6),"width_mm":round(w,6)})
        if net == TARGET_NET and (near(a,R403_PAD1) or near(b,R403_PAD1)):
            r403_touch.append((a,b))
        if net == TARGET_NET and abs(w-WIDTH) < 1e-6:
            for p,q in zip(POINTS,POINTS[1:]):
                if (near(a,p) and near(b,q)) or (near(a,q) and near(b,p)):
                    candidate_existing.append((p,q))
    if len(source_tracks) != 1:
        raise SystemExit(f"route1bn exact source-track gate failed: {source_tracks}")
    if r403_touch or candidate_existing:
        raise SystemExit(f"route1bn candidate copper already exists: r403={r403_touch}, candidate={candidate_existing}")

    segs = list(zip(POINTS, POINTS[1:]))
    actual_lengths = [round(math.dist(a,b),6) for a,b in segs]
    if actual_lengths != SEGMENT_LENGTHS or abs(sum(actual_lengths)-TOTAL_LENGTH) > 1e-6:
        raise SystemExit(f"route1bn segment geometry gate failed: {actual_lengths}")

    half = WIDTH/2.0
    best = float("inf")
    nearest = None

    def consider(clearance, item):
        nonlocal best, nearest
        if clearance < best:
            best, nearest = clearance, item

    for p in pads:
        if p["net"] == TARGET_NET:
            continue
        clearance = min(segment_rect_distance(a,b,p["bbox"])-half for a,b in segs)
        consider(clearance, {"kind":"pad","reference":p["reference"],"pad":p["pad"],"net":p["net"]})
    for t in tracks:
        if t["net"] == TARGET_NET:
            continue
        clearance = min(
            segment_segment_distance(a,b,t["start"],t["end"])-half-t["width"]/2.0
            for a,b in segs
        )
        consider(clearance, {"kind":"track","net":t["net"],"start_mm":list(t["start"]),"end_mm":list(t["end"]),"width_mm":round(t["width"],6)})
    for v in vias:
        if v["net"] == TARGET_NET:
            continue
        clearance = min(point_segment_distance(v["pos"],a,b)-v["radius"]-half for a,b in segs)
        consider(clearance, {"kind":"via","net":v["net"],"position_mm":list(v["pos"])})

    clearance = round(best,6)
    if clearance < RULE or abs(clearance-EXPECTED_CLEARANCE) > 1e-6:
        raise SystemExit(f"route1bn exact clearance gate failed: {clearance}")

    expected_limiters = [
        {"kind":"pad","reference":"R403","pad":"2","net":"SYS_I2C_SDA"},
        {"kind":"pad","reference":"C4","pad":"2","net":"GND"},
    ]
    if nearest not in expected_limiters:
        raise SystemExit(f"route1bn nearest-copper identity changed: {nearest}")

    def pad_path_clearance(pad) -> float:
        r = bbox(pad)
        return round(min(segment_rect_distance(a,b,r)-half for a,b in segs), 6)

    co_limiting_clearances = {
        "R403.2/SYS_I2C_SDA": pad_path_clearance(p2),
        "C4.2/GND": pad_path_clearance(c4p2),
    }
    if co_limiting_clearances != {
        "R403.2/SYS_I2C_SDA": EXPECTED_CLEARANCE,
        "C4.2/GND": EXPECTED_CLEARANCE,
    }:
        raise SystemExit(f"route1bn co-limiting clearance gate failed: {co_limiting_clearances}")

    out = {
        "revision":"r13-route1bn-r403-1v8-exact-probe",
        "issue":20,
        "source_route1bm_sha256":source_sha,
        "source_gate":{"rule_violations":0,"unconnected_items":111,"pin_net_audit":"PASS","audited_nodes":268,"mismatches":[],"unexpected_pad_nets":[]},
        "board_modified":False,
        "actual_drc_index":matches[0],
        "source_track":source_tracks[0],
        "pads":{
            "R403.1":{"net":p1.GetNetname(),"position_mm":list(xy(p1.GetPosition()))},
            "R403.2":{"net":p2.GetNetname(),"position_mm":list(xy(p2.GetPosition()))}
        },
        "r403_touching_1v8_track_count":len(r403_touch),
        "candidate_existing_segment_count":len(candidate_existing),
        "path":{
            "points_mm":[list(p) for p in POINTS],
            "path_family":"VHVH",
            "segment_count":4,
            "segment_lengths_mm":actual_lengths,
            "total_length_mm":TOTAL_LENGTH,
            "track_width_mm":WIDTH,
            "minimum_conservative_clearance_mm":clearance,
            "required_clearance_mm":RULE,
            "nearest_unrelated_copper":nearest,
            "co_limiting_clearances_mm":co_limiting_clearances
        },
        "vias_planned":0,
        "component_moves_planned":0,
        "component_rotations_planned":0,
        "design_rule_waiver":False,
        "release_status":"NOT_FOR_GERBER"
    }
    Path(args.output).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))


if __name__ == "__main__":
    main()
