#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / "hardware/main-board/pcb/route-r13-1bg/AegisBioWatch-MainBoard-Route1bg-r13.kicad_pcb"
SRC_REPORT = ROOT / "hardware/main-board/pcb/route-r13-1bg/routing-seed-r13-1bg.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bi"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bi-r13.kicad_pcb"
OUT_REPORT = OUT_DIR / "routing-seed-r13-1bi.json"

POINTS = [[11.08, 4.72], [10.305, 4.72], [10.305, 11.085]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = json.loads(SRC_REPORT.read_text(encoding="utf-8"))
    source_sha = sha256(SRC_PCB)
    if source.get("output_sha256") != source_sha:
        raise SystemExit("route1bi report source SHA mismatch")

    out = {
        "revision": "r13-route1bi-u3-c1-1v8-local",
        "source_route1bg_sha256": source_sha,
        "output_sha256": sha256(OUT_PCB),
        "track_segments_added": 2,
        "vias_added": 0,
        "track_width_mm": 0.30,
        "segment_lengths_mm": [0.775, 6.365],
        "track_length_mm": 7.14,
        "connections": {
            "U3.8/+1V8 to C1.1/+1V8": {
                "u3_value": "W25Q256JWPIQ 256Mbit",
                "c1_value": "10uF",
                "path_points_mm": POINTS,
                "u3_pad8_mm": [11.08, 4.72],
                "u3_pad8_net": "+1V8",
                "u3_pad7_mm": [11.08, 5.99],
                "u3_pad7_net": "FLASH_HOLD_N",
                "u3_pad5_mm": [11.08, 8.53],
                "u3_pad5_net": "AUX_SPI_MOSI",
                "c1_pad1_mm": [10.305, 11.085],
                "c1_pad1_net": "+1V8",
                "c1_pad2_mm": [11.265, 11.085],
                "c1_pad2_net": "GND"
            }
        },
        "component_moves": [],
        "component_rotations": [],
        "accepted_route1bg_geometry_modified": False,
        "u3_signal_routing_touched": False,
        "c1_gnd_routing_touched": False,
        "rf_routing_touched": False,
        "supplier_gated_interfaces_touched": False,
        "sys_i2c_scl_u2_r104_status": "DEFERRED_GEOMETRY_GATED",
        "ldo2_in_status": "DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD",
        "route1n_chg5v_status": "REJECTED_AND_DEFERRED",
        "validation_status": "PENDING_EXECUTED_KICAD_DRC",
        "release_status": "NOT_FOR_GERBER",
        "report_process": "fresh_python_without_pcbnew"
    }
    OUT_REPORT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
