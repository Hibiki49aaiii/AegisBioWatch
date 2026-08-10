#!/usr/bin/env python3
"""r13 route-1o: close U2.22/VBUSOUT_SENSE to the local C105 decoupler.

Source: executed-KiCad-clean route-1m (0 violations / 164 unconnected /
268-node physical audit PASS).

route-1n CHG_5V was rejected because the accepted VSYS barrier blocks a safe
local escape. route-1o therefore advances an independent local node instead:
- U2.22/VBUSOUT_SENSE -> left-side dogleg -> C105.1 on F.Cu
- C105.2/GND -> short F.Cu stub -> through-via -> continuous In1.Cu GND

No component moves or rotations. The route stays left of the accepted route1k
VSYS barrier and away from the C114 GND via. RF and supplier-gated interfaces
remain untouched. Planning/evidence artifact only; not fabrication authority.
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
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1m'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1m-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1m-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1m.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1o'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1o-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1o-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1o-report.py'

SENSE_WIDTH = 0.30
GND_WIDTH = 0.30
VIA_SIZE = 0.60
VIA_DRILL = 0.30
ESCAPE_X = 14.10
GND_VIA = (17.70, 25.38)


def stage(name: str) -> None:
    print(f'[route1o] {name}', flush=True)


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
        raise SystemExit('route1o zone refill failed')


def main():
    stage('start')
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1m-drc-json', required=True)
    ap.add_argument('--route1m-pin-net-audit', required=True)
    args = ap.parse_args()

    rep = loadj(SRC_REPORT)
    srcsha = sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1m report/PCB SHA mismatch')
    d = loadj(args.route1m_drc_json)
    a = loadj(args.route1m_pin_net_audit)
    if len(d.get('violations', [])) != 0 or len(d.get('unconnected_items', [])) != 164:
        raise SystemExit('route1m DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1m pin/net gate failed')
    stage('source gates passed')

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    for ref in ('U2', 'C105'):
        if ref not in fps:
            raise SystemExit(f'route1o missing {ref}')
    u2 = fps['U2']
    c105 = fps['C105']

    gates = {
        'U2.22': pads(u2, '22')[0].GetNetname(),
        'C105.1': pads(c105, '1')[0].GetNetname(),
        'C105.2': pads(c105, '2')[0].GetNetname(),
    }
    if gates != {'U2.22': 'VBUSOUT_SENSE', 'C105.1': 'VBUSOUT_SENSE', 'C105.2': 'GND'}:
        raise SystemExit(f'route1o net gate failed: {gates}')

    u2_sense = point(u2, '22')
    c105_sense = point(c105, '1')
    c105_gnd = point(c105, '2')
    expected = {
        'U2.22': ((13.8875, 27.75), u2_sense),
        'C105.1': ((15.410102, 25.381239), c105_sense),
        'C105.2': ((16.960102, 25.381239), c105_gnd),
    }
    for name, (want, got) in expected.items():
        if abs(want[0]-got[0]) > 0.001 or abs(want[1]-got[1]) > 0.001:
            raise SystemExit(f'route1o {name} geometry gate failed: {got}')

    sense = board.FindNet('VBUSOUT_SENSE')
    gnd = board.FindNet('GND')
    if sense is None or gnd is None:
        raise SystemExit('route1o net reacquire failed')

    added = 0
    vias = 0
    p1 = (ESCAPE_X, u2_sense[1])
    p2 = (ESCAPE_X, c105_sense[1])
    added += add_track(board, sense, u2_sense, p1, SENSE_WIDTH)
    added += add_track(board, sense, p1, p2, SENSE_WIDTH)
    added += add_track(board, sense, p2, c105_sense, SENSE_WIDTH)
    added += add_track(board, gnd, c105_gnd, GND_VIA, GND_WIDTH)
    vias += add_via(board, gnd, GND_VIA)
    if added != 4 or vias != 1:
        raise SystemExit(f'route1o internal scope gate failed: segments={added} vias={vias}')

    refill_all_zones(board)
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit('route1o SaveBoard failed')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1o report helper missing')
    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
