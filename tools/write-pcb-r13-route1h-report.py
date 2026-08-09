#!/usr/bin/env python3
"""Finalize route-1h geometry, then write metadata outside pcbnew/SWIG state."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / 'hardware/main-board/pcb/route-r13-1g/AegisBioWatch-MainBoard-Route1g-r13.kicad_pcb'
SRC_REPORT = ROOT / 'hardware/main-board/pcb/route-r13-1g/routing-seed-r13-1g.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1h'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1h-r13.kicad_pcb'
OUT_REPORT = OUT_DIR / 'routing-seed-r13-1h.json'
POSTPROCESS = ROOT / 'tools/postprocess-pcb-r13-route1h-pvss1-via.py'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1h report inputs missing')
    if not POSTPROCESS.is_file():
        raise SystemExit('route1h PVSS1-via postprocessor missing')

    src = json.loads(SRC_REPORT.read_text())
    srcsha = sha(SRC_PCB)
    if src.get('output_sha256') != srcsha:
        raise SystemExit('route1g report/PCB SHA mismatch in report helper')

    # Run the focused KiCad edit in its own process. That process deliberately
    # exits immediately after SaveBoard, so this report process never imports
    # pcbnew and remains insulated from KiCad 9 SWIG teardown instability.
    subprocess.run([sys.executable, str(POSTPROCESS)], check=True)

    out = {
        'revision': 'r13-route1h-pvss-input-loops',
        'source_route1g_sha256': srcsha,
        'output_sha256': sha(OUT_PCB),
        'moved_footprints': {
            'C103': {'from_mm': [6.84638, 29.040584], 'to_mm': [6.35, 29.040584]},
            'C104': {'from_mm': [5.094124, 28.977213], 'to_mm': [4.82, 28.977213]},
        },
        'track_segments_removed': 11,
        'removed_by_net_layer': {
            '+3V0@In2.Cu': 1,
            'PMIC_SW1@F.Cu': 2,
            'PMIC_SW2@F.Cu': 4,
            'VSYS@F.Cu': 4,
        },
        'track_segments_added': 20,
        'vias_added': 4,
        'via_size_mm': 0.60,
        'via_drill_mm': 0.30,
        'sw_width_mm': 0.20,
        'vsys_width_mm': 0.30,
        'pvss_width_mm': 0.20,
        'vout2_sense_trunk_layer': 'B.Cu',
        'vout2_sense_points_mm': [
            [9.62, 25.30],
            [9.62, 31.00],
            [4.80, 33.828194],
        ],
        'pvss1_points_mm': [
            [8.9875, 27.25],
            [8.25, 27.20],
            [6.30, 27.20],
            [5.55, 27.55],
            [6.35, 28.265584],
        ],
        'pvss2_points_mm': [
            [8.9875, 29.25],
            [8.25, 29.30],
            [4.50, 29.30],
            [3.75, 28.202213],
            [4.82, 28.202213],
        ],
        'logical_connectivity_added': ['U2.2<->C103.2', 'U2.6<->C104.2'],
        'deferred_same_net_nodes': ['C107.2', 'NT101.1', 'C108.2', 'NT102.1'],
        'in1_gnd_plane_preserved_and_refilled': True,
        'rf_routing_touched': False,
        'supplier_gated_interfaces_touched': False,
        'validation_status': 'PENDING_EXECUTED_KICAD_DRC',
        'release_status': 'NOT_FOR_GERBER',
        'report_process': 'fresh_python_without_pcbnew_after_focused_postprocess',
    }
    OUT_REPORT.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
