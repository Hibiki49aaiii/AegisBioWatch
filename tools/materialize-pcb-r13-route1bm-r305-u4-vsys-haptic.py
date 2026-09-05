#!/usr/bin/env python3
"""Materialize route-1bm: R305.2/VSYS_HAPTIC -> U4.10/VSYS_HAPTIC."""
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
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bl"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bl-r13.kicad_pcb"
SRC_PRO = SRC_DIR / "AegisBioWatch-MainBoard-Route1bl-r13.kicad_pro"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bl.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bm"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bm-r13.kicad_pcb"
OUT_PRO = OUT_DIR / "AegisBioWatch-MainBoard-Route1bm-r13.kicad_pro"
REPORT_HELPER = ROOT / "tools/write-pcb-r13-route1bm-report.py"

TARGET_NET = "VSYS_HAPTIC"
POINTS = [
    (31.315, 18.595),
    (31.315, 17.500),
    (25.000, 17.500),
    (25.000, 13.400),
    (23.005, 13.400),
]
TRACK_WIDTH = 0.30
EXPECTED_CLEARANCE = 0.20
R305_PAD1 = (30.295, 18.595)
R305_PAD2 = POINTS[0]
U4_PAD10 = POINTS[-1]
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


def mm(v: int) -> float:
    return float(pcbnew.ToMM(v))


def iu(v: float) -> int:
    return int(pcbnew.FromMM(v))


def xy(v) -> tuple[float, float]:
    return (round(mm(v.x), 6), round(mm(v.y), 6))


def get_pad(fp, number: str):
    pads=[p for p in fp.Pads() if str(p.GetNumber())==str(number)]
    if len(pads)!=1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(pads)}")
    return pads[0]


