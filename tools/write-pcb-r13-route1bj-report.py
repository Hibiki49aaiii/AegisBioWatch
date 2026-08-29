#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / "hardware/main-board/pcb/route-r13-1bi/AegisBioWatch-MainBoard-Route1bi-r13.kicad_pcb"
SRC_REPORT = ROOT / "hardware/main-board/pcb/route-r13-1bi/routing-seed-r13-1bi.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bj"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bj-r13.kicad_pcb"
OUT_REPORT = OUT_DIR / "routing-seed-r13-1bj.json"

POINTS = [[15.755, 26.725], [15.755, 26.2], [20.255, 26.2], [20.255, 25.975]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = json.loads(SRC_REPORT.read_text(encoding="utf-8"))
    source_sha = sha256(SRC_PCB)
    if source.get("output_sha256") != source_sha:
        raise SystemExit("route1bj report source SHA mismatch")

    out = {
        "revision": "r13-route1bj-r404-r302-1v8-local",
        "source_route1bi_sha256": source_sha,
        "output_sha256": sha256(OUT_PCB),
        "track_segments_added": 3,
        "vias_added": 0,
        "track_width_mm": 0.30,
        "segment_lengths_mm": [0.525, 4.5, 0.225],
        "track_length_mm": 5.25,
        "connections": {
            "R404.1/+1V8 to R302.1/+1V8": {
                "r404_value": "4.7k PU PROV",
                "r302_value": "47k PU",
                "path_points_mm": POINTS,
                "r404_pad1_mm": [15.755, 26.725],
                "r404_pad1_net": "+1V8",
                "r404_pad2_mm": [16.395, 26.725],
                "r404_pad2_net": "SYS_I2C_SCL",
                "r302_pad1_mm": [20.255, 25.975],
                "r302_pad1_net": "+1V8",
                "r302_pad2_mm": [20.895, 25.975],
                "r302_pad2_net": "FLASH_HOLD_N",
                "nearest_r501_pad1_mm": [18.005, 26.725],
                "nearest_r501_pad1_net": "CHG_5V"
            }
        },
        "component_moves": [],
        "component_rotations": [],
        "accepted_route1bi_geometry_modified": False,
        "r404_signal_routing_touched": False,
        "r302_signal_routing_touched": False,
        "chg_5v_routing_touched": False,
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
