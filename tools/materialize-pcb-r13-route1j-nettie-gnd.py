#!/usr/bin/env python3
"""r13 route-1j: connect NT101/NT102 GND sides to the continuous In1.Cu GND plane.

Source: executed-KiCad-clean route-1i (0 violations / 172 unconnected /
268-node physical audit PASS).

This increment adds only two short F.Cu GND stubs and two deliberate GND
through-vias. The vias penetrate the existing continuous In1.Cu GND zone; the
zone is refilled after insertion. PVSS local copper, switching nodes, RF and
supplier-gated interfaces are untouched.

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
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1i'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1i-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1i-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1i.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1j'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1j-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1j-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1j-report.py'

GND_WIDTH = 0.30
VIA_SIZE = 0.60
VIA_DRILL = 0.30
# Keep the upper GND via above/left of the route-1i PVSS1 In2 trunk. The
# rejected (10.40,25.20) point had only 0.0935 mm clearance to that trunk.
NT101_GND_VIA = (10.35, 25.05)
NT102_GND_VIA = (10.35, 32.05)


def stage(name: str) -> None:
    print(f'[route1j] {name}', flush=True)


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
        raise SystemExit('route1j zone refill failed')


def main():
    stage('start')
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1i-drc-json', required=True)
    ap.add_argument('--route1i-pin-net-audit', required=True)
    args = ap.parse_args()

    rep = loadj(SRC_REPORT)
    srcsha = sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1i report/PCB SHA mismatch')
    d = loadj(args.route1i_drc_json)
    a = loadj(args.route1i_pin_net_audit)
    if len(d.get('violations', [])) != 0 or len(d.get('unconnected_items', [])) != 172:
        raise SystemExit('route1i DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1i pin/net gate failed')
    stage('source gates passed')

    b = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    for ref in ('NT101', 'NT102'):
        if ref not in fps:
            raise SystemExit(f'missing required footprint {ref}')
    nt101, nt102 = fps['NT101'], fps['NT102']

    # route1i rotated NT101, so its GND pad is now physical pad 2 on the left.
    gates = {
        'NT101.1': pads(nt101, '1')[0].GetNetname(),
        'NT101.2': pads(nt101, '2')[0].GetNetname(),
        'NT102.1': pads(nt102, '1')[0].GetNetname(),
        'NT102.2': pads(nt102, '2')[0].GetNetname(),
    }
    expected = {
        'NT101.1': 'PVSS1_LOCAL', 'NT101.2': 'GND',
        'NT102.1': 'PVSS2_LOCAL', 'NT102.2': 'GND',
    }
    if gates != expected:
        raise SystemExit(f'route1j NetTie net gate failed: {gates}')
    if abs(float(nt101.GetOrientationDegrees()) - 180.0) > 0.001:
        raise SystemExit(f'route1j NT101 orientation gate failed: {nt101.GetOrientationDegrees()}')

    nt101_gnd = point(nt101, '2')
    nt102_gnd = point(nt102, '2')
    expected_nt101 = (9.938265, 24.624113)
    expected_nt102 = (9.650627, 32.045243)
    for actual, expected_point, name in (
        (nt101_gnd, expected_nt101, 'NT101.2'),
        (nt102_gnd, expected_nt102, 'NT102.2'),
    ):
        if abs(actual[0]-expected_point[0]) > 0.001 or abs(actual[1]-expected_point[1]) > 0.001:
            raise SystemExit(f'route1j {name} geometry gate failed: {actual}')

    gnd = b.FindNet('GND')
    if gnd is None:
        raise SystemExit('route1j GND net reacquire failed')

    added = 0
    vias = 0
    added += add_track(b, gnd, nt101_gnd, NT101_GND_VIA, GND_WIDTH)
    vias += add_via(b, gnd, NT101_GND_VIA)
    added += add_track(b, gnd, nt102_gnd, NT102_GND_VIA, GND_WIDTH)
    vias += add_via(b, gnd, NT102_GND_VIA)
    if added != 2 or vias != 2:
        raise SystemExit('route1j internal scope gate failed')

    refill_all_zones(b)
    b.SynchronizeNetsAndNetClasses(True)
    b.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), b):
        raise SystemExit('route1j SaveBoard failed')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1j report helper missing')
    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
