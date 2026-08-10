#!/usr/bin/env python3
"""r13 route-1p: close nPM1300 VSET1 strap and its local GND return.

Source: executed-KiCad-clean route-1o (0 violations / 162 unconnected /
268-node physical audit PASS).

This increment connects only U2.17/PMIC_VSET1 to R101.1 and R101.2/GND to the
existing continuous In1.Cu GND reference. CHG_5V remains deferred after the
rejected route-1n geometry. No RF or supplier-gated interfaces are touched.

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
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1o'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1o-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1o-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1o.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1p'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1p-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1p-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1p-report.py'

VSET_WIDTH = 0.20
GND_WIDTH = 0.30
GND_VIA = (15.70, 32.40)
VIA_SIZE = 0.60
VIA_DRILL = 0.30


def stage(name: str) -> None:
    print(f'[route1p] {name}', flush=True)


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
        raise SystemExit('route1p zone refill failed')


def main():
    stage('start')
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1o-drc-json', required=True)
    ap.add_argument('--route1o-pin-net-audit', required=True)
    args = ap.parse_args()

    rep = loadj(SRC_REPORT)
    srcsha = sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1o report/PCB SHA mismatch')
    d = loadj(args.route1o_drc_json)
    a = loadj(args.route1o_pin_net_audit)
    if len(d.get('violations', [])) != 0 or len(d.get('unconnected_items', [])) != 162:
        raise SystemExit('route1o DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1o pin/net gate failed')
    stage('source gates passed')

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    for ref in ('U2', 'R101'):
        if ref not in fps:
            raise SystemExit(f'route1p missing {ref}')
    u2, r101 = fps['U2'], fps['R101']

    gates = {
        'U2.17': pads(u2, '17')[0].GetNetname(),
        'R101.1': pads(r101, '1')[0].GetNetname(),
        'R101.2': pads(r101, '2')[0].GetNetname(),
    }
    if gates != {'U2.17': 'PMIC_VSET1', 'R101.1': 'PMIC_VSET1', 'R101.2': 'GND'}:
        raise SystemExit(f'route1p net gate failed: {gates}')

    u2_vset = point(u2, '17')
    r101_vset = point(r101, '1')
    r101_gnd = point(r101, '2')
    expected = {
        'U2.17': ((13.8875, 30.25), u2_vset),
        'R101.1': ((13.964027, 32.210297), r101_vset),
        'R101.2': ((14.604027, 32.210297), r101_gnd),
    }
    for name, (want, got) in expected.items():
        if abs(want[0]-got[0]) > 0.001 or abs(want[1]-got[1]) > 0.001:
            raise SystemExit(f'route1p {name} geometry gate failed: {got}')

    vset = board.FindNet('PMIC_VSET1')
    gnd = board.FindNet('GND')
    if vset is None or gnd is None:
        raise SystemExit('route1p net reacquire failed')

    added = 0
    vias = 0
    added += add_track(board, vset, u2_vset, r101_vset, VSET_WIDTH)
    added += add_track(board, gnd, r101_gnd, GND_VIA, GND_WIDTH)
    vias += add_via(board, gnd, GND_VIA)
    if added != 2 or vias != 1:
        raise SystemExit(f'route1p internal scope gate failed: segments={added} vias={vias}')

    refill_all_zones(board)
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit('route1p SaveBoard failed')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1p report helper missing')
    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
