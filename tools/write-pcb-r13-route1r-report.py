#!/usr/bin/env python3
"""Write route-1r metadata in a fresh Python process with no pcbnew/SWIG state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / 'hardware/main-board/pcb/route-r13-1q/AegisBioWatch-MainBoard-Route1q-r13.kicad_pcb'
SRC_REPORT = ROOT / 'hardware/main-board/pcb/route-r13-1q/routing-seed-r13-1q.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1r'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1r-r13.kicad_pcb'
OUT_REPORT = OUT_DIR / 'routing-seed-r13-1r.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1r report inputs missing')
    src = json.loads(SRC_REPORT.read_text())
    srcsha = sha(SRC_PCB)
    if src.get('output_sha256') != srcsha:
        raise SystemExit('route1q report/PCB SHA mismatch in route1r report helper')

    out = {
        'revision': 'r13-route1r-ldo1in-local-closure',
        'source_route1q_sha256': srcsha,
        'output_sha256': sha(OUT_PCB),
        'track_segments_added': 5,
        'vias_added': 0,
        'track_width_mm': 0.20,
        'connections': {
            'LDO1_IN': {
                'u2_28_mm': [11.6875, 26.05],
                'bend1_mm': [11.6875, 25.70],
                'bend2_mm': [12.00, 25.40],
                'bend3_mm': [13.55, 25.40],
                'bend4_mm': [13.55, 24.750105],
                'r105_2_mm': [13.10307, 24.750105],
                'r105_value': '0R DNP/OPTION'
            }
        },
        'rejected_geometry': {
            'route': 'U2.28 -> (11.6875,25.30) -> (13.55,25.30) -> (13.55,24.750105) -> R105.2',
            'executed_run_id': 31468964539,
            'violations': 2,
            'unconnected_items': 157,
            'actual_clearance_mm': 0.0002,
            'required_clearance_mm': 0.1000,
            'conflict': 'accepted PVSS1_LOCAL via at (11.30,25.20)',
            'correction': 'terminate straight U2.28 escape at y=25.70, then shift right before descending to y=25.40'
        },
        'logical_connectivity_added': [
            'U2.28/LDO1_IN <-> R105.2/LDO1_IN'
        ],
        'r105_vsys_side_status': 'UNCHANGED_PENDING_SEPARATE_VALIDATION',
        'route1n_chg5v_status': 'REJECTED_AND_DEFERRED',
        'component_moves': [],
        'component_rotations': [],
        'accepted_route1q_geometry_modified': False,
        'in1_gnd_plane_preserved_and_refilled': True,
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
