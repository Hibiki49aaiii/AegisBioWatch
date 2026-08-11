#!/usr/bin/env python3
"""r13 route-1r: connect nPM1300 LDO1_IN to R105.2.

Source: executed-KiCad-clean route-1q (0 violations / 158 unconnected /
268-node physical audit PASS).

Only the LDO1_IN side of optional R105 is routed in this increment. R105.1/VSYS
is deliberately left unchanged until this local escape is proven clean. The
five-segment dogleg exits U2.28 outward, shifts right before the accepted
PVSS1 via at (11.30,25.20), then approaches R105.2 from the right.

The first executed candidate using y=25.30 directly above the PVSS1 via was
rejected by KiCad with two 0.0002 mm actual-clearance violations.

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
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1q'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1q-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1q-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1q.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1r'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1r-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1r-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1r-report.py'

TRACK_WIDTH = 0.20
BEND1 = (11.6875, 25.70)
BEND2 = (12.00, 25.40)
BEND3 = (13.55, 25.40)
BEND4 = (13.55, 24.750105)


def stage(name: str) -> None:
    print(f'[route1r] {name}', flush=True)


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


def refill_all_zones(board):
    zs = pcbnew.ZONES()
    for z in board.Zones():
        zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs):
        raise SystemExit('route1r zone refill failed')


def main():
    stage('start')
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1q-drc-json', required=True)
    ap.add_argument('--route1q-pin-net-audit', required=True)
    args = ap.parse_args()

    rep = loadj(SRC_REPORT)
    srcsha = sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1q report/PCB SHA mismatch')
    d = loadj(args.route1q_drc_json)
    a = loadj(args.route1q_pin_net_audit)
    if len(d.get('violations', [])) != 0 or len(d.get('unconnected_items', [])) != 158:
        raise SystemExit('route1q DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1q pin/net gate failed')
    stage('source gates passed')

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    for ref in ('U2', 'R105'):
        if ref not in fps:
            raise SystemExit(f'route1r missing {ref}')
    u2, r105 = fps['U2'], fps['R105']

    gates = {
        'U2.28': pads(u2, '28')[0].GetNetname(),
        'R105.1': pads(r105, '1')[0].GetNetname(),
        'R105.2': pads(r105, '2')[0].GetNetname(),
        'R105.value': r105.GetValue(),
    }
    expected = {
        'U2.28': 'LDO1_IN',
        'R105.1': 'VSYS',
        'R105.2': 'LDO1_IN',
        'R105.value': '0R DNP/OPTION',
    }
    if gates != expected:
        raise SystemExit(f'route1r net/value gate failed: {gates}')

    u2_ldo1 = point(u2, '28')
    r105_vsys = point(r105, '1')
    r105_ldo1 = point(r105, '2')
    expected_geom = {
        'U2.28': ((11.6875, 26.05), u2_ldo1),
        'R105.1': ((12.46307, 24.750105), r105_vsys),
        'R105.2': ((13.10307, 24.750105), r105_ldo1),
    }
    for name, (want, got) in expected_geom.items():
        if abs(want[0]-got[0]) > 0.001 or abs(want[1]-got[1]) > 0.001:
            raise SystemExit(f'route1r {name} geometry gate failed: {got}')

    ldo1 = board.FindNet('LDO1_IN')
    if ldo1 is None:
        raise SystemExit('route1r LDO1_IN net reacquire failed')

    added = 0
    added += add_track(board, ldo1, u2_ldo1, BEND1, TRACK_WIDTH)
    added += add_track(board, ldo1, BEND1, BEND2, TRACK_WIDTH)
    added += add_track(board, ldo1, BEND2, BEND3, TRACK_WIDTH)
    added += add_track(board, ldo1, BEND3, BEND4, TRACK_WIDTH)
    added += add_track(board, ldo1, BEND4, r105_ldo1, TRACK_WIDTH)
    if added != 5:
        raise SystemExit(f'route1r internal scope gate failed: segments={added}')

    refill_all_zones(board)
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit('route1r SaveBoard failed')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1r report helper missing')
    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
