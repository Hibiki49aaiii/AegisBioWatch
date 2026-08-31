#!/usr/bin/env python3
"""Read-only exact Phase B probe for Issue #19 route-1bm R305.2 -> U4.10 VSYS_HAPTIC."""
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
PHASE_A3 = ROOT / "docs/pcb-route-r13-1bm-refine-phase-a3.json"

TARGET_NET = "VSYS_HAPTIC"
WIDTH = 0.30
RULE = 0.10
EXPECTED_CLEARANCE = 0.20
POINTS = [
    (31.315, 18.595),
    (31.315, 17.500),
    (25.000, 17.500),
    (25.000, 13.400),
    (23.005, 13.400),
]
SEGMENT_LENGTHS = [1.095, 6.315, 4.100, 1.995]
TOTAL_LENGTH = 13.505
R305_PAD1 = (30.295, 18.595)
R305_PAD2 = POINTS[0]
U4_PAD10 = POINTS[-1]
U4_PAD9_NET = "HAPTIC_OUT_N"
BYPASS_POINTS = [
    (6.805, 22.335),
    (6.805, 21.650),
    (16.005, 21.650),
    (16.005, 23.725),
]
EPS = 1e-9


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mm(v: int) -> float:
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


def orient(a, b, c) -> float:
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def on_segment(a, b, p) -> bool:
    return (
        min(a[0], b[0])-EPS <= p[0] <= max(a[0], b[0])+EPS
        and min(a[1], b[1])-EPS <= p[1] <= max(a[1], b[1])+EPS
        and abs(orient(a, b, p)) <= EPS
    )


def segments_intersect(a, b, c, d) -> bool:
    o1,o2,o3,o4 = orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
    if ((o1 > EPS and o2 < -EPS) or (o1 < -EPS and o2 > EPS)) and (
        (o3 > EPS and o4 < -EPS) or (o3 < -EPS and o4 > EPS)
    ):
        return True
    return on_segment(a,b,c) or on_segment(a,b,d) or on_segment(c,d,a) or on_segment(c,d,b)


def point_segment_distance(p, a, b) -> float:
    vx,vy = b[0]-a[0], b[1]-a[1]
    wx,wy = p[0]-a[0], p[1]-a[1]
    vv = vx*vx + vy*vy
    if vv <= EPS:
        return math.dist(p,a)
    t = max(0.0, min(1.0, (wx*vx+wy*vy)/vv))
    q = (a[0]+t*vx, a[1]+t*vy)
    return math.dist(p,q)


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
    dx = max(r[0]-p[0],0.0,p[0]-r[2])
    dy = max(r[1]-p[1],0.0,p[1]-r[3])
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


