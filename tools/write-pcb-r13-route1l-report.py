#!/usr/bin/env python3
"""Write route-1l metadata in a fresh Python process with no pcbnew/SWIG state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / 'hardware/main-board/pcb/route-r13-1k/AegisBioWatch-MainBoard-Route1k-r13.kicad_pcb'
SRC_REPORT = ROOT / 'hardware/main-board/pcb/route-r13-1k/routing-seed-r13-1k.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1l'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1l-r13.kicad_pcb'
OUT_REPORT = OUT_DIR / 'routing-seed-r13-1l.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1l report inputs missing')
    src = json.loads(SRC_REPORT.read_text())
    srcsha = sha(SRC_PCB)
    if src.get('output_sha256') != srcsha:
        raise SystemExit('route1k report/PCB SHA mismatch in route1l helper')

    out = {
        'revision': 'r13-route1l-c102-vsys-bulk-decoupling',
        'source_route1k_sha256': srcsha,
        'output_sha256': sha(OUT_PCB),
        'track_segments_added': 5,
        'vias_added': 3,
        'vsys_track_width_mm': 0.40,
        'gnd_track_width_mm': 0.40,
        'via_size_mm': 0.60,
        'via_drill_mm': 0.30,
        'c102': {
            'value': '10uF 10V X7R 0603',
            'center_mm': [10.218578, 33.302172],
            'vsys_pad_mm': [9.443578, 33.302172],
            'gnd_pad_mm': [10.993578, 33.302172],
            'vsys_entry_via_mm': [9.00, 34.00],
            'vsys_dogleg_mm': [8.20, 32.80],
            'vsys_exit_via_mm': [15.50, 27.57],
            'vsys_crossing_layer': 'B.Cu',
            'vsys_rejoin_node': 'C114.1/VSYS',
            'gnd_via_mm': [11.40, 33.30],
            'gnd_reference': 'continuous In1.Cu GND zone'
        },
        'rejected_geometry': {
            'strategy': 'straight B.Cu entry-to-exit trunk',
            'from_mm': [9.00, 34.00],
            'to_mm': [15.50, 27.57],
            'reason': 'shorted accepted route1j GND via at (10.35,32.05); no waiver used'
        },
        'logical_connectivity_added': [
            'C102.1/VSYS -> accepted C114/U2.20 VSYS island',
            'C102.2/GND -> continuous GND reference'
        ],
        'component_moves': [],
        'component_rotations': [],
        'accepted_pvss_geometry_modified': False,
        'accepted_c114_geometry_modified': False,
        'in1_gnd_plane_preserved_and_refilled': True,
        'vbat_charger_deferred': True,
        'rf_routing_touched': False,
        'supplier_gated_interfaces_touched': False,
        'validation_status': 'PENDING_EXECUTED_KICAD_DRC',
        'release_status': 'NOT_FOR_GERBER',
        'report_process': 'fresh_python_without_pcbnew'
    }
    OUT_REPORT.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
