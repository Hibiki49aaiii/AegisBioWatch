#!/usr/bin/env python3
"""Read-only exact Phase B probe for Issue #21 route-1bo +1V8 source track -> J8.1."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / "hardware/main-board/pcb/route-r13-1bn/AegisBioWatch-MainBoard-Route1bn-r13.kicad_pcb"
SRC_REPORT = ROOT / "hardware/main-board/pcb/route-r13-1bn/routing-seed-r13-1bn.json"
PHASE_A2 = ROOT / "docs/pcb-route-r13-1bo-j8-refine-phase-a2.json"

TARGET_NET = "+1V8"
WIDTH = 0.30
RULE = 0.10
EXPECTED_CLEARANCE = 0.4897
SOURCE_ENDPOINT = (10.305, 4.72)
SOURCE_TRACK_LENGTH_MM = 6.3650
J8_PAD1 = (12.105, 15.26)
POINTS = [
    SOURCE_ENDPOINT,
    (9.7, 4.72),
    (9.7, 15.8),
    (12.105, 15.8),
    J8_PAD1,
]
SEGMENT_LENGTHS = [0.605, 11.08, 2.405, 0.54]
TOTAL_LENGTH = 14.63
EXPECTED_BLANKS = {
    (10.835, 14.625),
    (15.915, 13.609),
    (15.915, 15.641),
}
EPS = 1e-9


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mm(v) -> float:
    return float(pcbnew.ToMM(v))


def xy(v) -> tuple[float, float]:
    return (round(mm(v.x), 6), round(mm(v.y), 6))


def near(a, b, tol: float = 0.002) -> bool:
    return math.dist(a, b) <= tol


def bbox(item) -> tuple[float, float, float, float]:
    b = item.GetBoundingBox()
    return (mm(b.GetX()), mm(b.GetY()), mm(b.GetRight()), mm(b.GetBottom()))


def get_pad(fp, number: str):
    pads = [p for p in fp.Pads() if str(p.GetNumber()) == str(number)]
    if len(pads) != 1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(pads)}")
    return pads[0]


def item_pos(item: dict) -> tuple[float, float]:
    p = item.get("pos", {})
    return (float(p.get("x", 1e9)), float(p.get("y", 1e9)))


def orient(a, b, c) -> float:
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def on_segment(a, b, p) -> bool:
    return (
        min(a[0], b[0])-EPS <= p[0] <= max(a[0], b[0])+EPS
        and min(a[1], b[1])-EPS <= p[1] <= max(a[1], b[1])+EPS
        and abs(orient(a,b,p)) <= EPS
    )


def segments_intersect(a,b,c,d) -> bool:
    o1,o2,o3,o4 = orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
    if ((o1>EPS and o2<-EPS) or (o1<-EPS and o2>EPS)) and ((o3>EPS and o4<-EPS) or (o3<-EPS and o4>EPS)):
        return True
    return on_segment(a,b,c) or on_segment(a,b,d) or on_segment(c,d,a) or on_segment(c,d,b)


def point_segment_distance(p,a,b) -> float:
    vx,vy=b[0]-a[0],b[1]-a[1]
    wx,wy=p[0]-a[0],p[1]-a[1]
    vv=vx*vx+vy*vy
    if vv<=EPS:
        return math.dist(p,a)
    t=max(0.0,min(1.0,(wx*vx+wy*vy)/vv))
    q=(a[0]+t*vx,a[1]+t*vy)
    return math.dist(p,q)


def segment_segment_distance(a,b,c,d) -> float:
    if segments_intersect(a,b,c,d):
        return 0.0
    return min(point_segment_distance(a,c,d),point_segment_distance(b,c,d),point_segment_distance(c,a,b),point_segment_distance(d,a,b))


def point_in_rect(p,r) -> bool:
    return r[0]-EPS<=p[0]<=r[2]+EPS and r[1]-EPS<=p[1]<=r[3]+EPS


def point_rect_distance(p,r) -> float:
    dx=max(r[0]-p[0],0.0,p[0]-r[2])
    dy=max(r[1]-p[1],0.0,p[1]-r[3])
    return math.hypot(dx,dy)


def segment_rect_distance(a,b,r) -> float:
    if point_in_rect(a,r) or point_in_rect(b,r):
        return 0.0
    corners=[(r[0],r[1]),(r[2],r[1]),(r[2],r[3]),(r[0],r[3])]
    if any(segments_intersect(a,b,c,d) for c,d in zip(corners,corners[1:]+corners[:1])):
        return 0.0
    return min(point_rect_distance(a,r),point_rect_distance(b,r),*(point_segment_distance(c,a,b) for c in corners))


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--route1bn-drc-json",required=True)
    ap.add_argument("--route1bn-pin-net-audit",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    report=load_json(SRC_REPORT)
    source_sha=sha256(SRC_PCB)
    if report.get("output_sha256")!=source_sha:
        raise SystemExit("route1bo exact probe source report/PCB SHA mismatch")

    drc=load_json(Path(args.route1bn_drc_json))
    audit=load_json(Path(args.route1bn_pin_net_audit))
    if len(drc.get("violations",[]))!=0 or len(drc.get("unconnected_items",[]))!=110:
        raise SystemExit("route1bo exact probe source DRC gate failed")
    if audit.get("result")!="PASS" or audit.get("audited_present_source_nodes")!=268 or audit.get("mismatches",[])!=[] or audit.get("unexpected_pad_nets",[])!=[]:
        raise SystemExit("route1bo exact probe source audit gate failed")

    phase=load_json(PHASE_A2)
    selected=phase.get("selected_phase_b_path",{})
    if phase.get("status")!="PHASE_A2_LOCAL_REFINE_COMPLETE" or phase.get("base",{}).get("accepted_authority")!="route-1bn":
        raise SystemExit("route1bo exact probe Phase A2 authority/status gate failed")
    if phase.get("semantic_decision",{}).get("candidate_selected_for_phase_b") is not True:
        raise SystemExit("route1bo exact probe semantic selection gate failed")
    if selected.get("points_mm")!=[list(p) for p in POINTS] or selected.get("path_family")!="HVHV" or selected.get("segment_count")!=4:
        raise SystemExit("route1bo exact probe selected path/scope changed")
    if abs(float(selected.get("path_length_mm",-1))-TOTAL_LENGTH)>1e-6 or abs(float(selected.get("minimum_conservative_clearance_mm",-1))-EXPECTED_CLEARANCE)>1e-6:
        raise SystemExit("route1bo exact probe selected geometry provenance changed")

    matches=[]
    for idx,u in enumerate(drc.get("unconnected_items",[])):
        items=u.get("items",[])
        if len(items)!=2:
            continue
        has_source=any(x.get("description","").startswith("Track [+1V8] on Top_layer") and near(item_pos(x),SOURCE_ENDPOINT) for x in items)
        has_target=any(x.get("description","")=="Pad 1 [+1V8] of J8 on Top_layer" and near(item_pos(x),J8_PAD1) for x in items)
        if has_source and has_target:
            matches.append(idx)
    if matches!=[3]:
        raise SystemExit(f"route1bo exact ratsnest identity gate failed: {matches}")

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={fp.GetReference():fp for fp in board.GetFootprints()}
    j8=fps.get("J8")
    if j8 is None or j8.GetValue()!="TC2030_SWD_6":
        raise SystemExit("route1bo J8 identity/value gate failed")
    p1=get_pad(j8,"1")
    if (p1.GetNetname(),xy(p1.GetPosition()))!=(TARGET_NET,J8_PAD1):
        raise SystemExit("route1bo J8.1 identity/net/coordinate gate failed")

    blanks=[]
    for p in j8.Pads():
        if str(p.GetNumber())!="":
            continue
        size=(round(mm(p.GetSize().x),6),round(mm(p.GetSize().y),6))
        drill=(round(mm(p.GetDrillSize().x),6),round(mm(p.GetDrillSize().y),6))
        pos=xy(p.GetPosition())
        is_npth=(p.GetAttribute()==pcbnew.PAD_ATTRIB_NPTH)
        blanks.append({"position_mm":list(pos),"size_mm":list(size),"drill_mm":list(drill),"net":p.GetNetname(),"is_npth":is_npth})
        if not is_npth or p.GetNetname()!="" or size!=(0.9906,0.9906) or drill!=(0.9906,0.9906):
            raise SystemExit(f"route1bo J8 numberless NPTH gate failed: {blanks[-1]}")
    if {tuple(x["position_mm"]) for x in blanks}!=EXPECTED_BLANKS or len(blanks)!=3:
        raise SystemExit(f"route1bo J8 numberless NPTH position/cardinality gate failed: {blanks}")

    source_tracks=[]
    candidate_existing=[]
    j8_touch=[]
    pads=[]
    tracks=[]
    vias=[]
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.IsOnLayer(pcbnew.F_Cu):
                pads.append({"reference":fp.GetReference(),"pad":str(p.GetNumber()),"net":p.GetNetname(),"bbox":bbox(p)})
    for item in board.GetTracks():
        net=item.GetNetname() if hasattr(item,"GetNetname") else ""
        if isinstance(item,pcbnew.PCB_VIA):
            r=bbox(item)
            vias.append({"net":net,"pos":xy(item.GetPosition()),"radius":max(r[2]-r[0],r[3]-r[1])/2.0})
            continue
        if item.GetLayer()!=pcbnew.F_Cu:
            continue
        a,b=xy(item.GetStart()),xy(item.GetEnd())
        w=mm(item.GetWidth())
        tracks.append({"net":net,"start":a,"end":b,"width":w})
        if net==TARGET_NET and (near(a,SOURCE_ENDPOINT) or near(b,SOURCE_ENDPOINT)) and abs(mm(item.GetLength())-SOURCE_TRACK_LENGTH_MM)<=0.002:
            source_tracks.append({"start_mm":list(a),"end_mm":list(b),"length_mm":round(mm(item.GetLength()),6),"width_mm":round(w,6)})
        if net==TARGET_NET and (near(a,J8_PAD1) or near(b,J8_PAD1)):
            j8_touch.append((a,b))
        if net==TARGET_NET and abs(w-WIDTH)<1e-6:
            for p,q in zip(POINTS,POINTS[1:]):
                if (near(a,p) and near(b,q)) or (near(a,q) and near(b,p)):
                    candidate_existing.append((p,q))
    if len(source_tracks)!=1:
        raise SystemExit(f"route1bo exact source-track gate failed: {source_tracks}")
    if j8_touch or candidate_existing:
        raise SystemExit(f"route1bo candidate copper already exists: j8={j8_touch}, candidate={candidate_existing}")

    segs=list(zip(POINTS,POINTS[1:]))
    actual_lengths=[round(math.dist(a,b),6) for a,b in segs]
    if actual_lengths!=SEGMENT_LENGTHS or abs(sum(actual_lengths)-TOTAL_LENGTH)>1e-6:
        raise SystemExit(f"route1bo segment geometry gate failed: {actual_lengths}")

    half=WIDTH/2.0
    best=float("inf")
    nearest=None
    def consider(clearance,item):
        nonlocal best,nearest
        if clearance<best:
            best,nearest=clearance,item

    for p in pads:
        if p["net"]==TARGET_NET:
            continue
        consider(min(segment_rect_distance(a,b,p["bbox"])-half for a,b in segs),{"kind":"pad","reference":p["reference"],"pad":p["pad"],"net":p["net"]})
    for t in tracks:
        if t["net"]==TARGET_NET:
            continue
        consider(min(segment_segment_distance(a,b,t["start"],t["end"])-half-t["width"]/2.0 for a,b in segs),{"kind":"track","net":t["net"],"start_mm":list(t["start"]),"end_mm":list(t["end"]),"width_mm":round(t["width"],6)})
    for v in vias:
        if v["net"]==TARGET_NET:
            continue
        consider(min(point_segment_distance(v["pos"],a,b)-v["radius"]-half for a,b in segs),{"kind":"via","net":v["net"],"position_mm":list(v["pos"])})

    clearance=round(best,6)
    expected_nearest={"kind":"pad","reference":"J8","pad":"","net":""}
    if abs(clearance-EXPECTED_CLEARANCE)>1e-6 or clearance<RULE or nearest!=expected_nearest:
        raise SystemExit(f"route1bo exact clearance/limiter gate failed: clearance={clearance} nearest={nearest}")

    out={
        "revision":"r13-route1bo-j8-1v8-exact-probe",
        "issue":21,
        "source_route1bn_sha256":source_sha,
        "source_gate":{"rule_violations":0,"unconnected_items":110,"pin_net_audit":"PASS","audited_nodes":268,"mismatches":[],"unexpected_pad_nets":[]},
        "board_modified":False,
        "actual_drc_index":matches[0],
        "source_track":source_tracks[0],
        "J8":{"value":j8.GetValue(),"pad1":{"net":p1.GetNetname(),"position_mm":list(xy(p1.GetPosition()))},"numberless_pads":blanks,"numberless_pads_all_npth":all(x["is_npth"] for x in blanks)},
        "candidate_existing_segment_count":len(candidate_existing),
        "j8_touching_1v8_track_count":len(j8_touch),
        "path":{"points_mm":[list(p) for p in POINTS],"path_family":"HVHV","segment_count":4,"segment_lengths_mm":actual_lengths,"total_length_mm":TOTAL_LENGTH,"track_width_mm":WIDTH,"minimum_conservative_clearance_mm":clearance,"required_clearance_mm":RULE,"nearest_unrelated_copper":nearest},
        "vias_planned":0,
        "component_moves_planned":0,
        "component_rotations_planned":0,
        "design_rule_waiver":False,
        "via_in_pad":False,
        "release_status":"NOT_FOR_GERBER"
    }
    Path(args.output).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))


if __name__=="__main__":
    main()
