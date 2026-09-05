#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_PCB = ROOT / "hardware/main-board/pcb/route-r13-1bj/AegisBioWatch-MainBoard-Route1bj-r13.kicad_pcb"
SRC_REPORT = ROOT / "hardware/main-board/pcb/route-r13-1bj/routing-seed-r13-1bj.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bk"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bk-r13.kicad_pcb"
OUT_REPORT = OUT_DIR / "routing-seed-r13-1bk.json"

POINTS = [[6.805, 22.335], [6.805, 21.65], [16.005, 21.65], [16.005, 23.725]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = json.loads(SRC_REPORT.read_text(encoding="utf-8"))
    source_sha = sha256(SRC_PCB)
    if source.get("output_sha256") != source_sha:
        raise SystemExit("route1bk report source SHA mismatch")

    out = {
        "revision": "r13-route1bk-c305-c304-vsys-haptic-local",
        "source_route1bj_sha256": source_sha,
        "output_sha256": sha256(OUT_PCB),
        "track_segments_added": 3,
        "vias_added": 0,
        "track_width_mm": 0.30,
        "segment_lengths_mm": [0.685, 9.2, 2.075],
        "track_length_mm": 11.96,
        "connections": {
            "C305.1/VSYS_HAPTIC to C304.1/VSYS_HAPTIC": {
                "c305_value": "1uF",
                "c304_value": "100nF",
                "path_points_mm": POINTS,
                "c305_pad1_mm": [6.805, 22.335],
                "c305_pad1_net": "VSYS_HAPTIC",
                "c305_pad2_mm": [7.765, 22.335],
                "c305_pad2_net": "GND",
                "c304_pad1_mm": [16.005, 23.725],
                "c304_pad1_net": "VSYS_HAPTIC",
                "c304_pad2_mm": [16.645, 23.725],
                "c304_pad2_net": "GND",
                "u4_value": "DRV2605LDGSR",
                "u4_pad10_mm": [23.005, 13.4],
                "u4_pad10_net": "VSYS_HAPTIC",
                "r305_value": "0R / FB OPTION",
                "r305_pad2_mm": [31.315, 18.595],
                "r305_pad2_net": "VSYS_HAPTIC"
            }
        },
        "component_moves": [],
        "component_rotations": [],
        "accepted_route1bj_geometry_modified": False,
        "c305_gnd_routing_touched": False,
        "c304_gnd_routing_touched": False,
        "u4_vdd_routing_touched": False,
        "r305_feed_routing_touched": False,
        "rf_routing_touched": False,
        "supplier_gated_interfaces_touched": False,
        "dock_5v_raw_status": "DEFERRED_COORDINATED_POWER_ROUTING",
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
