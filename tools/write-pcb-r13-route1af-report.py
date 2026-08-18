#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1ae/AegisBioWatch-MainBoard-Route1ae-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1ae/routing-seed-r13-1ae.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1af'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1af-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1af.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1af report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1ae report/PCB SHA mismatch in route1af report helper')
    out={
      'revision':'r13-route1af-c111-gnd-local','source_route1ae_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':1,'track_width_mm':0.30,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'C111.2/GND':{'pad_mm':[8.654853,20.728837],'gnd_via_mm':[8.654853,19.828837],'target_reference':'continuous In1.Cu GND zone','c111_value':'10uF X5R 25V','c111_1_net':'BIO_SW'}},
      'design_rationale':'Give the second BIO_SW local capacitor an independent short vertical standard-rule GND return. Accepted route1ae geometry leaves a clear corridor below C111.2.',
      'logical_connectivity_added':['C111.2/GND -> continuous In1.Cu GND reference'],
      'bio_sw_status':'UNCHANGED_PENDING_SEPARATE_VALIDATION','component_moves':[],'component_rotations':[],
      'accepted_route1ae_geometry_modified':False,'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED',
      'ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD','route1n_chg5v_status':'REJECTED_AND_DEFERRED',
      'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,'validation_status':'PENDING_EXECUTED_KICAD_DRC',
      'release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
