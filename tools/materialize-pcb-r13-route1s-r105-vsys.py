#!/usr/bin/env python3
"""r13 route-1s: connect R105.1/VSYS into the accepted VSYS spine.

Source: executed-KiCad-clean route-1r (0 violations / 157 unconnected /
268-node physical audit PASS).

The optional R105 VSYS side escapes left to a new through via, routes on B.Cu
above the accepted VBUSOUT_SENSE corridor, then joins the existing accepted
VSYS via at (15.50,27.57). No accepted route-1r copper is modified.

Planning/evidence artifact only; not fabrication authority.
"""
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
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1r'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1r-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1r-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1r.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1s'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1s-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1s-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1s-report.py'

TRACK_WIDTH = 0.30
VSYS_VIA = (11.90, 24.70)
BEND1 = (11.90, 24.35)
BEND2 = (15.65, 24.35)
BEND3 = (15.65, 27.15)
TARGET_VSYS_VIA = (15.50, 27.57)
VIA_SIZE = 0.60
VIA_DRILL = 0.30


def stage(name: str) -> None:
    print(f'[route1s] {name}', flush=True)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def loadj(path: str | Path):
    return json.loads(Path(path).read_text())


def mm(v) -> float:
    return float(pcbnew.ToMM(v))


def iu(v: float) -> int:
    return int(pcbnew.FromMM(v))


def pads(fp, number: str):
    return [p for p in fp.Pads() if str(p.GetNumber()) == str(number)]


def point(fp, number: str):
    ps = pads(fp, number)
    if not ps:
        raise SystemExit(f'{fp.GetReference()} missing pad {number}')
    return (
        sum(mm(p.GetPosition().x) for p in ps) / len(ps),
        sum(mm(p.GetPosition().y) for p in ps) / len(ps),
    )


def add_track(board, net, a, b, width, layer):
    t = pcbnew.PCB_TRACK(board)
    t.SetLayer(layer)
    t.SetNet(net)
    t.SetWidth(iu(width))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]), iu(a[1])))
    t.SetEnd(pcbnew.VECTOR2I(iu(b[0]), iu(b[1])))
    board.Add(t)
    return 1


def add_via(board, net, p):
    v = pcbnew.PCB_VIA(board)
    v.SetNet(net)
    v.SetPosition(pcbnew.VECTOR2I(iu(p[0]), iu(p[1])))
    v.SetWidth(iu(VIA_SIZE))
    v.SetDrill(iu(VIA_DRILL))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    board.Add(v)
    return 1


def has_vsys_via(board, p):
    for item in board.GetTracks():
        if not isinstance(item, pcbnew.PCB_VIA):
            continue
        if item.GetNetname() != 'VSYS':
            continue
        q = item.GetPosition()
        if abs(mm(q.x)-p[0]) <= 0.001 and abs(mm(q.y)-p[1]) <= 0.001:
            return True
    return False


def refill_all_zones(board):
    zs = pcbnew.ZONES()
    for z in board.Zones():
        zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs):
        raise SystemExit('route1s zone refill failed')


def main():
    stage('start')
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1r-drc-json', required=True)
    ap.add_argument('--route1r-pin-net-audit', required=True)
    args = ap.parse_args()

    rep = loadj(SRC_REPORT)
    srcsha = sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1r report/PCB SHA mismatch')
    d = loadj(args.route1r_drc_json)
    a = loadj(args.route1r_pin_net_audit)
    if len(d.get('violations', [])) != 0 or len(d.get('unconnected_items', [])) != 157:
        raise SystemExit('route1r DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1r pin/net gate failed')
    stage('source gates passed')

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    if 'R105' not in fps:
        raise SystemExit('route1s missing R105')
    r105 = fps['R105']
    gates = {
        'R105.1': pads(r105, '1')[0].GetNetname(),
        'R105.2': pads(r105, '2')[0].GetNetname(),
        'R105.value': r105.GetValue(),
    }
    expected = {
        'R105.1': 'VSYS',
        'R105.2': 'LDO1_IN',
        'R105.value': '0R DNP/OPTION',
    }
    if gates != expected:
        raise SystemExit(f'route1s net/value gate failed: {gates}')

    r105_vsys = point(r105, '1')
    if abs(r105_vsys[0]-12.46307) > 0.001 or abs(r105_vsys[1]-24.750105) > 0.001:
        raise SystemExit(f'route1s R105.1 geometry gate failed: {r105_vsys}')
    if not has_vsys_via(board, TARGET_VSYS_VIA):
        raise SystemExit('route1s accepted target VSYS via missing')

    vsys = board.FindNet('VSYS')
    if vsys is None:
        raise SystemExit('route1s VSYS net reacquire failed')

    added = 0
    vias = 0
    added += add_track(board, vsys, r105_vsys, VSYS_VIA, TRACK_WIDTH, pcbnew.F_Cu)
    vias += add_via(board, vsys, VSYS_VIA)
    added += add_track(board, vsys, VSYS_VIA, BEND1, TRACK_WIDTH, pcbnew.B_Cu)
    added += add_track(board, vsys, BEND1, BEND2, TRACK_WIDTH, pcbnew.B_Cu)
    added += add_track(board, vsys, BEND2, BEND3, TRACK_WIDTH, pcbnew.B_Cu)
    added += add_track(board, vsys, BEND3, TARGET_VSYS_VIA, TRACK_WIDTH, pcbnew.B_Cu)
    if added != 5 or vias != 1:
        raise SystemExit(f'route1s internal scope gate failed: segments={added} vias={vias}')

    refill_all_zones(board)
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit('route1s SaveBoard failed')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1s report helper missing')
    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
