#!/usr/bin/env python3
"""Materialize route-1bn: +1V8 source track -> R403.1/+1V8."""
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

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bm"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bm-r13.kicad_pcb"
SRC_PRO = SRC_DIR / "AegisBioWatch-MainBoard-Route1bm-r13.kicad_pro"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bm.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bn"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bn-r13.kicad_pcb"
OUT_PRO = OUT_DIR / "AegisBioWatch-MainBoard-Route1bn-r13.kicad_pro"
REPORT_HELPER = ROOT / "tools/write-pcb-r13-route1bn-report.py"

TARGET_NET = "+1V8"
POINTS = [
    (41.005, 14.975),
    (41.005, 15.650),
    (39.600, 15.650),
    (39.600, 25.975),
    (40.255, 25.975),
]
TRACK_WIDTH = 0.30
EXPECTED_CLEARANCE = 0.26
SOURCE_ENDPOINT = POINTS[0]
SOURCE_TRACK_LENGTH_MM = 4.6628
R403_PAD1 = POINTS[-1]
R403_PAD2 = (40.895, 25.975)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mm(v) -> float:
    return float(pcbnew.ToMM(v))


def iu(v: float) -> int:
    return int(pcbnew.FromMM(v))


def xy(v) -> tuple[float, float]:
    return (round(mm(v.x),6), round(mm(v.y),6))


def near(a,b,tol:float=0.002)->bool:
    return math.dist(a,b)<=tol


def get_pad(fp, number: str):
    pads=[p for p in fp.Pads() if str(p.GetNumber())==str(number)]
    if len(pads)!=1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(pads)}")
    return pads[0]


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--route1bm-drc-json",required=True)
    ap.add_argument("--route1bm-pin-net-audit",required=True)
    ap.add_argument("--exact-probe-json",required=True)
    args=ap.parse_args()

    source_report=load_json(SRC_REPORT)
    source_sha=sha256(SRC_PCB)
    if source_report.get("output_sha256")!=source_sha:
        raise SystemExit("route1bn source report/PCB SHA mismatch")
    drc=load_json(Path(args.route1bm_drc_json))
    audit=load_json(Path(args.route1bm_pin_net_audit))
    probe=load_json(Path(args.exact_probe_json))
    if len(drc.get("violations",[]))!=0 or len(drc.get("unconnected_items",[]))!=111:
        raise SystemExit("route1bn source DRC gate failed")
    if audit.get("result")!="PASS" or audit.get("audited_present_source_nodes")!=268 or audit.get("mismatches",[])!=[] or audit.get("unexpected_pad_nets",[])!=[]:
        raise SystemExit("route1bn source audit gate failed")
    if probe.get("revision")!="r13-route1bn-r403-1v8-exact-probe":
        raise SystemExit("route1bn exact-probe revision gate failed")
    if probe.get("source_route1bm_sha256")!=source_sha or probe.get("board_modified") is not False:
        raise SystemExit("route1bn exact-probe provenance gate failed")
    path=probe.get("path",{})
    if path.get("points_mm") != [list(p) for p in POINTS]:
        raise SystemExit("route1bn exact-probe path gate failed")
    if path.get("path_family")!="VHVH" or path.get("segment_count")!=4 or path.get("track_width_mm")!=TRACK_WIDTH:
        raise SystemExit("route1bn exact-probe scope gate failed")
    if abs(float(path.get("minimum_conservative_clearance_mm",-1))-EXPECTED_CLEARANCE)>1e-6:
        raise SystemExit("route1bn exact-probe clearance gate failed")
    if probe.get("vias_planned")!=0 or probe.get("component_moves_planned")!=0 or probe.get("component_rotations_planned")!=0 or probe.get("design_rule_waiver") is not False:
        raise SystemExit("route1bn mutation scope gate failed")

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={fp.GetReference():fp for fp in board.GetFootprints()}
    r403=fps.get("R403")
    if r403 is None or r403.GetValue()!="4.7k PU PROV":
        raise SystemExit("route1bn R403 identity gate failed")
    p1,p2=get_pad(r403,"1"),get_pad(r403,"2")
    if (p1.GetNetname(),xy(p1.GetPosition()))!=(TARGET_NET,R403_PAD1):
        raise SystemExit("route1bn R403.1 gate failed")
    if (p2.GetNetname(),xy(p2.GetPosition()))!=("SYS_I2C_SDA",R403_PAD2):
        raise SystemExit("route1bn R403.2 preservation gate failed")

    source_tracks=[]
    existing_candidate=[]
    r403_touch=[]
    for item in board.GetTracks():
        if isinstance(item,pcbnew.PCB_VIA) or item.GetLayer()!=pcbnew.F_Cu:
            continue
        net=item.GetNetname()
        a,b=xy(item.GetStart()),xy(item.GetEnd())
        w=round(mm(item.GetWidth()),6)
        if net==TARGET_NET and (near(a,SOURCE_ENDPOINT) or near(b,SOURCE_ENDPOINT)) and abs(mm(item.GetLength())-SOURCE_TRACK_LENGTH_MM)<=0.002:
            source_tracks.append((a,b,round(mm(item.GetLength()),6),w))
        if net==TARGET_NET and (near(a,R403_PAD1) or near(b,R403_PAD1)):
            r403_touch.append((a,b))
        if net==TARGET_NET and abs(w-TRACK_WIDTH)<1e-6:
            for p,q in zip(POINTS,POINTS[1:]):
                if (near(a,p) and near(b,q)) or (near(a,q) and near(b,p)):
                    existing_candidate.append((p,q))
    if len(source_tracks)!=1:
        raise SystemExit(f"route1bn source-track gate failed: {source_tracks}")
    if r403_touch or existing_candidate:
        raise SystemExit(f"route1bn candidate copper already exists: r403={r403_touch}, candidate={existing_candidate}")

    net=board.FindNet(TARGET_NET)
    if net is None:
        raise SystemExit("route1bn +1V8 net reacquire failed")
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
        raise SystemExit("route1bn zone refill failed")
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board):
        raise SystemExit("route1bn SaveBoard failed")
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])


if __name__=="__main__":
    main()
