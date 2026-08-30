#!/usr/bin/env python3
"""Read-only exact Phase B probe for route-1bl VSYS source endpoint -> R106.1."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bk"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bk-r13.kicad_pcb"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bk.json"

WIDTH = 0.30
RULE = 0.10
SCREEN_POINTS = [(8.9875, 28.25), (7.2, 28.25), (7.2, 26.4), (5.270826, 26.4), (5.270826, 25.865834)]
POINTS = [(7.35, 28.25), (7.2, 28.25), (7.2, 26.4), (5.270826, 26.4), (5.270826, 25.865834)]
SEGMENT_LENGTHS = [0.15, 1.85, 1.929174, 0.534166]
TOTAL_LENGTH = 4.46334
EXPECTED_CLEARANCE = 0.184166
EPS = 1e-9

TARGET_NET = "VSYS"
TARGET_A_DESC = "Track [VSYS] on Top_layer, length 1.6375 mm"
TARGET_B_DESC = "Track [VSYS] on Top_layer, length 0.6208 mm"
EXPECTED_A = (8.9875, 28.25)
EXPECTED_B = (5.270826, 25.865834)
EXPECTED_SOURCE_TRACK_START = (8.9875, 28.25)
EXPECTED_SOURCE_TRACK_END = (7.35, 28.25)
EXPECTED_SOURCE_TRACK_WIDTH = 0.30
EXPECTED_R106_PAD2 = (5.910826, 25.865834)


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
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def on_segment(a, b, p) -> bool:
    return (
        min(a[0], b[0])-EPS <= p[0] <= max(a[0], b[0])+EPS
        and min(a[1], b[1])-EPS <= p[1] <= max(a[1], b[1])+EPS
        and abs(orient(a, b, p)) <= EPS
    )


def segments_intersect(a,b,c,d) -> bool:
    o1,o2,o3,o4=orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
    if ((o1 > EPS and o2 < -EPS) or (o1 < -EPS and o2 > EPS)) and (
        (o3 > EPS and o4 < -EPS) or (o3 < -EPS and o4 > EPS)
    ):
        return True
    return on_segment(a,b,c) or on_segment(a,b,d) or on_segment(c,d,a) or on_segment(c,d,b)


def point_segment_distance(p,a,b) -> float:
    vx,vy=b[0]-a[0],b[1]-a[1]
    wx,wy=p[0]-a[0],p[1]-a[1]
    vv=vx*vx+vy*vy
    if vv <= EPS:
        return math.dist(p,a)
    t=max(0.0,min(1.0,(wx*vx+wy*vy)/vv))
    q=(a[0]+t*vx,a[1]+t*vy)
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
    dx=max(r[0]-p[0],0.0,p[0]-r[2])
    dy=max(r[1]-p[1],0.0,p[1]-r[3])
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


def frange(start: float, stop: float, step: float) -> list[float]:
    first=math.floor(start/step)*step
    last=math.ceil(stop/step)*step
    count=int(round((last-first)/step))
    return [round(first+i*step,6) for i in range(count+1)]


def normalize(points):
    out=[]
    for p in points:
        q=(round(float(p[0]),6),round(float(p[1]),6))
        if not out or math.dist(out[-1],q)>EPS:
            out.append(q)
    return out


def path_length(points) -> float:
    return sum(math.dist(a,b) for a,b in zip(points,points[1:]))


def get_pad(fp, number: str):
    pads=[p for p in fp.Pads() if str(p.GetNumber())==str(number)]
    if len(pads)!=1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality failed: {len(pads)}")
    return pads[0]


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--route1bk-drc-json",required=True)
    ap.add_argument("--route1bk-pin-net-audit",required=True)
    ap.add_argument("--refine-json",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    report=load_json(SRC_REPORT)
    src_sha=sha256(SRC_PCB)
    if report.get("output_sha256") != src_sha:
        raise SystemExit("route1bl exact probe source SHA gate failed")

    drc=load_json(Path(args.route1bk_drc_json))
    audit=load_json(Path(args.route1bk_pin_net_audit))
    if len(drc.get("violations",[])) != 0 or len(drc.get("unconnected_items",[])) != 113:
        raise SystemExit("route1bl R106 DRC source gate failed")
    if audit.get("result")!="PASS" or audit.get("audited_present_source_nodes")!=268:
        raise SystemExit("route1bl R106 audit source gate failed")

    refine=load_json(Path(args.refine_json))
    if refine.get("revision")!="r13-route1bl-r106-vsys-local-refine":
        raise SystemExit("route1bl exact probe refine revision gate failed")
    if refine.get("source_gate")!={"rule_violations":0,"unconnected_items":113,"pin_net_audit":"PASS","audited_nodes":268}:
        raise SystemExit("route1bl exact probe refine source gate failed")
    if refine.get("board_modified") is not False:
        raise SystemExit("route1bl exact probe refine modified-board gate failed")
    best=refine.get("best_passing_path") or {}
    if best.get("points_mm") != [list(p) for p in SCREEN_POINTS]:
        raise SystemExit(f"route1bl exact probe refined screen path changed: {best.get('points_mm')}")
    if best.get("path_family")!="HVHV" or best.get("segment_count")!=4:
        raise SystemExit("route1bl exact probe refine family/scope gate failed")
    if abs(float(best.get("minimum_conservative_clearance_mm",-1))-EXPECTED_CLEARANCE)>1e-6:
        raise SystemExit("route1bl exact probe refine clearance gate failed")

    # KiCad may choose different representative coordinates/descriptions for the
    # same unconnected VSYS islands after deterministic reproduction. Do not use
    # those representatives as electrical authority. Gate the global DRC state
    # here, then gate the exact source track and R106 pads directly from PCB data.
    vsys_unconnected_count=0
    for u in drc["unconnected_items"]:
        items=u.get("items",[])
        if len(items)==2 and all("[VSYS]" in x.get("description","") for x in items):
            vsys_unconnected_count += 1
    if vsys_unconnected_count < 1:
        raise SystemExit("route1bl R106 expected at least one VSYS unconnected item")

    drc_index=None
    A=EXPECTED_A
    B=EXPECTED_B

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={fp.GetReference():fp for fp in board.GetFootprints()}
    if "R106" not in fps or fps["R106"].GetValue()!="0R DNP/OPTION":
        raise SystemExit("route1bl R106 identity gate failed")

    p1=get_pad(fps["R106"],"1")
    p2=get_pad(fps["R106"],"2")
    if p1.GetNetname()!=TARGET_NET or xy(p1.GetPosition())!=EXPECTED_B:
        raise SystemExit("route1bl R106.1 gate failed")
    if p2.GetNetname()!="LDO2_IN" or xy(p2.GetPosition())!=EXPECTED_R106_PAD2:
        raise SystemExit("route1bl R106.2/LDO2_IN preservation gate failed")

    exact_source_tracks=[]
    pads=[]
    tracks=[]
    vias=[]
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.IsOnLayer(pcbnew.F_Cu):
                pads.append({
                    "reference":fp.GetReference(),
                    "pad":str(p.GetNumber()),
                    "net":p.GetNetname(),
                    "bbox":bbox(p),
                })
    for item in board.GetTracks():
        net=item.GetNetname() if hasattr(item,"GetNetname") else ""
        if isinstance(item,pcbnew.PCB_VIA):
            r=bbox(item)
            vias.append({
                "net":net,
                "pos":xy(item.GetPosition()),
                "radius":max(r[2]-r[0],r[3]-r[1])/2.0,
            })
        elif item.GetLayer()==pcbnew.F_Cu:
            start,end=xy(item.GetStart()),xy(item.GetEnd())
            width=mm(item.GetWidth())
            tracks.append({"net":net,"start":start,"end":end,"width":width})
            if (
                net==TARGET_NET
                and {start,end}=={EXPECTED_SOURCE_TRACK_START,EXPECTED_SOURCE_TRACK_END}
                and abs(width-EXPECTED_SOURCE_TRACK_WIDTH)<1e-9
            ):
                exact_source_tracks.append(item)
    if len(exact_source_tracks)!=1:
        raise SystemExit(f"route1bl R106 source track cardinality failed: {len(exact_source_tracks)}")

    def evaluate(points):
        segs=list(zip(points,points[1:]))
        best=float("inf")
        nearest=None
        half=WIDTH/2.0

        def consider(clearance,item):
            nonlocal best,nearest
            if clearance<best:
                best=clearance
                nearest=item

        for p in pads:
            if p["net"]==TARGET_NET:
                continue
            clearance=min(segment_rect_distance(a,b,p["bbox"])-half for a,b in segs)
            consider(clearance,{
                "kind":"pad",
                "reference":p["reference"],
                "pad":p["pad"],
                "net":p["net"],
            })
        for t in tracks:
            if t["net"]==TARGET_NET:
                continue
            clearance=min(
                segment_segment_distance(a,b,t["start"],t["end"])-half-t["width"]/2.0
                for a,b in segs
            )
            consider(clearance,{
                "kind":"track",
                "net":t["net"],
                "start_mm":list(t["start"]),
                "end_mm":list(t["end"]),
                "width_mm":round(t["width"],6),
            })
        for v in vias:
            if v["net"]==TARGET_NET:
                continue
            clearance=min(point_segment_distance(v["pos"],a,b)-v["radius"]-half for a,b in segs)
            consider(clearance,{
                "kind":"via",
                "net":v["net"],
                "position_mm":list(v["pos"]),
            })
        return round(best,6),nearest

    points=normalize(POINTS)
    if points != POINTS:
        raise SystemExit("route1bl exact probe point normalization changed")
    clearance,nearest=evaluate(points)
    if clearance + 1e-9 < EXPECTED_CLEARANCE or clearance < RULE:
        raise SystemExit(f"route1bl exact probe effective-path clearance failed: {clearance}")

    p2_box=bbox(p2)
    independent_r106p2_gap=round(p2_box[0] - (B[0] + WIDTH/2.0),6)
    if abs(independent_r106p2_gap-clearance)>1e-6:
        raise SystemExit(
            f"route1bl exact probe independent R106.2 gap mismatch: {independent_r106p2_gap} vs {clearance}"
        )

    actual_lengths=[round(math.dist(a,b),6) for a,b in zip(points,points[1:])]
    if actual_lengths != SEGMENT_LENGTHS:
        raise SystemExit(f"route1bl exact probe segment lengths changed: {actual_lengths}")
    actual_total=round(sum(actual_lengths),6)
    if abs(actual_total-TOTAL_LENGTH)>1e-6:
        raise SystemExit(f"route1bl exact probe total length changed: {actual_total}")

    out={
        "revision":"r13-route1bl-r106-vsys-exact-probe",
        "source_route1bk_sha256":src_sha,
        "source_gate":{
            "rule_violations":0,
            "unconnected_items":113,
            "pin_net_audit":"PASS",
            "audited_nodes":268,
        },
        "board_modified":False,
        "R106_value":fps["R106"].GetValue(),
        "R106_pad1_mm":list(B),
        "R106_pad1_net":p1.GetNetname(),
        "R106_pad2_mm":list(EXPECTED_R106_PAD2),
        "R106_pad2_net":p2.GetNetname(),
        "R106_pad2_bbox_mm":[round(v,6) for v in p2_box],
        "source_point_mm":list(A),
        "source_track":{
            "start_mm":list(EXPECTED_SOURCE_TRACK_START),
            "end_mm":list(EXPECTED_SOURCE_TRACK_END),
            "width_mm":EXPECTED_SOURCE_TRACK_WIDTH,
            "net":TARGET_NET,
        },
        "screen_path_points_mm":[list(p) for p in SCREEN_POINTS],
        "effective_new_copper_path":{
            "points_mm":[list(p) for p in points],
            "segment_count":4,
            "segment_lengths_mm":actual_lengths,
            "total_length_mm":actual_total,
            "track_width_mm":WIDTH,
            "minimum_conservative_clearance_mm":clearance,
            "required_clearance_mm":RULE,
            "nearest_unrelated_copper":nearest,
            "independent_r106p2_gap_mm":independent_r106p2_gap,
        },
        "accepted_source_track_overlap_materialized":False,
        "release_status":"NOT_FOR_GERBER",
    }
    Path(args.output).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))


if __name__=="__main__":
    main()
