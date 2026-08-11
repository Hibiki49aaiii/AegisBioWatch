#!/usr/bin/env python3
"""Write route-1u metadata in a fresh Python process with no pcbnew/SWIG state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / 'hardware/main-board/pcb/route-r13-1t/AegisBioWatch-MainBoard-Route1t-r13.kicad_pcb'
SRC_REPORT = ROOT / 'hardware/main-board/pcb/route-r13-1t/routing-seed-r13-1t.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1u'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1u-r13.kicad_pcb'
OUT_REPORT = OUT_DIR / 'routing-seed-r13-1u.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1u report inputs missing')
    src = json.loads(SRC_REPORT.read_text())
    srcsha = sha(SRC_PCB)
    if src.get('output_sha256') != srcsha:
        raise SystemExit('route1t report/PCB SHA mismatch in route1u report helper')

    out = {
        'revision': 'r13-route1u-c113-gnd-closure',
        'source_route1t_sha256': srcsha,
        'output_sha256': sha(OUT_PCB),
        'track_segments_added': 1,
        'vias_added': 1,
        'track_width_mm': 0.30,
        'via_size_mm': 0.60,
        'via_drill_mm': 0.30,
        'connections': {
            'C113.2/GND': {
                'pad_mm': [12.885188, 32.399818],
                'gnd_via_mm': [12.70, 33.10],
                'target_reference': 'continuous In1.Cu GND zone',
                'c113_value': '100nF X5R'
            }
        },
        'rejected_geometry': {
            'gnd_via_mm': [12.55, 33.05],
            'clearance_to_R103_2_SYS_I2C_SDA_mm': 0.0668,
            'required_clearance_mm': 0.1000,
            'correction': 'move GND via to (12.70,33.10)'
        },
        'logical_connectivity_added': [
            'C113.2/GND -> continuous In1.Cu GND reference'
        ],
        'c113_1_1v8_status': 'UNCHANGED_PENDING_SEPARATE_VALIDATION',
        'ldo2_in_status': 'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
        'route1n_chg5v_status': 'REJECTED_AND_DEFERRED',
        'component_moves': [],
        'component_rotations': [],
        'accepted_route1t_geometry_modified': False,
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
