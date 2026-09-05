#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/"hardware/main-board/pcb/route-r13-1bl/AegisBioWatch-MainBoard-Route1bl-r13.kicad_pcb"
SRC_REPORT=ROOT/"hardware/main-board/pcb/route-r13-1bl/routing-seed-r13-1bl.json"
OUT_DIR=ROOT/"hardware/main-board/pcb/route-r13-1bm"
OUT_PCB=OUT_DIR/"AegisBioWatch-MainBoard-Route1bm-r13.kicad_pcb"
OUT_REPORT=OUT_DIR/"routing-seed-r13-1bm.json"

POINTS=[[31.315,18.595],[31.315,17.5],[25.0,17.5],[25.0,13.4],[23.005,13.4]]


def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main()->None:
    source=json.loads(SRC_REPORT.read_text(encoding="utf-8"))
    source_sha=sha256(SRC_PCB)
    if source.get("output_sha256")!=source_sha:
        raise SystemExit("route1bm report source SHA mismatch")

    out={
        "revision":"r13-route1bm-r305-u4-vsys-haptic-local",
        "issue":19,
        "source_route1bl_sha256":source_sha,
        "output_sha256":sha256(OUT_PCB),
        "track_segments_added":4,
        "vias_added":0,
        "track_width_mm":0.30,
        "segment_lengths_mm":[1.095,6.315,4.1,1.995],
        "track_length_mm":13.505,
        "minimum_conservative_clearance_mm":0.20,
        "connections":{
            "R305.2/VSYS_HAPTIC to U4.10/VSYS_HAPTIC":{
                "path_points_mm":POINTS,
                "path_family":"VHVH",
                "r305_value":"0R / FB OPTION",
                "r305_pad1_mm":[30.295,18.595],
                "r305_pad1_net":"VSYS",
                "r305_pad2_mm":[31.315,18.595],
                "r305_pad2_net":"VSYS_HAPTIC",
                "u4_value":"DRV2605LDGSR",
                "u4_pad10_mm":[23.005,13.4],
                "u4_pad10_net":"VSYS_HAPTIC",
                "nearest_unrelated_copper":"U4.9/HAPTIC_OUT_N",
                "accepted_route1bk_bypass_geometry_modified":False,
            }
        },
        "component_moves":[],
        "component_rotations":[],
        "accepted_route1bl_geometry_modified":False,
        "accepted_route1bk_bypass_geometry_modified":False,
        "r305_vsys_pad1_routing_touched":False,
        "u4_other_pads_routing_touched":False,
        "rf_routing_touched":False,
        "supplier_gated_interfaces_touched":False,
        "design_rule_waiver":False,
        "via_in_pad":False,
        "dock_5v_raw_status":"DEFERRED_COORDINATED_POWER_ROUTING",
        "sys_i2c_scl_u2_r104_status":"DEFERRED_GEOMETRY_GATED",
        "ldo2_in_status":"DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD",
        "chg_5v_status":"DEFERRED",
        "validation_status":"PENDING_EXECUTED_KICAD_DRC",
        "release_status":"NOT_FOR_GERBER",
        "report_process":"fresh_python_without_pcbnew",
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))


if __name__=="__main__":
    main()