def near(a,b,tol:float=0.002)->bool:
    return math.dist(a,b)<=tol


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--route1bl-drc-json",required=True)
    ap.add_argument("--route1bl-pin-net-audit",required=True)
    ap.add_argument("--exact-probe-json",required=True)
    args=ap.parse_args()

    source_report=load_json(SRC_REPORT)
    source_sha=sha256(SRC_PCB)
    if source_report.get("output_sha256")!=source_sha:
        raise SystemExit("route1bm source report/PCB SHA mismatch")

    drc=load_json(Path(args.route1bl_drc_json))
    audit=load_json(Path(args.route1bl_pin_net_audit))
    probe=load_json(Path(args.exact_probe_json))
    if len(drc.get("violations",[]))!=0 or len(drc.get("unconnected_items",[]))!=112:
        raise SystemExit("route1bm source DRC gate failed")
    if (
        audit.get("result")!="PASS"
        or audit.get("audited_present_source_nodes")!=268
        or audit.get("mismatches",[])!=[]
        or audit.get("unexpected_pad_nets",[])!=[]
    ):
        raise SystemExit("route1bm source audit gate failed")
    if probe.get("revision")!="r13-route1bm-r305-u4-vsys-haptic-exact-probe":
        raise SystemExit("route1bm exact-probe revision gate failed")
    if probe.get("source_route1bl_sha256")!=source_sha or probe.get("board_modified") is not False:
        raise SystemExit("route1bm exact-probe provenance gate failed")
    path=probe.get("path",{})
    if path.get("points_mm") != [list(p) for p in POINTS]:
        raise SystemExit("route1bm exact-probe path gate failed")
    if path.get("path_family")!="VHVH" or path.get("segment_count")!=4:
        raise SystemExit("route1bm exact-probe scope gate failed")
    if path.get("track_width_mm")!=TRACK_WIDTH:
        raise SystemExit("route1bm exact-probe width gate failed")
    if abs(float(path.get("minimum_conservative_clearance_mm",-1))-EXPECTED_CLEARANCE)>1e-6:
        raise SystemExit("route1bm exact-probe clearance gate failed")
    if probe.get("vias_planned")!=0 or probe.get("component_moves_planned")!=0 or probe.get("component_rotations_planned")!=0:
        raise SystemExit("route1bm exact-probe mutation scope gate failed")
    if probe.get("design_rule_waiver") is not False:
        raise SystemExit("route1bm design-rule waiver gate failed")

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={fp.GetReference():fp for fp in board.GetFootprints()}
    r305,u4,c305,c304=fps.get("R305"),fps.get("U4"),fps.get("C305"),fps.get("C304")
    if None in (r305,u4,c305,c304):
        raise SystemExit("route1bm missing haptic supply components")
    if r305.GetValue()!="0R / FB OPTION" or u4.GetValue()!="DRV2605LDGSR":
        raise SystemExit("route1bm R305/U4 identity gate failed")
    if c305.GetValue()!="1uF" or c304.GetValue()!="100nF":
        raise SystemExit("route1bm C305/C304 identity gate failed")

    r305p1,r305p2=get_pad(r305,"1"),get_pad(r305,"2")
    u4p10=get_pad(u4,"10")
    c305p1,c304p1=get_pad(c305,"1"),get_pad(c304,"1")
    if (r305p1.GetNetname(),xy(r305p1.GetPosition()))!=("VSYS",R305_PAD1):
        raise SystemExit("route1bm R305.1 preservation gate failed")
    if (r305p2.GetNetname(),xy(r305p2.GetPosition()))!=(TARGET_NET,R305_PAD2):
        raise SystemExit("route1bm R305.2 gate failed")
    if (u4p10.GetNetname(),xy(u4p10.GetPosition()))!=(TARGET_NET,U4_PAD10):
        raise SystemExit("route1bm U4.10 gate failed")
    if (c305p1.GetNetname(),xy(c305p1.GetPosition()))!=(TARGET_NET,BYPASS_POINTS[0]):
        raise SystemExit("route1bm C305.1 gate failed")
    if (c304p1.GetNetname(),xy(c304p1.GetPosition()))!=(TARGET_NET,BYPASS_POINTS[-1]):
        raise SystemExit("route1bm C304.1 gate failed")

    bypass_hits=[]
    existing_candidate=[]
    r305_touch=[]
    u4_touch=[]
    for item in board.GetTracks():
        if isinstance(item,pcbnew.PCB_VIA) or item.GetLayer()!=pcbnew.F_Cu:
            continue
        net=item.GetNetname()
        a,b=xy(item.GetStart()),xy(item.GetEnd())
        w=round(mm(item.GetWidth()),6)
        if net!=TARGET_NET or abs(w-TRACK_WIDTH)>=1e-6:
            continue
        for p,q in zip(BYPASS_POINTS,BYPASS_POINTS[1:]):
            if (near(a,p) and near(b,q)) or (near(a,q) and near(b,p)):
                bypass_hits.append((p,q))
        for p,q in zip(POINTS,POINTS[1:]):
            if (near(a,p) and near(b,q)) or (near(a,q) and near(b,p)):
                existing_candidate.append((p,q))
        if near(a,R305_PAD2) or near(b,R305_PAD2):
            r305_touch.append((a,b))
        if near(a,U4_PAD10) or near(b,U4_PAD10):
            u4_touch.append((a,b))
    if len(bypass_hits)!=3:
        raise SystemExit(f"route1bm accepted bypass geometry gate failed: {bypass_hits}")
    if existing_candidate or r305_touch or u4_touch:
        raise SystemExit(
            f"route1bm candidate copper already exists: candidate={existing_candidate}, r305={r305_touch}, u4={u4_touch}"
        )

    net=board.FindNet(TARGET_NET)
    if net is None:
        raise SystemExit("route1bm VSYS_HAPTIC net reacquire failed")
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
        raise SystemExit("route1bm zone refill failed")
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board):
        raise SystemExit("route1bm SaveBoard failed")
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO,OUT_PRO)

    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])


if __name__=="__main__":
    main()
