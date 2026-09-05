#!/usr/bin/env python3
"""r13 route-1c: add the continuous In1.Cu GND reference plane only.

Input is the executed route-1b SW-only board. This stage intentionally adds no
vias and no new signal tracks. Existing all-layer and internal-copper RF
keep-outs remain authoritative and are left untouched. The purpose is to prove
that the continuous inner GND reference itself can be introduced without
breaking the route-1b DRC-clean baseline before any stitching vias are added.

Planning/evidence artifact only; not fabrication authority.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path
import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1b'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1b-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1b-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1b.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1c'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1c-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1c-r13.kicad_pro'
OUT_REPORT = OUT_DIR / 'routing-seed-r13-1c.json'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def iu(v): return int(pcbnew.FromMM(v))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--route1b-drc-json', required=True)
    ap.add_argument('--route1b-pin-net-audit', required=True)
    args = ap.parse_args()

    src_rep = loadj(SRC_REPORT)
    src_sha = sha(SRC_PCB)
    if src_rep.get('output_sha256') != src_sha:
        raise SystemExit('route1b report/PCB SHA mismatch')

    drc = loadj(args.route1b_drc_json)
    audit = loadj(args.route1b_pin_net_audit)
    if len(drc.get('violations', [])) != 0 or len(drc.get('unconnected_items', [])) != 184:
        raise SystemExit('route1b DRC gate failed')
    if audit.get('result') != 'PASS' or audit.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1b pin/net gate failed')

    b = pcbnew.LoadBoard(str(SRC_PCB))
    gnd = b.FindNet('GND')
    if gnd is None:
        raise SystemExit('GND net not found')

    # r10 board datum is 41 x 34 mm: (2.00, 2.75) -> (43.00, 36.75).
    # Use the full outline as the zone boundary. KiCad's zone filler clips copper
    # to board-edge clearance and honors the retained RF keep-out zones.
    z = pcbnew.ZONE(b)
    z.SetNet(gnd)
    z.SetLayer(pcbnew.In1_Cu)
    z.SetZoneName('GND_IN1_CONTINUOUS_R13_1C')
    z.SetLocalClearance(iu(0.20))
    poly = pcbnew.VECTOR_VECTOR2I()
    for x, y in [(2.0, 2.75), (43.0, 2.75), (43.0, 36.75), (2.0, 36.75)]:
        poly.append(pcbnew.VECTOR2I(iu(x), iu(y)))
    z.AddPolygon(poly)
    b.Add(z)

    # Fill in the same KiCad Python runtime before saving so DRC sees current
    # filled copper, not a stale/unfilled zone representation.
    filler = pcbnew.ZONE_FILLER(b)
    zones = pcbnew.ZONES()
    zones.append(z)
    if not filler.Fill(zones):
        raise SystemExit('ZONE_FILLER failed')

    b.SynchronizeNetsAndNetClasses(True)
    b.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), b):
        raise SystemExit('SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO, OUT_PRO)

    all_zones = list(b.Zones())
    gnd_in1 = [q for q in all_zones if q.GetNetname() == 'GND' and q.IsOnLayer(pcbnew.In1_Cu)]
    if len(gnd_in1) != 1:
        raise SystemExit(f'expected exactly one GND In1 zone, got {len(gnd_in1)}')

    out = {
        'revision': 'r13-route1c-in1-gnd-plane',
        'source_route1b_sha256': src_sha,
        'output_sha256': sha(OUT_PCB),
        'zone_name': 'GND_IN1_CONTINUOUS_R13_1C',
        'zone_net': 'GND',
        'zone_layer': 'In1.Cu',
        'board_outline_mm': [[2.0, 2.75], [43.0, 2.75], [43.0, 36.75], [2.0, 36.75]],
        'existing_keepouts_preserved': True,
        'track_segments_added': 0,
        'vias_added': 0,
        'routed_nets_added': [],
        'rf_routing_touched': False,
        'supplier_gated_interfaces_touched': False,
        'routing_status': 'GND_REFERENCE_PLANE_ADDED_NO_STITCHING',
        'validation_status': 'PENDING_EXECUTED_KICAD_DRC',
        'release_status': 'NOT_FOR_GERBER'
    }
    OUT_REPORT.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
