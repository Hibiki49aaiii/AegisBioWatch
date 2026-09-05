#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1aq/AegisBioWatch-MainBoard-Route1aq-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1aq/routing-seed-r13-1aq.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ar'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ar-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1ar.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1ar report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha:
        raise SystemExit('route1aq report/PCB SHA mismatch in route1ar report helper')
    out={
      'revision':'r13-route1ar-c3-gnd-local',
      'source_route1aq_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,
      'vias_added':1,
      'track_width_mm':0.30,
      'via_size_mm':0.60,
      'via_drill_mm':0.30,
      'connections':{
        'C3.2/GND':{
          'pad_mm':[41.645,13.475],
          'gnd_via_mm':[42.25,13.475],
          'target_reference':'continuous In1.Cu GND zone',
          'c3_value':'100nF',
          'c3_1_net':'+1V8',
          'c3_2_net':'GND'
        }
      },
      'preflight':{
        'minimum_pessimistic_non_gnd_copper_margin_mm':0.1852,
        'limiting_object':'C3.1/+1V8',
        'via_copper_to_right_edge_mm':0.45,
        'board_right_edge_x_mm':43.0,
        'distance_to_route1aq_gnd_via_center_mm':1.5
      },
      'design_rationale':'Route C3.2/GND toward increasing X directly into the continuous In1.Cu GND reference with one short 0.30 mm F.Cu segment and one standard 0.60/0.30 mm through via at (42.25,13.475). Conservative accepted-route1aq geometry screening gives approximately 0.1852 mm minimum pessimistic non-GND copper margin, limited by C3.1/+1V8; the via copper remains approximately 0.45 mm from the x=43.0 mm board edge and its center is 1.5 mm from the accepted same-net route1aq GND via at (42.25,11.975). RF-adjacent and supplier-gated regions remain untouched. Executed KiCad DRC remains the acceptance authority.',
      'logical_connectivity_added':['C3.2/GND -> continuous In1.Cu GND reference'],
      'c3_signal_pad_status':'UNCHANGED',
      'component_moves':[],
      'component_rotations':[],
      'accepted_route1aq_geometry_modified':False,
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
