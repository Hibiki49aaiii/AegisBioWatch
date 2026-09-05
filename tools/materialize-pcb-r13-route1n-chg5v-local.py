#!/usr/bin/env python3
"""r13 route-1n: close U2.21/CHG_5V to the local C101 decoupler.

Source: executed-KiCad-clean route-1m (0 violations / 164 unconnected /
268-node physical audit PASS).

C101 is rotated in place from 90 to 270 degrees so its CHG_5V pad faces U2.21
and its GND pad faces an open return corridor. This increment then adds only:
- U2.21/CHG_5V -> C101.1/CHG_5V on F.Cu
- C101.2/GND -> short F.Cu stub -> through-via -> continuous In1.Cu GND

The remote CHG_5V path through R501/D101 and DOCK_5V_RAW remains deferred.
RF and supplier-gated interfaces are untouched. Planning/evidence artifact only;
not fabrication authority.
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
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1n'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1n-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1n-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1n-report.py'

CHG_WIDTH = 0.40
GND_WIDTH = 0.40
VIA_SIZE = 0.60
VIA_DRILL = 0.30
GND_VIA = (18.25, 29.575)


def stage(name: str) -> None:
    print(f'[route1n] {name}', flush=True)


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
        raise SystemExit('route1n zone refill failed')


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
    for ref in ('U2', 'C101'):
        if ref not in fps:
            raise SystemExit(f'route1n missing {ref}')
    u2 = fps['U2']
    c101 = fps['C101']

    gates = {
        'U2.21': pads(u2, '21')[0].GetNetname(),
        'C101.1': pads(c101, '1')[0].GetNetname(),
        'C101.2': pads(c101, '2')[0].GetNetname(),
    }
    if gates != {'U2.21': 'CHG_5V', 'C101.1': 'CHG_5V', 'C101.2': 'GND'}:
        raise SystemExit(f'route1n net gate failed: {gates}')

    u2_chg = point(u2, '21')
    source_chg = point(c101, '1')
    source_gnd = point(c101, '2')
    if abs(float(c101.GetOrientationDegrees()) - 90.0) > 0.001:
        raise SystemExit(f'route1n source C101 orientation gate failed: {c101.GetOrientationDegrees()}')
    source_expected = {
        'U2.21': ((13.8875, 28.25), u2_chg),
        'C101.1': ((17.141428, 29.574501), source_chg),
        'C101.2': ((17.141428, 28.024501), source_gnd),
    }
    for name, (want, got) in source_expected.items():
        if abs(want[0]-got[0]) > 0.001 or abs(want[1]-got[1]) > 0.001:
            raise SystemExit(f'route1n source {name} geometry gate failed: {got}')

    center_before = (mm(c101.GetPosition().x), mm(c101.GetPosition().y))
    c101.SetOrientationDegrees(270.0)
    center_after = (mm(c101.GetPosition().x), mm(c101.GetPosition().y))
    if abs(center_before[0]-center_after[0]) > 0.001 or abs(center_before[1]-center_after[1]) > 0.001:
        raise SystemExit(f'route1n C101 center moved during rotation: {center_before} -> {center_after}')

    c101_chg = point(c101, '1')
    c101_gnd = point(c101, '2')
    rotated_expected = {
        'C101.1': ((17.141428, 28.024501), c101_chg),
        'C101.2': ((17.141428, 29.574501), c101_gnd),
    }
    for name, (want, got) in rotated_expected.items():
        if abs(want[0]-got[0]) > 0.001 or abs(want[1]-got[1]) > 0.001:
            raise SystemExit(f'route1n rotated {name} geometry gate failed: {got}')
    stage('C101 rotated 90 to 270 degrees in place')

    chg = board.FindNet('CHG_5V')
    gnd = board.FindNet('GND')
    if chg is None or gnd is None:
        raise SystemExit('route1n net reacquire failed')

    added = 0
    vias = 0
    added += add_track(board, chg, u2_chg, c101_chg, CHG_WIDTH)
    added += add_track(board, gnd, c101_gnd, GND_VIA, GND_WIDTH)
    vias += add_via(board, gnd, GND_VIA)
    if added != 2 or vias != 1:
        raise SystemExit(f'route1n internal scope gate failed: segments={added} vias={vias}')

    refill_all_zones(board)
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit('route1n SaveBoard failed')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1n report helper missing')
    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
