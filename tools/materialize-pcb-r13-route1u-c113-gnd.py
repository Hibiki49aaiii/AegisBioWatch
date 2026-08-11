#!/usr/bin/env python3
"""r13 route-1u: close C113.2/GND into the continuous In1.Cu GND plane.

Source: executed-KiCad-clean route-1t (0 violations / 155 unconnected /
268-node physical audit PASS).

This increment only connects the GND side of C113 (100 nF X5R) with one short
F.Cu segment and one standard through via. C113.1/+1V8 remains unchanged.
The first via at (12.55,33.05) was rejected after executed DRC measured only
0.0668 mm clearance to R103.2/SYS_I2C_SDA; the via is moved to (12.70,33.10).
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
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1t'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1t-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1t-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1t.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1u'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1u-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1u-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1u-report.py'

TRACK_WIDTH = 0.30
GND_VIA = (12.70, 33.10)
VIA_SIZE = 0.60
VIA_DRILL = 0.30


def stage(name: str) -> None:
    print(f'[route1u] {name}', flush=True)


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


def add_track(board, net, a, b):
    t = pcbnew.PCB_TRACK(board)
    t.SetLayer(pcbnew.F_Cu)
    t.SetNet(net)
    t.SetWidth(iu(TRACK_WIDTH))
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
        raise SystemExit('route1u zone refill failed')


def main():
    stage('start')
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1t-drc-json', required=True)
    ap.add_argument('--route1t-pin-net-audit', required=True)
    args = ap.parse_args()

    rep = loadj(SRC_REPORT)
    srcsha = sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1t report/PCB SHA mismatch')
    d = loadj(args.route1t_drc_json)
    a = loadj(args.route1t_pin_net_audit)
    if len(d.get('violations', [])) != 0 or len(d.get('unconnected_items', [])) != 155:
        raise SystemExit('route1t DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1t pin/net gate failed')
    stage('source gates passed')

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    if 'C113' not in fps:
        raise SystemExit('route1u missing C113')
    c113 = fps['C113']
    gates = {
        'C113.1': pads(c113, '1')[0].GetNetname(),
        'C113.2': pads(c113, '2')[0].GetNetname(),
        'C113.value': c113.GetValue(),
    }
    expected = {
        'C113.1': '+1V8',
        'C113.2': 'GND',
        'C113.value': '100nF X5R',
    }
    if gates != expected:
        raise SystemExit(f'route1u net/value gate failed: {gates}')

    c113_gnd = point(c113, '2')
    want = (12.885188, 32.399818)
    if abs(c113_gnd[0]-want[0]) > 0.001 or abs(c113_gnd[1]-want[1]) > 0.001:
        raise SystemExit(f'route1u C113.2 geometry gate failed: {c113_gnd}')

    gnd = board.FindNet('GND')
    if gnd is None:
        raise SystemExit('route1u GND net reacquire failed')

    added = add_track(board, gnd, c113_gnd, GND_VIA)
    vias = add_via(board, gnd, GND_VIA)
    if added != 1 or vias != 1:
        raise SystemExit(f'route1u internal scope gate failed: segments={added} vias={vias}')

    refill_all_zones(board)
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit('route1u SaveBoard failed')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1u report helper missing')
    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
