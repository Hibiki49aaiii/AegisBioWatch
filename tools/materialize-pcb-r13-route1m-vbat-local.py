#!/usr/bin/env python3
"""r13 route-1m: close the local U2.19/VBAT to C106 decoupling branch.

Source: executed-KiCad-clean route-1l (0 violations / 166 unconnected /
268-node physical audit PASS).

This increment is intentionally limited to the local VBAT decoupler C106:
- U2.19/VBAT -> C106.1/VBAT on F.Cu
- C106.2/GND -> one short F.Cu stub + through-via into continuous In1.Cu GND

Battery connector, charger input, protection, RF and supplier-gated interfaces
remain deferred. Planning/evidence artifact only; not fabrication authority.
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
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1l'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1l-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1l-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1l.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1m'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1m-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1m-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1m-report.py'

VBAT_WIDTH = 0.40
GND_WIDTH = 0.40
VIA_SIZE = 0.60
VIA_DRILL = 0.30
GND_VIA = (16.35, 30.49)


def stage(name: str) -> None:
    print(f'[route1m] {name}', flush=True)


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
        raise SystemExit('route1m zone refill failed')


def main():
    stage('start')
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1l-drc-json', required=True)
    ap.add_argument('--route1l-pin-net-audit', required=True)
    args = ap.parse_args()

    rep = loadj(SRC_REPORT)
    srcsha = sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1l report/PCB SHA mismatch')
    d = loadj(args.route1l_drc_json)
    a = loadj(args.route1l_pin_net_audit)
    if len(d.get('violations', [])) != 0 or len(d.get('unconnected_items', [])) != 166:
        raise SystemExit('route1l DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1l pin/net gate failed')
    stage('source gates passed')

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    for ref in ('U2', 'C106'):
        if ref not in fps:
            raise SystemExit(f'route1m missing {ref}')
    u2 = fps['U2']
    c106 = fps['C106']

    gates = {
        'U2.19': pads(u2, '19')[0].GetNetname(),
        'C106.1': pads(c106, '1')[0].GetNetname(),
        'C106.2': pads(c106, '2')[0].GetNetname(),
    }
    if gates != {'U2.19': 'VBAT', 'C106.1': 'VBAT', 'C106.2': 'GND'}:
        raise SystemExit(f'route1m net gate failed: {gates}')

    u2_vbat = point(u2, '19')
    c106_vbat = point(c106, '1')
    c106_gnd = point(c106, '2')
    expected = {
        'U2.19': ((13.8875, 29.25), u2_vbat),
        'C106.1': ((15.522674, 28.939978), c106_vbat),
        'C106.2': ((15.522674, 30.489978), c106_gnd),
    }
    for name, (want, got) in expected.items():
        if abs(want[0]-got[0]) > 0.001 or abs(want[1]-got[1]) > 0.001:
            raise SystemExit(f'route1m {name} geometry gate failed: {got}')

    vbat = board.FindNet('VBAT')
    gnd = board.FindNet('GND')
    if vbat is None or gnd is None:
        raise SystemExit('route1m net reacquire failed')

    added = 0
    vias = 0
    added += add_track(board, vbat, u2_vbat, c106_vbat, VBAT_WIDTH)
    added += add_track(board, gnd, c106_gnd, GND_VIA, GND_WIDTH)
    vias += add_via(board, gnd, GND_VIA)
    if added != 2 or vias != 1:
        raise SystemExit(f'route1m internal scope gate failed: segments={added} vias={vias}')

    refill_all_zones(board)
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit('route1m SaveBoard failed')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1m report helper missing')
    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
