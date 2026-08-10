#!/usr/bin/env python3
"""Write route-1k metadata in a fresh Python process with no pcbnew/SWIG state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1j/AegisBioWatch-MainBoard-Route1j-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1j/routing-seed-r13-1j.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1k'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1k-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1k.json'


def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main()->None:
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1k report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256') != srcsha:
        raise SystemExit('route1j report/PCB SHA mismatch in route1k helper')
    out={
      'revision':'r13-route1k-c114-vsys-hf-decoupling',
      'source_route1j_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':3,
      'vias_added':1,
      'vsys_track_width_mm':0.30,
      'gnd_track_width_mm':0.30,
      'via_size_mm':0.60,
      'via_drill_mm':0.30,
      'c114':{
        'value':'100nF HF / APP',
        'vsys_pad_mm':[6.892232,27.030566],
        'gnd_pad_mm':[6.892232,26.390566],
        'vsys_spine_join_points_mm':[[7.35,27.030566],[7.35,28.25]],
        'gnd_via_mm':[7.35,26.39],
        'gnd_reference':'continuous In1.Cu GND zone'
      },
      'logical_connectivity_added':['C114.1/VSYS -> accepted VSYS spine','C114.2/GND -> continuous GND reference'],
      'c102_bulk_vsys_deferred':True,
      'vbat_charger_deferred':True,
      'component_moves':[],
      'component_rotations':[],
      'accepted_pvss_geometry_modified':False,
      'in1_gnd_plane_preserved_and_refilled':True,
      'rf_routing_touched':False,
      'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC',
      'release_status':'NOT_FOR_GERBER',
      'report_process':'fresh_python_without_pcbnew'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':
    main()
