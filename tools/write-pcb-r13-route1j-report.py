#!/usr/bin/env python3
"""Write route-1j metadata in a fresh Python process with no pcbnew/SWIG state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / 'hardware/main-board/pcb/route-r13-1i/AegisBioWatch-MainBoard-Route1i-r13.kicad_pcb'
SRC_REPORT = ROOT / 'hardware/main-board/pcb/route-r13-1i/routing-seed-r13-1i.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1j'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1j-r13.kicad_pcb'
OUT_REPORT = OUT_DIR / 'routing-seed-r13-1j.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1j report inputs missing')
    src = json.loads(SRC_REPORT.read_text())
    srcsha = sha(SRC_PCB)
    if src.get('output_sha256') != srcsha:
        raise SystemExit('route1i report/PCB SHA mismatch in route1j report helper')

    out = {
        'revision': 'r13-route1j-nettie-gnd',
        'source_route1i_sha256': srcsha,
        'output_sha256': sha(OUT_PCB),
        'track_segments_added': 2,
        'vias_added': 2,
        'gnd_track_width_mm': 0.30,
        'via_size_mm': 0.60,
        'via_drill_mm': 0.30,
        'connections': {
            'NT101.2/GND': {
                'pad_mm': [9.938265, 24.624113],
                'gnd_via_mm': [10.40, 25.20],
                'target_reference': 'continuous In1.Cu GND zone'
            },
            'NT102.2/GND': {
                'pad_mm': [9.650627, 32.045243],
                'gnd_via_mm': [10.35, 32.05],
                'target_reference': 'continuous In1.Cu GND zone'
            }
        },
        'logical_connectivity_added': [
            'NT101.2/GND -> continuous GND reference',
            'NT102.2/GND -> continuous GND reference'
        ],
        'component_moves': [],
        'component_rotations': [],
        'pvss_local_copper_modified': False,
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
