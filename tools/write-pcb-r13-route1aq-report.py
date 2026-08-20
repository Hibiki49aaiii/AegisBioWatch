#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1ap/AegisBioWatch-MainBoard-Route1ap-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1ap/routing-seed-r13-1ap.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1aq'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1aq-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1aq.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1aq report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha:
        raise SystemExit('route1ap report/PCB SHA mismatch in route1aq report helper')
    out={
      'revision':'r13-route1aq-c2-gnd-local',
      'source_route1ap_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,
      'vias_added':1,
      'track_width_mm':0.30,
      'via_size_mm':0.60,
      'via_drill_mm':0.30,
      'connections':{
        'C2.2/GND':{
          'pad_mm':[41.645,11.975],
          'gnd_via_mm':[42.25,11.975],
          'target_reference':'continuous In1.Cu GND zone',
          'c2_value':'100nF',
          'c2_1_net':'+1V8',
          'c2_2_net':'GND'
        }
      },
      'preflight':{
        'minimum_pessimistic_non_gnd_copper_margin_mm':0.1852,
        'limiting_object':'C2.1/+1V8',
        'via_copper_to_right_edge_mm':0.45,
        'board_right_edge_x_mm':43.0,
        'in1_filled_right_boundary_x_mm_at_candidate_y':42.7995,
        'via_copper_inside_in1_filled_boundary_mm':0.2495
      },
      'design_rationale':'Route C2.2/GND toward increasing X directly into the continuous In1.Cu GND reference with one short 0.30 mm F.Cu segment and one standard 0.60/0.30 mm through via at (42.25,11.975). Conservative accepted-route1ap geometry screening gives approximately 0.1852 mm minimum pessimistic non-GND copper margin, limited by C2.1/+1V8; the via copper remains approximately 0.45 mm from the x=43.0 mm board edge and approximately 0.2495 mm inside the accepted In1.Cu filled-plane right boundary at this Y. RF-adjacent C7/C8/C9-C12/C401 and PMIC-constrained R502 remain deferred. Executed KiCad DRC remains the acceptance authority.',
      'logical_connectivity_added':['C2.2/GND -> continuous In1.Cu GND reference'],
      'c2_signal_pad_status':'UNCHANGED',
      'component_moves':[],
      'component_rotations':[],
      'accepted_route1ap_geometry_modified':False,
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
