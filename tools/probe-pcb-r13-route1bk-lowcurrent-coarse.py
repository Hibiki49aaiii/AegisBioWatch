#!/usr/bin/env python3
"""Read-only optimized coarse multi-bend screen for low-current route-1bk candidates."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bj"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bj-r13.kicad_pcb"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bj.json"

WIDTH = 0.30
RULE = 0.10
GRID = 0.25
MARGIN = 3.0
MAX_PATH_LENGTH = 20.0
EPS = 1e-9

TARGETS = [
    {
        "id": "CHG_SENSE_GATE_R502_R501",
        "net": "CHG_SENSE_GATE",
        "a": "Pad 1 [CHG_SENSE_GATE] of R502 on Top_layer",
        "b": "Pad 2 [CHG_SENSE_GATE] of R501 on Top_layer",
    },
    {
        "id": "CHG_SENSE_GATE_R501_Q501",
        "net": "CHG_SENSE_GATE",
        "a": "Pad 2 [CHG_SENSE_GATE] of R501 on Top_layer",
        "b": "Pad 1 [CHG_SENSE_GATE] of Q501 on Top_layer",
    },
    {
        "id": "HAPTIC_TRIG",
        "net": "HAPTIC_TRIG",
        "a": "Pad 4 [HAPTIC_TRIG] of U4 on Top_layer",
        "b": "Pad 1 [HAPTIC_TRIG] of R303 on Top_layer",
    },
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


def rects_overlap(a, b) -> bool:
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def orient(a, b, c) -> float:
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def on_segment(a, b, p) -> bool:
    return (
        min(a[0], b[0])-EPS <= p[0] <= max(a[0], b[0])+EPS
        and min(a[1], b[1])-EPS <= p[1] <= max(a[1], b[1])+EPS
        and abs(orient(a, b, p)) <= EPS
    )


def segments_intersect(a,b,c,d) -> bool:
    o1,o2,o3,o4 = orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
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


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--route1bj-drc-json",required=True)
    ap.add_argument("--route1bj-pin-net-audit",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    report=load_json(SRC_REPORT)
    src_sha=sha256(SRC_PCB)
    if report.get("output_sha256") != src_sha:
        raise SystemExit("route1bk low-current source SHA gate failed")

    drc=load_json(Path(args.route1bj_drc_json))
    audit=load_json(Path(args.route1bj_pin_net_audit))
    if len(drc.get("violations",[])) != 0 or len(drc.get("unconnected_items",[])) != 114:
        raise SystemExit("route1bk low-current DRC source gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bk low-current audit source gate failed")

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={fp.GetReference():fp for fp in board.GetFootprints()}
    expected_values={
        "R501":"100k",
        "R502":"1M PD",
        "Q501":"2N7002-CLASS",
        "U4":"DRV2605LDGSR",
        "R303":"100k PD",
    }
    for ref,val in expected_values.items():
        if ref not in fps or fps[ref].GetValue()!=val:
            raise SystemExit(f"route1bk low-current identity gate failed: {ref}")

    pads=[]
    tracks=[]
    vias=[]
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.IsOnLayer(pcbnew.F_Cu):
                r=bbox(p)
                pads.append({
                    "reference":fp.GetReference(),
                    "pad":str(p.GetNumber()),
                    "net":p.GetNetname(),
                    "bbox":r,
                })
    for item in board.GetTracks():
        net=item.GetNetname() if hasattr(item,"GetNetname") else ""
        if isinstance(item,pcbnew.PCB_VIA):
            r=bbox(item)
            vias.append({
                "net":net,
                "pos":xy(item.GetPosition()),
                "radius":max(r[2]-r[0],r[3]-r[1])/2.0,
                "bbox":r,
            })
        elif item.GetLayer()==pcbnew.F_Cu:
            start=xy(item.GetStart())
            end=xy(item.GetEnd())
            width=mm(item.GetWidth())
            h=width/2.0
            r=(min(start[0],end[0])-h,min(start[1],end[1])-h,max(start[0],end[0])+h,max(start[1],end[1])+h)
            tracks.append({
                "net":net,
                "start":start,
                "end":end,
                "width":width,
                "bbox":r,
            })

    def make_evaluator(net,region):
        # Search paths cannot interact with copper whose copper bbox lies
        # farther than half route width + rule clearance outside this region.
        expand=WIDTH/2.0+RULE+1e-6
        rr=(region[0]-expand,region[1]-expand,region[2]+expand,region[3]+expand)
        lp=[p for p in pads if p["net"]!=net and rects_overlap(p["bbox"],rr)]
        lt=[t for t in tracks if t["net"]!=net and rects_overlap(t["bbox"],rr)]
        lv=[v for v in vias if v["net"]!=net and rects_overlap(v["bbox"],rr)]

        def evaluate(points):
            segs=list(zip(points,points[1:]))
            best=float("inf")
            nearest=None
            half=WIDTH/2.0

            def consider(clearance,item):
                nonlocal best,nearest
                if clearance < best:
                    best=clearance
                    nearest=item

            for p in lp:
                clearance=min(segment_rect_distance(a,b,p["bbox"])-half for a,b in segs)
                consider(clearance,{"kind":"pad","reference":p["reference"],"pad":p["pad"],"net":p["net"]})
                if best + 1e-6 < RULE:
                    # Still continue across obstacle types only if needed for a
                    # more descriptive nearest item; current item already proves fail.
                    pass
            for t in lt:
                clearance=min(
                    segment_segment_distance(a,b,t["start"],t["end"])-half-t["width"]/2.0
                    for a,b in segs
                )
                consider(clearance,{
                    "kind":"track","net":t["net"],
                    "start_mm":list(t["start"]),"end_mm":list(t["end"]),
                    "width_mm":round(t["width"],6),
                })
            for v in lv:
                clearance=min(point_segment_distance(v["pos"],a,b)-v["radius"]-half for a,b in segs)
                consider(clearance,{"kind":"via","net":v["net"],"position_mm":list(v["pos"])})
            return round(best,6),nearest

        return evaluate,{"pads":len(lp),"tracks":len(lt),"vias":len(lv)}

    results=[]
    for spec in TARGETS:
        matches=[]
        for idx,u in enumerate(drc["unconnected_items"]):
            items=u.get("items",[])
            if len(items)!=2:
                continue
            descs=[x["description"] for x in items]
            if set(descs)=={spec["a"],spec["b"]}:
                bydesc={x["description"]:x for x in items}
                matches.append((idx,bydesc[spec["a"]],bydesc[spec["b"]]))
        if len(matches)!=1:
            raise SystemExit(f"route1bk target DRC cardinality failed {spec['id']}: {len(matches)}")

        idx,ai,bi=matches[0]
        A=(float(ai["pos"]["x"]),float(ai["pos"]["y"]))
        B=(float(bi["pos"]["x"]),float(bi["pos"]["y"]))
        region=(min(A[0],B[0])-MARGIN,min(A[1],B[1])-MARGIN,max(A[0],B[0])+MARGIN,max(A[1],B[1])+MARGIN)
        evaluate,obstacle_counts=make_evaluator(spec["net"],region)

        xs=frange(region[0],region[2],GRID)
        ys=frange(region[1],region[3],GRID)

        raw_paths=[]
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
            if length > MAX_PATH_LENGTH + EPS:
                return
            raw_paths.append((len(pts)-1,round(length,6),kind,pts))

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

        raw_paths.sort(key=lambda q:(q[0],q[1]))
        first_pass=None
        best_clearance=None
        evaluated=0
        for seg_count,length,kind,pts in raw_paths:
            clr,nearest=evaluate(pts)
            evaluated+=1
            result={
                "path_family":kind,
                "points_mm":[list(p) for p in pts],
                "segment_count":seg_count,
                "path_length_mm":length,
                "minimum_conservative_clearance_mm":clr,
                "nearest_unrelated_copper":nearest,
                "rule_pass":clr+1e-6>=RULE,
            }
            if best_clearance is None or clr > best_clearance["minimum_conservative_clearance_mm"]:
                best_clearance=result
            if result["rule_pass"]:
                first_pass=result
                break

        results.append({
            "id":spec["id"],
            "drc_index":idx,
            "net":spec["net"],
            "a":{"description":spec["a"],"position_mm":list(A)},
            "b":{"description":spec["b"],"position_mm":list(B)},
            "search_region_mm":list(region),
            "local_obstacle_counts":obstacle_counts,
            "candidate_path_count":len(raw_paths),
            "evaluated_path_count":evaluated,
            "passing_path_count":1 if first_pass else 0,
            "best_passing_path":first_pass,
            "best_clearance_path":best_clearance,
            "search_stopped_after_first_pass":first_pass is not None,
        })

    out={
        "revision":"r13-route1bk-lowcurrent-coarse-shortest-first-screen",
        "source_route1bj_sha256":src_sha,
        "source_gate":{
            "rule_violations":0,
            "unconnected_items":114,
            "pin_net_audit":"PASS",
            "audited_nodes":268,
        },
        "board_modified":False,
        "track_width_mm":WIDTH,
        "rule_clearance_mm":RULE,
        "grid_mm":GRID,
        "margin_mm":MARGIN,
        "max_segments":4,
        "max_path_length_mm":MAX_PATH_LENGTH,
        "search_policy":"shortest-first, stop after first legal path per target",
        "targets":results,
        "release_status":"NOT_FOR_GERBER",
    }
    Path(args.output).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))

    if out["board_modified"] is not False:
        raise SystemExit("route1bk low-current board-modified gate failed")


if __name__=="__main__":
    main()
