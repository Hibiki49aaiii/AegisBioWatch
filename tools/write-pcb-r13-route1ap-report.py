#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1ao/AegisBioWatch-MainBoard-Route1ao-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1ao/routing-seed-r13-1ao.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ap'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ap-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1ap.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1ap report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha:
        raise SystemExit('route1ao report/PCB SHA mismatch in route1ap report helper')
    out={
      'revision':'r13-route1ap-c13-gnd-local',
      'source_route1ao_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,
      'vias_added':1,
      'track_width_mm':0.30,
      'via_size_mm':0.60,
      'via_drill_mm':0.30,
      'connections':{
        'C13.2/GND':{
          'pad_mm':[40.895,22.975],
          'gnd_via_mm':[41.55,22.975],
          'target_reference':'continuous In1.Cu GND zone',
          'c13_value':'3.9pF',
          'c13_1_net':'NRF_RESET_RAW',
          'c13_2_net':'GND'
        }
      },
      'preflight':{
        'minimum_pessimistic_non_gnd_copper_margin_mm':0.1852,
        'limiting_object':'C13.1/NRF_RESET_RAW',
        'via_copper_to_right_edge_mm':1.15,
        'board_right_edge_x_mm':43.0
      },
      'design_rationale':'Route C13.2/GND toward increasing X directly into the continuous In1.Cu GND reference with one short 0.30 mm F.Cu segment and one standard 0.60/0.30 mm through via at (41.55,22.975). Conservative accepted-route1ao geometry screening gives approximately 0.1852 mm minimum pessimistic non-GND copper margin, limited by C13.1/NRF_RESET_RAW, and approximately 1.15 mm via-copper clearance to the x=43.0 mm board edge. C8 was excluded because its opposite pad is NRF_DECA_RF; R303/R304 were excluded for RF matching-region proximity; R502 was excluded for PMIC/LDO2 constraint-region proximity. Executed KiCad DRC remains the acceptance authority.',
      'logical_connectivity_added':['C13.2/GND -> continuous In1.Cu GND reference'],
      'c13_signal_pad_status':'UNCHANGED',
      'component_moves':[],
      'component_rotations':[],
      'accepted_route1ao_geometry_modified':False,
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
