#!/usr/bin/env python3
"""Materialize route-1bo: +1V8 source track -> J8.1/+1V8."""
from __future__ import annotations

import argparse
import faulthandler
import hashlib
import json
import math
import os
import shutil
import sys
from pathlib import Path

import pcbnew  # type: ignore

faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/"hardware/main-board/pcb/route-r13-1bn"
SRC_PCB=SRC_DIR/"AegisBioWatch-MainBoard-Route1bn-r13.kicad_pcb"
SRC_PRO=SRC_DIR/"AegisBioWatch-MainBoard-Route1bn-r13.kicad_pro"
SRC_REPORT=SRC_DIR/"routing-seed-r13-1bn.json"
OUT_DIR=ROOT/"hardware/main-board/pcb/route-r13-1bo"
OUT_PCB=OUT_DIR/"AegisBioWatch-MainBoard-Route1bo-r13.kicad_pcb"
OUT_PRO=OUT_DIR/"AegisBioWatch-MainBoard-Route1bo-r13.kicad_pro"
REPORT_HELPER=ROOT/"tools/write-pcb-r13-route1bo-report.py"

TARGET_NET="+1V8"
POINTS=[(10.305,4.72),(9.7,4.72),(9.7,15.8),(12.105,15.8),(12.105,15.26)]
TRACK_WIDTH=0.30
EXPECTED_CLEARANCE=0.4897
SOURCE_ENDPOINT=POINTS[0]
SOURCE_TRACK_LENGTH_MM=6.3650
J8_PAD1=POINTS[-1]
EXPECTED_BLANKS={(10.835,14.625),(15.915,13.609),(15.915,15.641)}


def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mm(v)->float:
    return float(pcbnew.ToMM(v))


def iu(v:float)->int:
    return int(pcbnew.FromMM(v))


def xy(v)->tuple[float,float]:
    return (round(mm(v.x),6),round(mm(v.y),6))


def near(a,b,tol:float=0.002)->bool:
    return math.dist(a,b)<=tol


def get_pad(fp,number:str):
    pads=[p for p in fp.Pads() if str(p.GetNumber())==str(number)]
    if len(pads)!=1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(pads)}")
    return pads[0]


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--route1bn-drc-json",required=True)
    ap.add_argument("--route1bn-pin-net-audit",required=True)
    ap.add_argument("--exact-probe-json",required=True)
    args=ap.parse_args()

    source_report=load_json(SRC_REPORT)
    source_sha=sha256(SRC_PCB)
    if source_report.get("output_sha256")!=source_sha:
        raise SystemExit("route1bo source report/PCB SHA mismatch")
    drc=load_json(Path(args.route1bn_drc_json))
    audit=load_json(Path(args.route1bn_pin_net_audit))
    probe=load_json(Path(args.exact_probe_json))
    if len(drc.get("violations",[]))!=0 or len(drc.get("unconnected_items",[]))!=110:
        raise SystemExit("route1bo source DRC gate failed")
    if audit.get("result")!="PASS" or audit.get("audited_present_source_nodes")!=268 or audit.get("mismatches",[])!=[] or audit.get("unexpected_pad_nets",[])!=[]:
        raise SystemExit("route1bo source audit gate failed")
    if probe.get("revision")!="r13-route1bo-j8-1v8-exact-probe" or probe.get("source_route1bn_sha256")!=source_sha or probe.get("board_modified") is not False:
        raise SystemExit("route1bo exact-probe provenance gate failed")
    if probe.get("J8",{}).get("numberless_pads_all_npth") is not True:
        raise SystemExit("route1bo exact-probe J8 NPTH gate failed")
    path=probe.get("path",{})
    if path.get("points_mm")!=[list(p) for p in POINTS] or path.get("path_family")!="HVHV" or path.get("segment_count")!=4 or path.get("track_width_mm")!=TRACK_WIDTH:
        raise SystemExit("route1bo exact-probe path/scope gate failed")
    if abs(float(path.get("minimum_conservative_clearance_mm",-1))-EXPECTED_CLEARANCE)>1e-6:
        raise SystemExit("route1bo exact-probe clearance gate failed")
    if probe.get("vias_planned")!=0 or probe.get("component_moves_planned")!=0 or probe.get("component_rotations_planned")!=0 or probe.get("design_rule_waiver") is not False or probe.get("via_in_pad") is not False:
        raise SystemExit("route1bo mutation scope gate failed")

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={fp.GetReference():fp for fp in board.GetFootprints()}
    j8=fps.get("J8")
    if j8 is None or j8.GetValue()!="TC2030_SWD_6":
        raise SystemExit("route1bo J8 identity gate failed")
    p1=get_pad(j8,"1")
    if (p1.GetNetname(),xy(p1.GetPosition()))!=(TARGET_NET,J8_PAD1):
        raise SystemExit("route1bo J8.1 gate failed")
    blanks=[p for p in j8.Pads() if str(p.GetNumber())==""]
    if len(blanks)!=3 or {xy(p.GetPosition()) for p in blanks}!=EXPECTED_BLANKS or any(p.GetAttribute()!=pcbnew.PAD_ATTRIB_NPTH or p.GetNetname()!="" for p in blanks):
        raise SystemExit("route1bo J8 numberless NPTH preservation gate failed")

    source_tracks=[]
    existing_candidate=[]
    j8_touch=[]
    for item in board.GetTracks():
        if isinstance(item,pcbnew.PCB_VIA) or item.GetLayer()!=pcbnew.F_Cu:
            continue
        net=item.GetNetname()
        a,b=xy(item.GetStart()),xy(item.GetEnd())
        w=round(mm(item.GetWidth()),6)
        if net==TARGET_NET and (near(a,SOURCE_ENDPOINT) or near(b,SOURCE_ENDPOINT)) and abs(mm(item.GetLength())-SOURCE_TRACK_LENGTH_MM)<=0.002:
            source_tracks.append((a,b,round(mm(item.GetLength()),6),w))
        if net==TARGET_NET and (near(a,J8_PAD1) or near(b,J8_PAD1)):
            j8_touch.append((a,b))
        if net==TARGET_NET and abs(w-TRACK_WIDTH)<1e-6:
            for p,q in zip(POINTS,POINTS[1:]):
                if (near(a,p) and near(b,q)) or (near(a,q) and near(b,p)):
                    existing_candidate.append((p,q))
    if len(source_tracks)!=1:
        raise SystemExit(f"route1bo source-track gate failed: {source_tracks}")
    if j8_touch or existing_candidate:
        raise SystemExit(f"route1bo candidate copper already exists: j8={j8_touch}, candidate={existing_candidate}")

    net=board.FindNet(TARGET_NET)
    if net is None:
        raise SystemExit("route1bo +1V8 net reacquire failed")
    for a,b in zip(POINTS,POINTS[1:]):
        track=pcbnew.PCB_TRACK(board)
        track.SetLayer(pcbnew.F_Cu)
        track.SetNet(net)
        track.SetWidth(iu(TRACK_WIDTH))
        track.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1])))
        track.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1])))
        board.Add(track)

    zones=pcbnew.ZONES()
    for z in board.Zones():
        zones.append(z)
    if len(zones) and not pcbnew.ZONE_FILLER(board).Fill(zones):
        raise SystemExit("route1bo zone refill failed")
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board):
        raise SystemExit("route1bo SaveBoard failed")
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])


if __name__=="__main__":
    main()
