#!/usr/bin/env python3
"""Materialize route-1bl: accepted VSYS source endpoint -> R106.1/VSYS."""
from __future__ import annotations

import argparse
import faulthandler
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

import pcbnew  # type: ignore

faulthandler.enable()

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bk"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bk-r13.kicad_pcb"
SRC_PRO = SRC_DIR / "AegisBioWatch-MainBoard-Route1bk-r13.kicad_pro"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bk.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bl"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bl-r13.kicad_pcb"
OUT_PRO = OUT_DIR / "AegisBioWatch-MainBoard-Route1bl-r13.kicad_pro"
REPORT_HELPER = ROOT / "tools/write-pcb-r13-route1bl-report.py"

POINTS = [(7.35, 28.25), (7.2, 28.25), (7.2, 26.4), (5.270826, 26.4), (5.270826, 25.865834)]
TRACK_WIDTH = 0.30
EXPECTED_CLEARANCE = 0.184166
SOURCE_TRACK_START = (8.9875, 28.25)
SOURCE_TRACK_END = (7.35, 28.25)
R106_PAD1 = (5.270826, 25.865834)
R106_PAD2 = (5.910826, 25.865834)


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


def pos(pad) -> tuple[float, float]:
    return xy(pad.GetPosition())


def get_pad(fp, number: str):
    pads=[p for p in fp.Pads() if str(p.GetNumber())==str(number)]
    if len(pads)!=1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(pads)}")
    return pads[0]


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--route1bk-drc-json",required=True)
    ap.add_argument("--route1bk-pin-net-audit",required=True)
    ap.add_argument("--exact-probe-json",required=True)
    args=ap.parse_args()

    source_report=load_json(SRC_REPORT)
    source_sha=sha256(SRC_PCB)
    if source_report.get("output_sha256")!=source_sha:
        raise SystemExit("route1bl source report/PCB SHA mismatch")

    drc=load_json(Path(args.route1bk_drc_json))
    audit=load_json(Path(args.route1bk_pin_net_audit))
    probe=load_json(Path(args.exact_probe_json))
    if len(drc.get("violations",[]))!=0 or len(drc.get("unconnected_items",[]))!=113:
        raise SystemExit("route1bl source DRC gate failed")
    if audit.get("result")!="PASS" or audit.get("audited_present_source_nodes")!=268:
        raise SystemExit("route1bl source audit gate failed")
    if probe.get("source_route1bk_sha256")!=source_sha or probe.get("board_modified") is not False:
        raise SystemExit("route1bl exact-probe provenance gate failed")
    path=probe.get("effective_new_copper_path",{})
    if path.get("points_mm") != [list(p) for p in POINTS]:
        raise SystemExit("route1bl exact-probe path gate failed")
    if path.get("segment_count")!=4 or path.get("track_width_mm")!=TRACK_WIDTH:
        raise SystemExit("route1bl exact-probe scope gate failed")
    if float(path.get("minimum_conservative_clearance_mm",-1)) < EXPECTED_CLEARANCE-1e-6:
        raise SystemExit("route1bl exact-probe clearance gate failed")
    if float(path.get("independent_r106p2_gap_mm",-1)) < EXPECTED_CLEARANCE-1e-6:
        raise SystemExit("route1bl independent R106.2 clearance gate failed")
    if probe.get("accepted_source_track_overlap_materialized") is not False:
        raise SystemExit("route1bl overlap policy gate failed")

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={fp.GetReference():fp for fp in board.GetFootprints()}
    r106=fps.get("R106")
    if r106 is None or r106.GetValue()!="0R DNP/OPTION":
        raise SystemExit("route1bl R106 identity gate failed")
    p1,p2=get_pad(r106,"1"),get_pad(r106,"2")
    if (p1.GetNetname(),pos(p1))!=("VSYS",R106_PAD1):
        raise SystemExit("route1bl R106.1 gate failed")
    if (p2.GetNetname(),pos(p2))!=("LDO2_IN",R106_PAD2):
        raise SystemExit("route1bl R106.2/LDO2_IN preservation gate failed")

    exact_source=[]
    existing_new=[]
    for item in board.GetTracks():
        if isinstance(item,pcbnew.PCB_VIA) or item.GetLayer()!=pcbnew.F_Cu:
            continue
        net=item.GetNetname()
        a,b=xy(item.GetStart()),xy(item.GetEnd())
        w=round(mm(item.GetWidth()),6)
        if net=="VSYS" and {a,b}=={SOURCE_TRACK_START,SOURCE_TRACK_END} and abs(w-TRACK_WIDTH)<1e-6:
            exact_source.append(item)
        for p,q in zip(POINTS,POINTS[1:]):
            if net=="VSYS" and {a,b}=={p,q} and abs(w-TRACK_WIDTH)<1e-6:
                existing_new.append((p,q))
    if len(exact_source)!=1:
        raise SystemExit(f"route1bl source VSYS track cardinality failed: {len(exact_source)}")
    if existing_new:
        raise SystemExit(f"route1bl candidate copper already exists: {existing_new}")

    net=board.FindNet("VSYS")
    if net is None:
        raise SystemExit("route1bl VSYS net reacquire failed")

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
        raise SystemExit("route1bl zone refill failed")
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board):
        raise SystemExit("route1bl SaveBoard failed")
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO,OUT_PRO)

    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])


if __name__=="__main__":
    main()
