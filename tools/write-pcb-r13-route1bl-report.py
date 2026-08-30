#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/"hardware/main-board/pcb/route-r13-1bk/AegisBioWatch-MainBoard-Route1bk-r13.kicad_pcb"
SRC_REPORT=ROOT/"hardware/main-board/pcb/route-r13-1bk/routing-seed-r13-1bk.json"
OUT_DIR=ROOT/"hardware/main-board/pcb/route-r13-1bl"
OUT_PCB=OUT_DIR/"AegisBioWatch-MainBoard-Route1bl-r13.kicad_pcb"
OUT_REPORT=OUT_DIR/"routing-seed-r13-1bl.json"

POINTS=[[7.35,28.25],[7.2,28.25],[7.2,26.4],[5.270826,26.4],[5.270826,25.865834]]


def sha256(path: Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main()->None:
    source=json.loads(SRC_REPORT.read_text(encoding="utf-8"))
    source_sha=sha256(SRC_PCB)
    if source.get("output_sha256")!=source_sha:
        raise SystemExit("route1bl report source SHA mismatch")

    out={
        "revision":"r13-route1bl-vsys-r106-option-feed",
        "source_route1bk_sha256":source_sha,
        "output_sha256":sha256(OUT_PCB),
        "track_segments_added":4,
        "vias_added":0,
        "track_width_mm":0.30,
        "segment_lengths_mm":[0.15,1.85,1.929174,0.534166],
        "track_length_mm":4.46334,
        "connections":{
            "accepted VSYS source endpoint to R106.1/VSYS":{
                "path_points_mm":POINTS,
                "source_existing_track_mm":[[8.9875,28.25],[7.35,28.25]],
                "source_existing_track_width_mm":0.30,
                "source_existing_track_modified":False,
                "r106_value":"0R DNP/OPTION",
                "r106_pad1_mm":[5.270826,25.865834],
                "r106_pad1_net":"VSYS",
                "r106_pad2_mm":[5.910826,25.865834],
                "r106_pad2_net":"LDO2_IN",
                "r106_pad2_routing_touched":False,
                "screen_best_clearance_mm":0.184166
            }
        },
        "component_moves":[],
        "component_rotations":[],
        "accepted_route1bk_geometry_modified":False,
        "existing_vsys_source_track_modified":False,
        "r106_ldo2_in_routing_touched":False,
        "rf_routing_touched":False,
        "supplier_gated_interfaces_touched":False,
        "dock_5v_raw_status":"DEFERRED_COORDINATED_POWER_ROUTING",
        "sys_i2c_scl_u2_r104_status":"DEFERRED_GEOMETRY_GATED",
        "ldo2_in_u2_r106_status":"DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD",
        "route1n_chg5v_status":"REJECTED_AND_DEFERRED",
        "validation_status":"PENDING_EXECUTED_KICAD_DRC",
        "release_status":"NOT_FOR_GERBER",
        "report_process":"fresh_python_without_pcbnew"
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))


if __name__=="__main__":
    main()
