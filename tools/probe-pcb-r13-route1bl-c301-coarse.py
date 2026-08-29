#!/usr/bin/env python3
"""Read-only max-four-segment coarse screen for route-1bl C301.1 -> accepted +1V8 rail."""
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
GRID = 0.25
MARGIN = 4.0
MAX_PATH_LENGTH = 14.0
EPS = 1e-9

TARGET_NET = "+1V8"
TARGET_A_DESC = "Pad 1 [+1V8] of C301 on Top_layer"
TARGET_B_DESC = "Track [+1V8] on Top_layer, length 4.5000 mm"
EXPECTED_A = (13.755, 23.725)
EXPECTED_B = (15.755, 26.2)
EXPECTED_TARGET_TRACK_START = (15.755, 26.2)
EXPECTED_TARGET_TRACK_END = (20.255, 26.2)
EXPECTED_TARGET_TRACK_WIDTH = 0.30


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
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    report=load_json(SRC_REPORT)
    src_sha=sha256(SRC_PCB)
    if report.get("output_sha256") != src_sha:
        raise SystemExit("route1bl C301 coarse source SHA gate failed")

    drc=load_json(Path(args.route1bk_drc_json))
    audit=load_json(Path(args.route1bk_pin_net_audit))
    if len(drc.get("violations",[])) != 0 or len(drc.get("unconnected_items",[])) != 113:
        raise SystemExit("route1bl C301 coarse DRC source gate failed")
    if audit.get("result")!="PASS" or audit.get("audited_present_source_nodes")!=268:
        raise SystemExit("route1bl C301 coarse audit source gate failed")

    matches=[]
    for idx,u in enumerate(drc["unconnected_items"]):
        items=u.get("items",[])
        if len(items)!=2:
            continue
        descs=[x["description"] for x in items]
        if set(descs)=={TARGET_A_DESC,TARGET_B_DESC}:
            bydesc={x["description"]:x for x in items}
            matches.append((idx,bydesc[TARGET_A_DESC],bydesc[TARGET_B_DESC]))
    if len(matches)!=1:
        raise SystemExit(f"route1bl C301 DRC target cardinality failed: {len(matches)}")
    drc_index,ai,bi=matches[0]
    A=(float(ai["pos"]["x"]),float(ai["pos"]["y"]))
    B=(float(bi["pos"]["x"]),float(bi["pos"]["y"]))
    if A!=EXPECTED_A or B!=EXPECTED_B:
        raise SystemExit(f"route1bl C301 DRC coordinate gate failed: {A} -> {B}")

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={fp.GetReference():fp for fp in board.GetFootprints()}
    for ref,val in {"C301":"100nF","R404":"4.7k PU PROV","R302":"47k PU"}.items():
        if ref not in fps or fps[ref].GetValue()!=val:
            raise SystemExit(f"route1bl C301 identity gate failed: {ref}")

    c301p1=get_pad(fps["C301"],"1")
    c301p2=get_pad(fps["C301"],"2")
    if c301p1.GetNetname()!=TARGET_NET or xy(c301p1.GetPosition())!=EXPECTED_A:
        raise SystemExit("route1bl C301.1 gate failed")
    if c301p2.GetNetname()!="GND" or xy(c301p2.GetPosition())!=(14.395,23.725):
        raise SystemExit("route1bl C301.2 gate failed")

    exact_target_tracks=[]
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
                and {start,end}=={EXPECTED_TARGET_TRACK_START,EXPECTED_TARGET_TRACK_END}
                and abs(width-EXPECTED_TARGET_TRACK_WIDTH)<1e-9
            ):
                exact_target_tracks.append(item)
    if len(exact_target_tracks)!=1:
        raise SystemExit(f"route1bl exact target track cardinality failed: {len(exact_target_tracks)}")

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
            consider(clearance,{"kind":"pad","reference":p["reference"],"pad":p["pad"],"net":p["net"]})
        for t in tracks:
            if t["net"]==TARGET_NET:
                continue
            clearance=min(
                segment_segment_distance(a,b,t["start"],t["end"])-half-t["width"]/2.0
                for a,b in segs
            )
            consider(clearance,{
                "kind":"track","net":t["net"],
                "start_mm":list(t["start"]),"end_mm":list(t["end"]),
                "width_mm":round(t["width"],6),
            })
        for v in vias:
            if v["net"]==TARGET_NET:
                continue
            clearance=min(point_segment_distance(v["pos"],a,b)-v["radius"]-half for a,b in segs)
            consider(clearance,{"kind":"via","net":v["net"],"position_mm":list(v["pos"])})
        return round(best,6),nearest

    region=(min(A[0],B[0])-MARGIN,min(A[1],B[1])-MARGIN,max(A[0],B[0])+MARGIN,max(A[1],B[1])+MARGIN)
    xs=frange(region[0],region[2],GRID)
    ys=frange(region[1],region[3],GRID)
    raw=[]
    seen=set()
    def queue(kind,pts):
        pts=normalize(pts)
        if len(pts)<2 or len(pts)>5:
            return
        key=tuple(pts)
        if key in seen:
            return
        seen.add(key)
        length=path_length(pts)
        if length>MAX_PATH_LENGTH+EPS:
            return
        raw.append((len(pts)-1,round(length,6),kind,pts))

    queue("L-HV",[A,(B[0],A[1]),B])
    queue("L-VH",[A,(A[0],B[1]),B])
    for x in xs:
        queue("HVH",[A,(x,A[1]),(x,B[1]),B])
    for y in ys:
        queue("VHV",[A,(A[0],y),(B[0],y),B])
    for x in xs:
        for y in ys:
            queue("HVHV",[A,(x,A[1]),(x,y),(B[0],y),B])
            queue("VHVH",[A,(A[0],y),(x,y),(x,B[1]),B])

    raw.sort(key=lambda q:(q[0],q[1]))
    passing=[]
    best_clearance=None
    for seg_count,length,kind,pts in raw:
        clr,nearest=evaluate(pts)
        result={
            "path_family":kind,
            "points_mm":[list(p) for p in pts],
            "segment_count":seg_count,
            "path_length_mm":length,
            "minimum_conservative_clearance_mm":clr,
            "nearest_unrelated_copper":nearest,
            "rule_pass":clr+1e-6>=RULE,
        }
        if best_clearance is None or clr>best_clearance["minimum_conservative_clearance_mm"]:
            best_clearance=result
        if result["rule_pass"]:
            passing.append(result)

    passing.sort(key=lambda p:(p["segment_count"],p["path_length_mm"],-p["minimum_conservative_clearance_mm"]))
    out={
        "revision":"r13-route1bl-c301-coarse-multibend-screen",
        "source_route1bk_sha256":src_sha,
        "source_gate":{
            "rule_violations":0,
            "unconnected_items":113,
            "pin_net_audit":"PASS",
            "audited_nodes":268,
        },
        "board_modified":False,
        "drc_index":drc_index,
        "net":TARGET_NET,
        "C301_value":fps["C301"].GetValue(),
        "C301_pad1_mm":list(A),
        "C301_pad2_mm":[14.395,23.725],
        "target_point_mm":list(B),
        "target_track":{
            "start_mm":list(EXPECTED_TARGET_TRACK_START),
            "end_mm":list(EXPECTED_TARGET_TRACK_END),
            "width_mm":EXPECTED_TARGET_TRACK_WIDTH,
            "net":TARGET_NET,
        },
        "track_width_mm":WIDTH,
        "rule_clearance_mm":RULE,
        "grid_mm":GRID,
        "margin_mm":MARGIN,
        "max_segments":4,
        "max_path_length_mm":MAX_PATH_LENGTH,
        "candidate_path_count":len(raw),
        "passing_path_count":len(passing),
        "best_passing_path":passing[0] if passing else None,
        "top_passing_paths":passing[:20],
        "best_clearance_path":best_clearance,
        "release_status":"NOT_FOR_GERBER",
    }
    Path(args.output).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))


if __name__=="__main__":
    main()
