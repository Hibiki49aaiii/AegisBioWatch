#!/usr/bin/env python3
"""r13 route-1t: connect R106.1/VSYS into the accepted route-1s VSYS network.

Source: executed-KiCad-clean route-1s (0 violations / 156 unconnected /
268-node physical audit PASS).

LDO2_IN remains intentionally untouched because U2.30 is geometrically trapped
between accepted GND/PVSS1 vias. This increment only closes the VSYS side of
optional R106 using one new via and a B.Cu detour to the accepted route-1s VSYS
via at (11.90,24.70). No via-in-pad or clearance waiver is used.
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
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1s'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1s-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1s-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1s.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1t'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1t-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1t-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1t-report.py'

TRACK_WIDTH = 0.30
NEW_VSYS_VIA = (4.65, 25.865834)
BEND1 = (4.65, 23.00)
BEND2 = (11.90, 23.00)
TARGET_VSYS_VIA = (11.90, 24.70)
VIA_SIZE = 0.60
VIA_DRILL = 0.30


def stage(name: str) -> None:
    print(f'[route1t] {name}', flush=True)


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
        if not isinstance(item, pcbnew.PCB_VIA) or item.GetNetname() != 'VSYS':
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
        raise SystemExit('route1t zone refill failed')


def main():
    stage('start')
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1s-drc-json', required=True)
    ap.add_argument('--route1s-pin-net-audit', required=True)
    args = ap.parse_args()

    rep = loadj(SRC_REPORT)
    srcsha = sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1s report/PCB SHA mismatch')
    d = loadj(args.route1s_drc_json)
    a = loadj(args.route1s_pin_net_audit)
    if len(d.get('violations', [])) != 0 or len(d.get('unconnected_items', [])) != 156:
        raise SystemExit('route1s DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1s pin/net gate failed')
    stage('source gates passed')

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    if 'R106' not in fps:
        raise SystemExit('route1t missing R106')
    r106 = fps['R106']
    gates = {
        'R106.1': pads(r106, '1')[0].GetNetname(),
        'R106.2': pads(r106, '2')[0].GetNetname(),
        'R106.value': r106.GetValue(),
    }
    expected = {
        'R106.1': 'VSYS',
        'R106.2': 'LDO2_IN',
        'R106.value': '0R DNP/OPTION',
    }
    if gates != expected:
        raise SystemExit(f'route1t net/value gate failed: {gates}')

    r106_vsys = point(r106, '1')
    want = (5.270826, 25.865834)
    if abs(r106_vsys[0]-want[0]) > 0.001 or abs(r106_vsys[1]-want[1]) > 0.001:
        raise SystemExit(f'route1t R106.1 geometry gate failed: {r106_vsys}')
    if not has_vsys_via(board, TARGET_VSYS_VIA):
        raise SystemExit('route1t accepted route1s VSYS target via missing')

    vsys = board.FindNet('VSYS')
    if vsys is None:
        raise SystemExit('route1t VSYS net reacquire failed')

    added = 0
    vias = 0
    added += add_track(board, vsys, r106_vsys, NEW_VSYS_VIA, TRACK_WIDTH, pcbnew.F_Cu)
    vias += add_via(board, vsys, NEW_VSYS_VIA)
    added += add_track(board, vsys, NEW_VSYS_VIA, BEND1, TRACK_WIDTH, pcbnew.B_Cu)
    added += add_track(board, vsys, BEND1, BEND2, TRACK_WIDTH, pcbnew.B_Cu)
    added += add_track(board, vsys, BEND2, TARGET_VSYS_VIA, TRACK_WIDTH, pcbnew.B_Cu)
    if added != 4 or vias != 1:
        raise SystemExit(f'route1t internal scope gate failed: segments={added} vias={vias}')

    refill_all_zones(board)
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit('route1t SaveBoard failed')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1t report helper missing')
    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