def near(a, b, tol: float = 0.002) -> bool:
    return math.dist(a,b) <= tol


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--route1bl-drc-json", required=True)
    ap.add_argument("--route1bl-pin-net-audit", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    source_report = load_json(SRC_REPORT)
    source_sha = sha256(SRC_PCB)
    if source_report.get("output_sha256") != source_sha:
        raise SystemExit("route1bm exact probe source report/PCB SHA mismatch")

    drc = load_json(Path(args.route1bl_drc_json))
    audit = load_json(Path(args.route1bl_pin_net_audit))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 112:
        raise SystemExit("route1bm exact probe source DRC gate failed")
    if (
        audit.get("result") != "PASS"
        or audit.get("audited_present_source_nodes") != 268
        or audit.get("mismatches", []) != []
        or audit.get("unexpected_pad_nets", []) != []
    ):
        raise SystemExit("route1bm exact probe source audit gate failed")

    phase_a3 = load_json(PHASE_A3)
    selected = phase_a3.get("refine", {}).get("selected_phase_b_path", {})
    if phase_a3.get("status") != "PHASE_A3_LOCAL_REFINE_COMPLETE":
        raise SystemExit("route1bm exact probe Phase A3 status gate failed")
    if phase_a3.get("base", {}).get("accepted_authority") != "route-1bl":
        raise SystemExit("route1bm exact probe Phase A3 authority gate failed")
    if selected.get("points_mm") != [list(p) for p in POINTS]:
        raise SystemExit(f"route1bm exact probe selected path changed: {selected.get('points_mm')}")
    if selected.get("path_family") != "VHVH" or selected.get("segment_count") != 4:
        raise SystemExit("route1bm exact probe selected family/scope gate failed")
    if abs(float(selected.get("path_length_mm", -1)) - TOTAL_LENGTH) > 1e-6:
        raise SystemExit("route1bm exact probe selected path length gate failed")
    if abs(float(selected.get("minimum_conservative_clearance_mm", -1)) - EXPECTED_CLEARANCE) > 1e-6:
        raise SystemExit("route1bm exact probe selected clearance provenance gate failed")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    r305,u4,c305,c304 = fps.get("R305"),fps.get("U4"),fps.get("C305"),fps.get("C304")
    if None in (r305,u4,c305,c304):
        raise SystemExit("route1bm exact probe missing haptic supply components")
    if r305.GetValue() != "0R / FB OPTION" or u4.GetValue() != "DRV2605LDGSR":
        raise SystemExit("route1bm exact probe R305/U4 identity gate failed")
    if c305.GetValue() != "1uF" or c304.GetValue() != "100nF":
        raise SystemExit("route1bm exact probe C305/C304 identity gate failed")

    r305p1,r305p2 = get_pad(r305,"1"),get_pad(r305,"2")
    u4p9,u4p10 = get_pad(u4,"9"),get_pad(u4,"10")
    c305p1,c304p1 = get_pad(c305,"1"),get_pad(c304,"1")
    observed = {
        "R305.1": {"net": r305p1.GetNetname(), "position_mm": list(xy(r305p1.GetPosition()))},
        "R305.2": {"net": r305p2.GetNetname(), "position_mm": list(xy(r305p2.GetPosition()))},
        "U4.9": {"net": u4p9.GetNetname(), "position_mm": list(xy(u4p9.GetPosition()))},
        "U4.10": {"net": u4p10.GetNetname(), "position_mm": list(xy(u4p10.GetPosition()))},
        "C305.1": {"net": c305p1.GetNetname(), "position_mm": list(xy(c305p1.GetPosition()))},
        "C304.1": {"net": c304p1.GetNetname(), "position_mm": list(xy(c304p1.GetPosition()))},
    }
    if observed["R305.1"] != {"net":"VSYS","position_mm":list(R305_PAD1)}:
        raise SystemExit(f"route1bm exact probe R305.1 preservation gate failed: {observed['R305.1']}")
    if observed["R305.2"] != {"net":TARGET_NET,"position_mm":list(R305_PAD2)}:
        raise SystemExit("route1bm exact probe R305.2 gate failed")
    if observed["U4.10"] != {"net":TARGET_NET,"position_mm":list(U4_PAD10)}:
        raise SystemExit("route1bm exact probe U4.10 gate failed")
    if observed["U4.9"]["net"] != U4_PAD9_NET:
        raise SystemExit("route1bm exact probe U4.9 net gate failed")
    if observed["C305.1"] != {"net":TARGET_NET,"position_mm":list(BYPASS_POINTS[0])}:
        raise SystemExit("route1bm exact probe C305.1 gate failed")
    if observed["C304.1"] != {"net":TARGET_NET,"position_mm":list(BYPASS_POINTS[-1])}:
        raise SystemExit("route1bm exact probe C304.1 gate failed")

    pads=[]
    tracks=[]
    vias=[]
    bypass_hits=[]
    r305_touch=[]
    u4_touch=[]
    candidate_existing=[]
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
        net = item.GetNetname() if hasattr(item,"GetNetname") else ""
        if isinstance(item,pcbnew.PCB_VIA):
            r=bbox(item)
            vias.append({"net":net,"pos":xy(item.GetPosition()),"radius":max(r[2]-r[0],r[3]-r[1])/2.0})
            continue
        if item.GetLayer()!=pcbnew.F_Cu:
            continue
        a,b=xy(item.GetStart()),xy(item.GetEnd())
        w=mm(item.GetWidth())
        tracks.append({"net":net,"start":a,"end":b,"width":w})
        if net==TARGET_NET and abs(w-WIDTH)<1e-6:
            for p,q in zip(BYPASS_POINTS,BYPASS_POINTS[1:]):
                if (near(a,p) and near(b,q)) or (near(a,q) and near(b,p)):
                    bypass_hits.append((p,q))
            if near(a,R305_PAD2) or near(b,R305_PAD2):
                r305_touch.append((a,b))
            if near(a,U4_PAD10) or near(b,U4_PAD10):
                u4_touch.append((a,b))
            for p,q in zip(POINTS,POINTS[1:]):
                if (near(a,p) and near(b,q)) or (near(a,q) and near(b,p)):
                    candidate_existing.append((p,q))

    if len(bypass_hits) != 3:
        raise SystemExit(f"route1bm exact probe accepted bypass geometry gate failed: {bypass_hits}")
    if r305_touch or u4_touch or candidate_existing:
        raise SystemExit(
            f"route1bm exact probe target already routed: r305={r305_touch}, u4={u4_touch}, candidate={candidate_existing}"
        )

    segs=list(zip(POINTS,POINTS[1:]))
    half=WIDTH/2.0
    best=float("inf")
    nearest=None

    def consider(clearance,item):
        nonlocal best,nearest
        if clearance < best:
            best=clearance
            nearest=item

    for p in pads:
        if p["net"]==TARGET_NET:
            continue
        clearance=min(segment_rect_distance(a,b,p["bbox"])-half for a,b in segs)
        consider(clearance,{"kind":"pad","reference":p["reference"],"pad":p["pad"],"net":p["net"]})
    for t in tracks:
        if t["net"]==TARGET_NET:
            continue
        clearance=min(
            segment_segment_distance(a,b,t["start"],t["end"])-half-t["width"]/2.0
            for a,b in segs
        )
        consider(clearance,{
            "kind":"track","net":t["net"],"start_mm":list(t["start"]),
            "end_mm":list(t["end"]),"width_mm":round(t["width"],6)
        })
    for v in vias:
        if v["net"]==TARGET_NET:
            continue
        clearance=min(point_segment_distance(v["pos"],a,b)-v["radius"]-half for a,b in segs)
        consider(clearance,{"kind":"via","net":v["net"],"position_mm":list(v["pos"])})

    clearance=round(best,6)
    if clearance < RULE or abs(clearance-EXPECTED_CLEARANCE) > 1e-6:
        raise SystemExit(f"route1bm exact probe clearance gate failed: {clearance}")
    if nearest != {"kind":"pad","reference":"U4","pad":"9","net":U4_PAD9_NET}:
        raise SystemExit(f"route1bm exact probe nearest-copper identity changed: {nearest}")

    actual_lengths=[round(math.dist(a,b),6) for a,b in segs]
    if actual_lengths != SEGMENT_LENGTHS:
        raise SystemExit(f"route1bm exact probe segment lengths changed: {actual_lengths}")
    if abs(sum(actual_lengths)-TOTAL_LENGTH) > 1e-6:
        raise SystemExit("route1bm exact probe total length gate failed")

    out = {
        "revision":"r13-route1bm-r305-u4-vsys-haptic-exact-probe",
        "issue":19,
        "source_route1bl_sha256":source_sha,
        "source_gate":{
            "rule_violations":0,
            "unconnected_items":112,
            "pin_net_audit":"PASS",
            "audited_nodes":268,
            "mismatches":[],
            "unexpected_pad_nets":[],
        },
        "board_modified":False,
        "pads":observed,
        "accepted_route1bk_bypass_segment_count":len(bypass_hits),
        "r305_touching_vsys_haptic_track_count":len(r305_touch),
        "u4_touching_vsys_haptic_track_count":len(u4_touch),
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
        },
        "vias_planned":0,
        "component_moves_planned":0,
        "component_rotations_planned":0,
        "design_rule_waiver":False,
        "release_status":"NOT_FOR_GERBER",
    }
    Path(args.output).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))


if __name__ == "__main__":
    main()
