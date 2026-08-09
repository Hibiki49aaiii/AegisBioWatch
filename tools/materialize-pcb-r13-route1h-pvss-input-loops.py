#!/usr/bin/env python3
"""r13 route-1h: co-design PMIC input-return geometry and route PVSS input loops.

This stage starts from the executed-KiCad-clean route-1g baseline. The existing
C103/C104 placement leaves the SW1/SW2 and PVSS endpoint ordering reversed on
F.Cu, so a planar top-only connection would force crossings. Route-1h keeps the
SW nodes on F.Cu, shifts C103/C104 left to open controlled escape channels,
moves the low-current VOUT2 sense trunk from In2.Cu to B.Cu, and uses In2.Cu
for the two short local PVSS input-return crossings.

Scope in this increment:
  * move C103 and C104 only;
  * replace route-1g SW1/SW2/VSYS local F.Cu geometry;
  * move the existing +3V0 VOUT2 sense trunk In2.Cu -> B.Cu without changing
    its endpoints or logical connectivity;
  * connect U2.2 <-> C103.2 (PVSS1_LOCAL);
  * connect U2.6 <-> C104.2 (PVSS2_LOCAL);
  * preserve the continuous In1.Cu GND zone and refill it around new vias.

NT101/NT102, C107.2/C108.2 and NetTie-to-GND completion are intentionally
left for later increments. No RF or supplier-gated interface is touched.

Planning/evidence artifact only; not fabrication authority.
"""
from __future__ import annotations

import argparse
import faulthandler
import hashlib
import json
import shutil
from pathlib import Path

import pcbnew  # type: ignore

faulthandler.enable()

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1g'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1g-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1g-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1g.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1h'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1h-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1h-r13.kicad_pro'
OUT_REPORT = OUT_DIR / 'routing-seed-r13-1h.json'

SW_WIDTH = 0.20
VSYS_WIDTH = 0.30
PVSS_WIDTH = 0.20
VIA_SIZE = 0.60
VIA_DRILL = 0.30

# Preserve Y/orientation; shift only X to open SW/VSYS/PVSS channels.
C103_X = 6.35
C104_X = 4.55
SW_ESCAPE_X = 7.72
VSYS_ESCAPE_X = 7.35
SW2_TURN_Y = 30.65

PVSS1_U2_VIA = (8.25, 27.20)
PVSS2_U2_VIA = (8.25, 29.30)
PVSS1_CAP_VIA_X = 5.55
PVSS2_CAP_VIA_X = 3.75
PVSS1_IN2_BEND_X = 6.30
PVSS2_IN2_BEND_1_X = 6.00
PVSS2_IN2_BEND_2_X = 4.50


def stage(name: str) -> None:
    print(f'[route1h] {name}', flush=True)


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
        raise SystemExit('zone refill failed')


