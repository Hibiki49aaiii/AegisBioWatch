#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1y/AegisBioWatch-MainBoard-Route1y-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1y/routing-seed-r13-1y.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1z'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1z-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1z.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1z report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1y report/PCB SHA mismatch in route1z report helper')
    out={
      'revision':'r13-route1z-c101-gnd-local','source_route1y_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':3,'vias_added':0,'track_width_mm':0.30,
      'connections':{'C101.2/GND':{'pad_mm':[17.141428,28.024501],'bend1_mm':[17.95,28.024501],'bend2_mm':[17.95,30.49],'target_existing_gnd_via_mm':[16.85,30.49]}},
      'design_rationale':'C101.1/CHG_5V is vertically between C101.2/GND and the existing GND via, so route right of the CHG_5V pad before returning to the accepted local GND via.',
      'logical_connectivity_added':['C101.2/GND -> accepted GND via (16.85,30.49)'],
      'chg_5v_status':'UNCHANGED_REJECTED_AND_DEFERRED','i2c_scl_status':'DEFERRED_STANDARD_RULE_CORRIDOR_NOT_DEMONSTRATED',
      'ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD','component_moves':[],'component_rotations':[],
      'accepted_route1y_geometry_modified':False,'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
