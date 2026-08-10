#!/usr/bin/env python3
"""r13 route-1q: close nPM1300 VSET2 strap and its local GND return.

Source: executed-KiCad-clean route-1p (0 violations / 160 unconnected /
268-node physical audit PASS).

This increment connects only U2.16/PMIC_VSET2 to R102.1 and R102.2/GND to the
continuous In1.Cu GND reference. A dogleg keeps the VSET2 trace clear of the
accepted VSET1/R101 geometry and C113. CHG_5V remains deferred.

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
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1p'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1p-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1p-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1p.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1q'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1q-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1q-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1q-report.py'

VSET_WIDTH = 0.20
GND_WIDTH = 0.30
VSET_BEND1 = (13.30, 31.35)
VSET_BEND2 = (13.30, 32.80)
GND_VIA = (15.40, 33.15)
VIA_SIZE = 0.60
VIA_DRILL = 0.30


def stage(name: str) -> None:
    print(f'[route1q] {name}', flush=True)


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


def add_track(board, net, a, b, width):
    t = pcbnew.PCB_TRACK(board)
    t.SetLayer(pcbnew.F_Cu)
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


def refill_all_zones(board):
    zs = pcbnew.ZONES()
    for z in board.Zones():
        zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs):
        raise SystemExit('route1q zone refill failed')


def main():
    stage('start')
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1p-drc-json', required=True)
    ap.add_argument('--route1p-pin-net-audit', required=True)
    args = ap.parse_args()

    rep = loadj(SRC_REPORT)
    srcsha = sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1p report/PCB SHA mismatch')
    d = loadj(args.route1p_drc_json)
    a = loadj(args.route1p_pin_net_audit)
    if len(d.get('violations', [])) != 0 or len(d.get('unconnected_items', [])) != 160:
        raise SystemExit('route1p DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1p pin/net gate failed')
    stage('source gates passed')

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    for ref in ('U2', 'R102'):
        if ref not in fps:
            raise SystemExit(f'route1q missing {ref}')
    u2, r102 = fps['U2'], fps['R102']

    gates = {
        'U2.16': pads(u2, '16')[0].GetNetname(),
        'R102.1': pads(r102, '1')[0].GetNetname(),
        'R102.2': pads(r102, '2')[0].GetNetname(),
        'R102.value': r102.GetValue(),
    }
    expected = {
        'U2.16': 'PMIC_VSET2',
        'R102.1': 'PMIC_VSET2',
        'R102.2': 'GND',
        'R102.value': '150k 1%',
    }
    if gates != expected:
        raise SystemExit(f'route1q net/value gate failed: {gates}')

    u2_vset = point(u2, '16')
    r102_vset = point(r102, '1')
    r102_gnd = point(r102, '2')
    expected_geom = {
        'U2.16': ((13.1875, 30.95), u2_vset),
        'R102.1': ((13.818252, 33.153649), r102_vset),
        'R102.2': ((14.458252, 33.153649), r102_gnd),
    }
    for name, (want, got) in expected_geom.items():
        if abs(want[0]-got[0]) > 0.001 or abs(want[1]-got[1]) > 0.001:
            raise SystemExit(f'route1q {name} geometry gate failed: {got}')

    vset = board.FindNet('PMIC_VSET2')
    gnd = board.FindNet('GND')
    if vset is None or gnd is None:
        raise SystemExit('route1q net reacquire failed')

    added = 0
    vias = 0
    added += add_track(board, vset, u2_vset, VSET_BEND1, VSET_WIDTH)
    added += add_track(board, vset, VSET_BEND1, VSET_BEND2, VSET_WIDTH)
    added += add_track(board, vset, VSET_BEND2, r102_vset, VSET_WIDTH)
    added += add_track(board, gnd, r102_gnd, GND_VIA, GND_WIDTH)
    vias += add_via(board, gnd, GND_VIA)
    if added != 4 or vias != 1:
        raise SystemExit(f'route1q internal scope gate failed: segments={added} vias={vias}')

    refill_all_zones(board)
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit('route1q SaveBoard failed')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1q report helper missing')
    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
