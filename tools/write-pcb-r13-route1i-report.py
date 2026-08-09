#!/usr/bin/env python3
"""Write route-1i metadata in a fresh Python process with no pcbnew/SWIG state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / 'hardware/main-board/pcb/route-r13-1h/AegisBioWatch-MainBoard-Route1h-r13.kicad_pcb'
SRC_REPORT = ROOT / 'hardware/main-board/pcb/route-r13-1h/routing-seed-r13-1h.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1i'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1i-r13.kicad_pcb'
OUT_REPORT = OUT_DIR / 'routing-seed-r13-1i.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1i report inputs missing')
    src = json.loads(SRC_REPORT.read_text())
    srcsha = sha(SRC_PCB)
    if src.get('output_sha256') != srcsha:
        raise SystemExit('route1h report/PCB SHA mismatch in route1i report helper')

    out = {
        'revision': 'r13-route1i-pvss-trees',
        'source_route1h_sha256': srcsha,
        'output_sha256': sha(OUT_PCB),
        'track_segments_added': 6,
        'vias_added': 2,
        'via_size_mm': 0.60,
        'via_drill_mm': 0.30,
        'pvss_width_mm': 0.20,
        'component_moves': [],
        'component_rotations': {
            'NT101': {'from_deg': 0.0, 'to_deg': 180.0, 'center_mm': [10.438265, 24.624113]}
        },
        'pvss1_tree': {
            'nodes': ['C107.2', 'NT101.1', 'accepted PVSS1 U2-side via'],
            'nt101_pvss1_pad_after_rotation_mm': [10.938265, 24.624113],
            'nt101_gnd_pad_after_rotation_mm': [9.938265, 24.624113],
            'branch_via_mm': [11.30, 25.20],
            'existing_u2_side_via_mm': [8.25, 27.20],
            'top_points_mm': [
                [11.957553, 23.51711],
                [10.938265, 24.624113],
                [11.30, 25.20]
            ],
            'internal_segment_layer': 'In2.Cu'
        },
        'pvss2_tree': {
            'nodes': ['C108.2', 'NT102.1', 'accepted PVSS2 U2-side via'],
            'branch_via_mm': [7.90, 33.10],
            'existing_u2_side_via_mm': [8.25, 29.30],
            'top_segment': 'C108.2->NT102.1->branch via',
            'internal_segment_layer': 'In2.Cu'
        },
        'logical_connectivity_added': [
            'C107.2<->NT101.1<->PVSS1 accepted loop',
            'C108.2<->NT102.1<->PVSS2 accepted loop'
        ],
        'nettied_gnd_side_connected': False,
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
