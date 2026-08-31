#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/"hardware/main-board/pcb/route-r13-1bm/AegisBioWatch-MainBoard-Route1bm-r13.kicad_pcb"
SRC_REPORT=ROOT/"hardware/main-board/pcb/route-r13-1bm/routing-seed-r13-1bm.json"
OUT_DIR=ROOT/"hardware/main-board/pcb/route-r13-1bn"
OUT_PCB=OUT_DIR/"AegisBioWatch-MainBoard-Route1bn-r13.kicad_pcb"
OUT_REPORT=OUT_DIR/"routing-seed-r13-1bn.json"

POINTS=[[41.005,14.975],[41.005,15.65],[39.6,15.65],[39.6,25.975],[40.255,25.975]]


def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main()->None:
    source=json.loads(SRC_REPORT.read_text(encoding="utf-8"))
    source_sha=sha256(SRC_PCB)
    if source.get("output_sha256")!=source_sha:
        raise SystemExit("route1bn report source SHA mismatch")
    out={
        "revision":"r13-route1bn-r403-1v8-local",
        "issue":20,
        "source_route1bm_sha256":source_sha,
        "output_sha256":sha256(OUT_PCB),
        "track_segments_added":4,
        "vias_added":0,
        "track_width_mm":0.30,
        "segment_lengths_mm":[0.675,1.405,10.325,0.655],
        "track_length_mm":13.06,
        "minimum_conservative_clearance_mm":0.26,
        "connections":{
            "+1V8 source track to R403.1/+1V8":{
                "path_points_mm":POINTS,
                "path_family":"VHVH",
                "source_track_endpoint_mm":[41.005,14.975],
                "source_track_expected_length_mm":4.6628,
                "r403_value":"4.7k PU PROV",
                "r403_pad1_mm":[40.255,25.975],
                "r403_pad1_net":"+1V8",
                "r403_pad2_mm":[40.895,25.975],
                "r403_pad2_net":"SYS_I2C_SDA",
                "co_limiting_unrelated_copper":["R403.2/SYS_I2C_SDA","C4.2/GND"],
                "minimum_conservative_clearance_note":"Both endpoint-adjacent unrelated pads independently limit the documented path at 0.260 mm."
            }
        },
        "component_moves":[],
        "component_rotations":[],
        "accepted_route1bm_geometry_modified":False,
        "source_1v8_track_modified":False,
        "r403_sys_i2c_sda_pad2_routing_touched":False,
        "rf_routing_touched":False,
        "supplier_gated_interfaces_touched":False,
        "design_rule_waiver":False,
        "via_in_pad":False,
        "validation_status":"PENDING_EXECUTED_KICAD_DRC",
        "release_status":"NOT_FOR_GERBER",
        "report_process":"fresh_python_without_pcbnew"
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))


if __name__=="__main__":
    main()
