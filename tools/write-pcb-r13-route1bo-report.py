#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/"hardware/main-board/pcb/route-r13-1bn/AegisBioWatch-MainBoard-Route1bn-r13.kicad_pcb"
SRC_REPORT=ROOT/"hardware/main-board/pcb/route-r13-1bn/routing-seed-r13-1bn.json"
OUT_DIR=ROOT/"hardware/main-board/pcb/route-r13-1bo"
OUT_PCB=OUT_DIR/"AegisBioWatch-MainBoard-Route1bo-r13.kicad_pcb"
OUT_REPORT=OUT_DIR/"routing-seed-r13-1bo.json"

POINTS=[[10.305,4.72],[9.7,4.72],[9.7,15.8],[12.105,15.8],[12.105,15.26]]


def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main()->None:
    source=json.loads(SRC_REPORT.read_text(encoding="utf-8"))
    source_sha=sha256(SRC_PCB)
    if source.get("output_sha256")!=source_sha:
        raise SystemExit("route1bo report source SHA mismatch")
    out={
        "revision":"r13-route1bo-j8-1v8-local",
        "issue":21,
        "source_route1bn_sha256":source_sha,
        "output_sha256":sha256(OUT_PCB),
        "track_segments_added":4,
        "vias_added":0,
        "track_width_mm":0.30,
        "segment_lengths_mm":[0.605,11.08,2.405,0.54],
        "track_length_mm":14.63,
        "minimum_conservative_clearance_mm":0.4897,
        "connections":{
            "+1V8 source track to J8.1/+1V8":{
                "path_points_mm":POINTS,
                "path_family":"HVHV",
                "source_track_endpoint_mm":[10.305,4.72],
                "source_track_expected_length_mm":6.365,
                "j8_value":"TC2030_SWD_6",
                "j8_pad1_mm":[12.105,15.26],
                "j8_pad1_net":"+1V8",
                "nearest_unrelated_copper":"J8 numberless NPTH at 10.835,14.625",
                "minimum_conservative_clearance_mm":0.4897
            }
        },
        "component_moves":[],
        "component_rotations":[],
        "accepted_route1bn_geometry_modified":False,
        "source_1v8_track_modified":False,
        "j8_numberless_npth_modified":False,
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
