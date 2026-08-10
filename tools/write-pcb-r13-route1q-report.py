#!/usr/bin/env python3
"""Write route-1q metadata in a fresh Python process with no pcbnew/SWIG state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / 'hardware/main-board/pcb/route-r13-1p/AegisBioWatch-MainBoard-Route1p-r13.kicad_pcb'
SRC_REPORT = ROOT / 'hardware/main-board/pcb/route-r13-1p/routing-seed-r13-1p.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1q'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1q-r13.kicad_pcb'
OUT_REPORT = OUT_DIR / 'routing-seed-r13-1q.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1q report inputs missing')
    src = json.loads(SRC_REPORT.read_text())
    srcsha = sha(SRC_PCB)
    if src.get('output_sha256') != srcsha:
        raise SystemExit('route1p report/PCB SHA mismatch in route1q report helper')

    out = {
        'revision': 'r13-route1q-vset2-local-strap',
        'source_route1p_sha256': srcsha,
        'output_sha256': sha(OUT_PCB),
        'track_segments_added': 4,
        'vias_added': 1,
        'vset_track_width_mm': 0.20,
        'gnd_track_width_mm': 0.30,
        'via_size_mm': 0.60,
        'via_drill_mm': 0.30,
        'connections': {
            'PMIC_VSET2': {
                'u2_16_mm': [13.1875, 30.95],
                'bend1_mm': [13.30, 31.35],
                'bend2_mm': [13.30, 32.80],
                'r102_1_mm': [13.818252, 33.153649],
                'r102_value': '150k 1%'
            },
            'R102.2/GND': {
                'pad_mm': [14.458252, 33.153649],
                'gnd_via_mm': [15.40, 33.15],
                'target_reference': 'continuous In1.Cu GND zone'
            }
        },
        'logical_connectivity_added': [
            'U2.16/PMIC_VSET2 <-> R102.1/PMIC_VSET2',
            'R102.2/GND -> continuous GND reference'
        ],
        'route1n_chg5v_status': 'REJECTED_AND_DEFERRED',
        'component_moves': [],
        'component_rotations': [],
        'accepted_vset1_vbusout_vbat_vsys_pvss_geometry_modified': False,
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
