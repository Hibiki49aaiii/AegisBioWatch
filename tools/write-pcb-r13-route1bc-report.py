#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1bb/AegisBioWatch-MainBoard-Route1bb-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1bb/routing-seed-r13-1bb.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bc'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1bc-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1bc.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1bc report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha:
        raise SystemExit('route1bb report/PCB SHA mismatch in route1bc report helper')
    out={
      'revision':'r13-route1bc-c2-c3-1v8-local',
      'source_route1bb_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':0,'track_width_mm':0.30,'track_length_mm':1.500,
      'connections':{'C2.1/+1V8 to C3.1/+1V8':{
        'c2_value':'100nF','c3_value':'100nF',
        'c2_pad1_mm':[41.005,11.975],'c3_pad1_mm':[41.005,13.475],
        'c2_pad1_net':'+1V8','c3_pad1_net':'+1V8',
        'c2_pad2_mm':[41.645,11.975],'c3_pad2_mm':[41.645,13.475],
        'c2_pad2_net':'GND','c3_pad2_net':'GND'}},
      'preflight':{
        'conservative_lateral_gap_to_adjacent_gnd_pad_column_mm':0.260,
        'minimum_clearance_rule_mm':0.100,
        'candidate_basis':'straight same-net 1.5 mm edge connection; executed KiCad DRC is authoritative',
        'rf_routing_touched':False,'supplier_gated_region':'untouched'},
      'design_rationale':'Add only one direct 1.500 mm vertical 0.30 mm F.Cu +1V8 segment from C2.1 at (41.005,11.975) to C3.1 at (41.005,13.475). No via is used. The adjacent C2.2/C3.2 GND pad column begins about 0.260 mm beyond the proposed track copper edge under a conservative rectangular estimate, but executed KiCad DRC remains the acceptance authority.',
      'logical_connectivity_added':['C2.1/+1V8 -> C3.1/+1V8'],
      'component_moves':[],'component_rotations':[],'accepted_route1bb_geometry_modified':False,
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED','ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__': main()
