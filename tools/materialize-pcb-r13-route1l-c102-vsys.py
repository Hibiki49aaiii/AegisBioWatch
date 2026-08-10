#!/usr/bin/env python3
"""r13 route-1l: close the C102 10 uF bulk VSYS decoupling branch.

Source: executed-KiCad-clean route-1k (0 violations / 168 unconnected /
268-node physical audit PASS).

This increment keeps C102 in place. Its VSYS side enters B.Cu through a local
via, runs upward/right through two B.Cu doglegs that clear the accepted PVSS2
and GND vias, then rejoins the accepted C114/U2.20 VSYS island through a second
via. C102 GND uses one short F.Cu stub and one through-via into the continuous
In1.Cu GND plane. Earlier straight/left-dogleg B.Cu paths remain rejected
negative evidence; no waiver is used.

VBAT/charger, RF and supplier-gated interfaces remain deferred.
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
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1k'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1k-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1k-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1k.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1l'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1l-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1l-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1l-report.py'

VSYS_WIDTH = 0.40
GND_WIDTH = 0.40
VIA_SIZE = 0.60
VIA_DRILL = 0.30
VSYS_ENTRY_VIA = (9.00, 34.00)
VSYS_DOGLEG_A = (11.00, 35.00)
VSYS_DOGLEG_B = (16.20, 31.00)
VSYS_EXIT_VIA = (15.50, 27.57)
GND_VIA = (11.40, 33.30)


def stage(name: str) -> None:
    print(f'[route1l] {name}', flush=True)


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


def refill_all_zones(board):
    zs = pcbnew.ZONES()
    for z in board.Zones():
        zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs):
        raise SystemExit('route1l zone refill failed')


def main():
    stage('start')
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1k-drc-json', required=True)
    ap.add_argument('--route1k-pin-net-audit', required=True)
    args = ap.parse_args()

    rep = loadj(SRC_REPORT)
    srcsha = sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1k report/PCB SHA mismatch')
    d = loadj(args.route1k_drc_json)
    a = loadj(args.route1k_pin_net_audit)
    if len(d.get('violations', [])) != 0 or len(d.get('unconnected_items', [])) != 168:
        raise SystemExit('route1k DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1k pin/net gate failed')
    stage('source gates passed')

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    for ref in ('C102', 'C114'):
        if ref not in fps:
            raise SystemExit(f'route1l missing {ref}')
    c102 = fps['C102']
    c114 = fps['C114']

    gates = {
        'C102.1': pads(c102, '1')[0].GetNetname(),
        'C102.2': pads(c102, '2')[0].GetNetname(),
        'C114.1': pads(c114, '1')[0].GetNetname(),
    }
    if gates != {'C102.1': 'VSYS', 'C102.2': 'GND', 'C114.1': 'VSYS'}:
        raise SystemExit(f'route1l net gate failed: {gates}')

    c102_vsys = point(c102, '1')
    c102_gnd = point(c102, '2')
    c114_vsys = point(c114, '1')
    expected = {
        'C102.1': ((9.443578, 33.302172), c102_vsys),
        'C102.2': ((10.993578, 33.302172), c102_gnd),
        'C114.1': ((14.90, 27.57), c114_vsys),
    }
    for name, (want, got) in expected.items():
        if abs(want[0]-got[0]) > 0.001 or abs(want[1]-got[1]) > 0.001:
            raise SystemExit(f'route1l {name} geometry gate failed: {got}')

    vsys = board.FindNet('VSYS')
    gnd = board.FindNet('GND')
    if vsys is None or gnd is None:
        raise SystemExit('route1l net reacquire failed')

    added = 0
    vias = 0
    added += add_track(board, vsys, c102_vsys, VSYS_ENTRY_VIA, VSYS_WIDTH, pcbnew.F_Cu)
    vias += add_via(board, vsys, VSYS_ENTRY_VIA)
    added += add_track(board, vsys, VSYS_ENTRY_VIA, VSYS_DOGLEG_A, VSYS_WIDTH, pcbnew.B_Cu)
    added += add_track(board, vsys, VSYS_DOGLEG_A, VSYS_DOGLEG_B, VSYS_WIDTH, pcbnew.B_Cu)
    added += add_track(board, vsys, VSYS_DOGLEG_B, VSYS_EXIT_VIA, VSYS_WIDTH, pcbnew.B_Cu)
    vias += add_via(board, vsys, VSYS_EXIT_VIA)
    added += add_track(board, vsys, VSYS_EXIT_VIA, c114_vsys, VSYS_WIDTH, pcbnew.F_Cu)

    added += add_track(board, gnd, c102_gnd, GND_VIA, GND_WIDTH, pcbnew.F_Cu)
    vias += add_via(board, gnd, GND_VIA)

    if added != 6 or vias != 3:
        raise SystemExit(f'route1l internal scope gate failed: segments={added} vias={vias}')

    refill_all_zones(board)
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit('route1l SaveBoard failed')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1l report helper missing')
    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