def main():
    stage('start')
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1g-drc-json', required=True)
    ap.add_argument('--route1g-pin-net-audit', required=True)
    args = ap.parse_args()

    rep = loadj(SRC_REPORT)
    srcsha = sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1g report/PCB SHA mismatch')
    d = loadj(args.route1g_drc_json)
    a = loadj(args.route1g_pin_net_audit)
    if len(d.get('violations', [])) != 0 or len(d.get('unconnected_items', [])) != 178:
        raise SystemExit('route1g DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1g pin/net gate failed')
    stage('source gates passed')

    b = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    for ref in ('U2', 'L101', 'L102', 'C103', 'C104'):
        if ref not in fps:
            raise SystemExit(f'missing required footprint {ref}')

    u2 = fps['U2']
    l101 = fps['L101']
    l102 = fps['L102']
    c103 = fps['C103']
    c104 = fps['C104']
    stage('board loaded')

    # Gate the exact local nets before moving anything.
    gates = {
        'U2.2': pads(u2, '2')[0].GetNetname(),
        'U2.3': pads(u2, '3')[0].GetNetname(),
        'U2.4': pads(u2, '4')[0].GetNetname(),
        'U2.5': pads(u2, '5')[0].GetNetname(),
        'U2.6': pads(u2, '6')[0].GetNetname(),
        'L101.1': pads(l101, '1')[0].GetNetname(),
        'L102.1': pads(l102, '1')[0].GetNetname(),
        'C103.1': pads(c103, '1')[0].GetNetname(),
        'C103.2': pads(c103, '2')[0].GetNetname(),
        'C104.1': pads(c104, '1')[0].GetNetname(),
        'C104.2': pads(c104, '2')[0].GetNetname(),
    }
    expected = {
        'U2.2': 'PVSS1_LOCAL', 'U2.3': 'PMIC_SW1', 'U2.4': 'VSYS',
        'U2.5': 'PMIC_SW2', 'U2.6': 'PVSS2_LOCAL',
        'L101.1': 'PMIC_SW1', 'L102.1': 'PMIC_SW2',
        'C103.1': 'VSYS', 'C103.2': 'PVSS1_LOCAL',
        'C104.1': 'VSYS', 'C104.2': 'PVSS2_LOCAL',
    }
    if gates != expected:
        raise SystemExit(f'critical local-net gate failed: {gates}')
    stage('local net gates passed')

    original_positions = {
        'C103': [mm(c103.GetPosition().x), mm(c103.GetPosition().y)],
        'C104': [mm(c104.GetPosition().x), mm(c104.GetPosition().y)],
    }
    c103_y = original_positions['C103'][1]
    c104_y = original_positions['C104'][1]
    c103.SetPosition(pcbnew.VECTOR2I(iu(C103_X), iu(c103_y)))
    c104.SetPosition(pcbnew.VECTOR2I(iu(C104_X), iu(c104_y)))
    stage('C103/C104 moved')

    # Resolve all post-move endpoints before removing controlled tracks.
    u2_p2 = point(u2, '2')
    u2_p3 = point(u2, '3')
    u2_p4 = point(u2, '4')
    u2_p5 = point(u2, '5')
    u2_p6 = point(u2, '6')
    l101_p1 = point(l101, '1')
    l102_p1 = point(l102, '1')
    c103_p1 = point(c103, '1')
    c103_p2 = point(c103, '2')
    c104_p1 = point(c104, '1')
    c104_p2 = point(c104, '2')
    stage('post-move endpoints resolved')

    # Remove only route-1g controlled local F.Cu geometry plus the single
    # route-1e VOUT2 sense trunk on In2.Cu. Existing +1V8/+3V0 power paths,
    # F.Cu sense stubs and the two sense vias remain untouched.
    removed = []
    for item in list(b.GetTracks()):
        if not isinstance(item, pcbnew.PCB_TRACK) or isinstance(item, pcbnew.PCB_VIA):
            continue
        nn = item.GetNetname()
        layer = item.GetLayer()
        if layer == pcbnew.F_Cu and nn in {'PMIC_SW1', 'PMIC_SW2', 'VSYS'}:
            removed.append((nn, 'F.Cu'))
            b.Remove(item)
        elif layer == pcbnew.In2_Cu and nn == '+3V0':
            removed.append((nn, 'In2.Cu'))
            b.Remove(item)
    stage('controlled tracks removed')

    counts = {}
    for key in removed:
        counts[key] = counts.get(key, 0) + 1
    expected_counts = {
        ('PMIC_SW1', 'F.Cu'): 2,
        ('PMIC_SW2', 'F.Cu'): 4,
        ('VSYS', 'F.Cu'): 4,
        ('+3V0', 'In2.Cu'): 1,
    }
    if counts != expected_counts:
        raise SystemExit(f'unexpected controlled-track removal counts: {counts}')

    n_sw1 = b.FindNet('PMIC_SW1')
    n_sw2 = b.FindNet('PMIC_SW2')
    n_vsys = b.FindNet('VSYS')
    n_pvss1 = b.FindNet('PVSS1_LOCAL')
    n_pvss2 = b.FindNet('PVSS2_LOCAL')
    n_3v0 = b.FindNet('+3V0')
    if any(n is None for n in (n_sw1, n_sw2, n_vsys, n_pvss1, n_pvss2, n_3v0)):
        raise SystemExit('required net reacquire failed')
    stage('nets reacquired')

    added = 0

    # SW1: long horizontal escape first, then a near-vertical climb to L101.1.
    sw1_escape = (SW_ESCAPE_X, u2_p3[1])
    added += add_track(b, n_sw1, u2_p3, sw1_escape, SW_WIDTH, pcbnew.F_Cu)
    added += add_track(b, n_sw1, sw1_escape, l101_p1, SW_WIDTH, pcbnew.F_Cu)

    # SW2: same X escape channel, then down to the accepted lower dogleg.
    sw2_escape = (SW_ESCAPE_X, u2_p5[1])
    sw2_turn = (SW_ESCAPE_X, SW2_TURN_Y)
    sw2_pre_l = (l102_p1[0], SW2_TURN_Y)
    added += add_track(b, n_sw2, u2_p5, sw2_escape, SW_WIDTH, pcbnew.F_Cu)
    added += add_track(b, n_sw2, sw2_escape, sw2_turn, SW_WIDTH, pcbnew.F_Cu)
    added += add_track(b, n_sw2, sw2_turn, sw2_pre_l, SW_WIDTH, pcbnew.F_Cu)
    added += add_track(b, n_sw2, sw2_pre_l, l102_p1, SW_WIDTH, pcbnew.F_Cu)

    # VSYS remains a top-copper spine between the two input capacitors, but the
    # vertical channel is shifted left of the SW turn channel.
    vsys_escape = (VSYS_ESCAPE_X, u2_p4[1])
    vsys_turn = (VSYS_ESCAPE_X, c103_p1[1])
    added += add_track(b, n_vsys, u2_p4, vsys_escape, VSYS_WIDTH, pcbnew.F_Cu)
    added += add_track(b, n_vsys, vsys_escape, vsys_turn, VSYS_WIDTH, pcbnew.F_Cu)
    added += add_track(b, n_vsys, vsys_turn, c103_p1, VSYS_WIDTH, pcbnew.F_Cu)
    added += add_track(b, n_vsys, c103_p1, c104_p1, VSYS_WIDTH, pcbnew.F_Cu)
    stage('SW/VSYS replacement tracks added')

    # Keep the existing VOUT2 sense endpoints/vias but free In2.Cu for local
    # PVSS returns by moving only the low-current trunk to B.Cu.
    sense_top = (9.62, 25.30)
    sense_out = (4.80, 33.828194)
    added += add_track(b, n_3v0, sense_top, sense_out, 0.20, pcbnew.B_Cu)
    stage('VOUT2 sense trunk moved to B.Cu')

    # PVSS1 local input return: short F.Cu stubs to two vias, then In2.Cu.
    pvss1_cap_via = (PVSS1_CAP_VIA_X, c103_p2[1])
    pvss1_bend = (PVSS1_IN2_BEND_X, PVSS1_U2_VIA[1])
    vias_added = 0
    added += add_track(b, n_pvss1, u2_p2, PVSS1_U2_VIA, PVSS_WIDTH, pcbnew.F_Cu)
    vias_added += add_via(b, n_pvss1, PVSS1_U2_VIA)
    added += add_track(b, n_pvss1, PVSS1_U2_VIA, pvss1_bend, PVSS_WIDTH, pcbnew.In2_Cu)
    added += add_track(b, n_pvss1, pvss1_bend, pvss1_cap_via, PVSS_WIDTH, pcbnew.In2_Cu)
    vias_added += add_via(b, n_pvss1, pvss1_cap_via)
    added += add_track(b, n_pvss1, pvss1_cap_via, c103_p2, PVSS_WIDTH, pcbnew.F_Cu)
    stage('PVSS1 local loop added')

    # PVSS2 local input return uses a lower In2 corridor and exits left of C104.
    pvss2_cap_via = (PVSS2_CAP_VIA_X, c104_p2[1])
    pvss2_b1 = (PVSS2_IN2_BEND_1_X, PVSS2_U2_VIA[1])
    pvss2_b2 = (PVSS2_IN2_BEND_2_X, PVSS2_U2_VIA[1])
    added += add_track(b, n_pvss2, u2_p6, PVSS2_U2_VIA, PVSS_WIDTH, pcbnew.F_Cu)
    vias_added += add_via(b, n_pvss2, PVSS2_U2_VIA)
    added += add_track(b, n_pvss2, PVSS2_U2_VIA, pvss2_b1, PVSS_WIDTH, pcbnew.In2_Cu)
    added += add_track(b, n_pvss2, pvss2_b1, pvss2_b2, PVSS_WIDTH, pcbnew.In2_Cu)
    added += add_track(b, n_pvss2, pvss2_b2, pvss2_cap_via, PVSS_WIDTH, pcbnew.In2_Cu)
    vias_added += add_via(b, n_pvss2, pvss2_cap_via)
    added += add_track(b, n_pvss2, pvss2_cap_via, c104_p2, PVSS_WIDTH, pcbnew.F_Cu)
    stage('PVSS2 local loop added')

    stage('refill zones begin')
    refill_all_zones(b)
    stage('refill zones done')
    stage('synchronize nets begin')
    b.SynchronizeNetsAndNetClasses(True)
    stage('synchronize nets done')
    stage('build connectivity begin')
    b.BuildConnectivity()
    stage('build connectivity done')

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    stage('save board begin')
    if not pcbnew.SaveBoard(str(OUT_PCB), b):
        raise SystemExit('SaveBoard failed')
    stage('save board done')
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)

    out = {
        'revision': 'r13-route1h-pvss-input-loops',
        'source_route1g_sha256': srcsha,
        'output_sha256': sha(OUT_PCB),
        'moved_footprints': {
            'C103': {'from_mm': original_positions['C103'], 'to_mm': [C103_X, c103_y]},
            'C104': {'from_mm': original_positions['C104'], 'to_mm': [C104_X, c104_y]},
        },
        'track_segments_removed': len(removed),
        'removed_by_net_layer': {f'{k[0]}@{k[1]}': v for k, v in sorted(counts.items())},
        'track_segments_added': added,
        'vias_added': vias_added,
        'via_size_mm': VIA_SIZE,
        'via_drill_mm': VIA_DRILL,
        'sw_width_mm': SW_WIDTH,
        'vsys_width_mm': VSYS_WIDTH,
        'pvss_width_mm': PVSS_WIDTH,
        'vout2_sense_trunk_layer': 'B.Cu',
        'pvss1_points_mm': [u2_p2, PVSS1_U2_VIA, pvss1_bend, pvss1_cap_via, c103_p2],
        'pvss2_points_mm': [u2_p6, PVSS2_U2_VIA, pvss2_b1, pvss2_b2, pvss2_cap_via, c104_p2],
        'logical_connectivity_added': ['U2.2<->C103.2', 'U2.6<->C104.2'],
        'deferred_same_net_nodes': ['C107.2', 'NT101.1', 'C108.2', 'NT102.1'],
        'in1_gnd_plane_preserved_and_refilled': True,
        'rf_routing_touched': False,
        'supplier_gated_interfaces_touched': False,
        'validation_status': 'PENDING_EXECUTED_KICAD_DRC',
        'release_status': 'NOT_FOR_GERBER',
    }
    OUT_REPORT.write_text(json.dumps(out, indent=2) + '\n')
    stage('report written')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
