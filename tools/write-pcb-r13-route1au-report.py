#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1at/AegisBioWatch-MainBoard-Route1at-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1at/routing-seed-r13-1at.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1au'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1au-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1au.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1au report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha:
        raise SystemExit('route1at report/PCB SHA mismatch in route1au report helper')
    out={
      'revision':'r13-route1au-d102-gnd-local',
      'source_route1at_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,
      'vias_added':1,
      'track_width_mm':0.30,
      'via_size_mm':0.60,
      'via_drill_mm':0.30,
      'connections':{
        'D102.2/GND':{
          'pad_mm':[41.82,10.27],
          'gnd_via_mm':[42.25,10.27],
          'target_reference':'continuous In1.Cu GND zone',
          'd102_value':'PESD5V0S1UL',
          'd102_1_net':'DOCK_5V_RAW',
          'd102_2_net':'GND',
          'd102_1_pad_mm':[41.12,10.27]
        }
      },
      'preflight':{
        'minimum_conservative_non_gnd_copper_gap_mm':0.3500,
        'limiting_object':'D102.1/DOCK_5V_RAW versus the new F.Cu segment',
        'via_to_d102_1_non_gnd_copper_gap_mm':0.6300,
        'track_length_mm':0.430,
        'via_copper_to_board_edge_gap_mm':0.450,
        'via_drill_edge_to_board_edge_gap_mm':0.600,
        'via_copper_to_antenna_keepout_gap_mm':0.970,
        'rf_region':'untouched',
        'supplier_gated_region':'untouched'
      },
      'design_rationale':'D102 is the dock-input 5 V ESD shunt. Close only D102.2/GND with one 0.43 mm horizontal 0.30 mm F.Cu segment to a standard 0.60/0.30 mm through-via at (42.25,10.27), stitching into the continuous In1.Cu GND plane. Conservative preflight gives approximately 0.35 mm minimum non-GND copper gap to D102.1/DOCK_5V_RAW, 0.45 mm via-copper clearance to the board edge, and 0.97 mm to the antenna keepout. D102.1, RF routing, J3/J5/J6 supplier-gated interfaces, and all accepted route1at geometry remain unchanged. Executed KiCad DRC remains acceptance authority.',
      'logical_connectivity_added':['D102.2/GND -> continuous In1.Cu GND reference'],
      'd102_signal_pad_status':'UNCHANGED',
      'component_moves':[],
      'component_rotations':[],
      'accepted_route1at_geometry_modified':False,
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED',
      'ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED',
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
