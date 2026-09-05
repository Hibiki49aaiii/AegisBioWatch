#!/usr/bin/env python3
"""r13 route-1i: extend accepted PVSS local loops to output caps and NetTies.

Source: executed-KiCad-clean route-1h (0 violations / 176 unconnected /
268-node physical audit PASS).

The route-1h NT101 orientation leaves its PVSS1 pad on the side opposite C107,
forcing any Top-copper return to wrap around the NetTie GND pad and nearby
power circuitry. Route-1i therefore rotates NT101 in place by 180 degrees so
PVSS1_LOCAL faces C107.2. This yields a short C107.2->NT101.1 Top-copper path,
then branches through one deliberate via to the accepted PVSS1 U2-side loop.
NT102 already has the correct orientation and is left unchanged.

NetTie GND-side pads remain deferred for route-1j. No other component moves,
no RF routing and no supplier-gated interfaces.
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
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1h'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1h-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1h-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1h.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1i'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1i-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1i-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1i-report.py'

PVSS_WIDTH = 0.20
VIA_SIZE = 0.60
VIA_DRILL = 0.30
PVSS1_EXISTING_VIA = (8.25, 27.20)
PVSS2_EXISTING_VIA = (8.25, 29.30)
PVSS1_BRANCH_VIA = (11.30, 25.20)
PVSS2_BRANCH_VIA = (7.90, 33.10)


def stage(name: str) -> None:
    print(f'[route1i] {name}', flush=True)


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
        raise SystemExit('route1i zone refill failed')


def has_via(board, netname: str, p: tuple[float, float], tol: float = 0.01) -> bool:
    for item in board.GetTracks():
        if not isinstance(item, pcbnew.PCB_VIA) or item.GetNetname() != netname:
            continue
        q = item.GetPosition()
        if abs(mm(q.x) - p[0]) <= tol and abs(mm(q.y) - p[1]) <= tol:
            return True
    return False


def near(a: float, b: float, tol: float = 0.001) -> bool:
    return abs(a - b) <= tol


def main():
    stage('start')
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1h-drc-json', required=True)
    ap.add_argument('--route1h-pin-net-audit', required=True)
    args = ap.parse_args()

    rep = loadj(SRC_REPORT)
    srcsha = sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1h report/PCB SHA mismatch')
    d = loadj(args.route1h_drc_json)
    a = loadj(args.route1h_pin_net_audit)
    if len(d.get('violations', [])) != 0 or len(d.get('unconnected_items', [])) != 176:
        raise SystemExit('route1h DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1h pin/net gate failed')
    stage('source gates passed')

    b = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    for ref in ('C107', 'C108', 'NT101', 'NT102'):
        if ref not in fps:
            raise SystemExit(f'missing required footprint {ref}')

    c107 = fps['C107']
    c108 = fps['C108']
    nt101 = fps['NT101']
    nt102 = fps['NT102']

    gates = {
        'C107.2': pads(c107, '2')[0].GetNetname(),
        'NT101.1': pads(nt101, '1')[0].GetNetname(),
        'NT101.2': pads(nt101, '2')[0].GetNetname(),
        'C108.2': pads(c108, '2')[0].GetNetname(),
        'NT102.1': pads(nt102, '1')[0].GetNetname(),
        'NT102.2': pads(nt102, '2')[0].GetNetname(),
    }
    expected = {
        'C107.2': 'PVSS1_LOCAL', 'NT101.1': 'PVSS1_LOCAL', 'NT101.2': 'GND',
        'C108.2': 'PVSS2_LOCAL', 'NT102.1': 'PVSS2_LOCAL', 'NT102.2': 'GND',
    }
    if gates != expected:
        raise SystemExit(f'route1i critical-net gate failed: {gates}')
    if not has_via(b, 'PVSS1_LOCAL', PVSS1_EXISTING_VIA):
        raise SystemExit('route1i missing accepted PVSS1 U2-side via')
    if not has_via(b, 'PVSS2_LOCAL', PVSS2_EXISTING_VIA):
        raise SystemExit('route1i missing accepted PVSS2 U2-side via')
    if not near(float(nt101.GetOrientationDegrees()), 0.0):
        raise SystemExit(f'route1i NT101 source-orientation gate failed: {nt101.GetOrientationDegrees()}')
    stage('net, via and NT101 orientation gates passed')

    # Rotate only NT101 in place. KiCad 9 exposes SetOrientationDegrees on
    # FOOTPRINT; pad numbers/nets remain unchanged while their physical sides
    # swap, putting PVSS1_LOCAL toward C107 and GND toward the PMIC/plane side.
    nt101.SetOrientationDegrees(180.0)
    if not near(float(nt101.GetOrientationDegrees()), 180.0):
        raise SystemExit('route1i NT101 rotation failed')
    stage('NT101 rotated 180 degrees in place')

    c107_p2 = point(c107, '2')
    nt101_p1 = point(nt101, '1')
    nt101_p2 = point(nt101, '2')
    c108_p2 = point(c108, '2')
    nt102_p1 = point(nt102, '1')

    # Rotation must physically swap the two NetTie sides without moving center.
    if not (near(nt101_p1[0], 10.938265) and near(nt101_p2[0], 9.938265)):
        raise SystemExit(f'route1i NT101 rotated-pad geometry gate failed: p1={nt101_p1} p2={nt101_p2}')

    n1 = b.FindNet('PVSS1_LOCAL')
    n2 = b.FindNet('PVSS2_LOCAL')
    if n1 is None or n2 is None:
        raise SystemExit('route1i net reacquire failed')

    added = 0
    vias_added = 0

    # PVSS1: short Top-copper output-cap return into the now-facing NetTie pad;
    # a second short Top segment reaches a clear branch via, then In2.Cu joins
    # the already-accepted U2/C103 PVSS1 loop.
    added += add_track(b, n1, c107_p2, nt101_p1, PVSS_WIDTH, pcbnew.F_Cu)
    added += add_track(b, n1, nt101_p1, PVSS1_BRANCH_VIA, PVSS_WIDTH, pcbnew.F_Cu)
    vias_added += add_via(b, n1, PVSS1_BRANCH_VIA)
    added += add_track(b, n1, PVSS1_BRANCH_VIA, PVSS1_EXISTING_VIA, PVSS_WIDTH, pcbnew.In2_Cu)

    # PVSS2 already has the favorable C108->local-pad ordering; retain it.
    added += add_track(b, n2, c108_p2, nt102_p1, PVSS_WIDTH, pcbnew.F_Cu)
    added += add_track(b, n2, nt102_p1, PVSS2_BRANCH_VIA, PVSS_WIDTH, pcbnew.F_Cu)
    vias_added += add_via(b, n2, PVSS2_BRANCH_VIA)
    added += add_track(b, n2, PVSS2_BRANCH_VIA, PVSS2_EXISTING_VIA, PVSS_WIDTH, pcbnew.In2_Cu)

    if added != 6 or vias_added != 2:
        raise SystemExit(f'route1i internal scope gate failed: segments={added} vias={vias_added}')

    refill_all_zones(b)
    b.SynchronizeNetsAndNetClasses(True)
    b.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), b):
        raise SystemExit('route1i SaveBoard failed')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1i report helper missing')
    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
