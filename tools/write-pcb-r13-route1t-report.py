#!/usr/bin/env python3
"""Write route-1t metadata in a fresh Python process with no pcbnew/SWIG state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / 'hardware/main-board/pcb/route-r13-1s/AegisBioWatch-MainBoard-Route1s-r13.kicad_pcb'
SRC_REPORT = ROOT / 'hardware/main-board/pcb/route-r13-1s/routing-seed-r13-1s.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1t'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1t-r13.kicad_pcb'
OUT_REPORT = OUT_DIR / 'routing-seed-r13-1t.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1t report inputs missing')
    src = json.loads(SRC_REPORT.read_text())
    srcsha = sha(SRC_PCB)
    if src.get('output_sha256') != srcsha:
        raise SystemExit('route1s report/PCB SHA mismatch in route1t report helper')

    out = {
        'revision': 'r13-route1t-r106-vsys-closure',
        'source_route1s_sha256': srcsha,
        'output_sha256': sha(OUT_PCB),
        'track_segments_added': 4,
        'vias_added': 1,
        'track_width_mm': 0.30,
        'via_size_mm': 0.60,
        'via_drill_mm': 0.30,
        'connections': {
            'R106.1/VSYS': {
                'pad_mm': [5.270826, 25.865834],
                'new_vsys_via_mm': [4.65, 25.865834],
                'b_cu_bend1_mm': [4.65, 23.00],
                'b_cu_bend2_mm': [11.90, 23.00],
                'accepted_route1s_vsys_via_mm': [11.90, 24.70]
            }
        },
        'logical_connectivity_added': [
            'R106.1/VSYS -> accepted route1s VSYS network at existing via (11.90,24.70)'
        ],
        'ldo2_in_status': 'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
        'route1n_chg5v_status': 'REJECTED_AND_DEFERRED',
        'component_moves': [],
        'component_rotations': [],
        'accepted_route1s_geometry_modified': False,
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
