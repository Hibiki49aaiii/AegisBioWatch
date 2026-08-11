#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1u/AegisBioWatch-MainBoard-Route1u-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1u/routing-seed-r13-1u.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1v'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1v-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1v.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1v report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1u report/PCB SHA mismatch in route1v report helper')
    out={
      'revision':'r13-route1v-c113-1v8-closure','source_route1u_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':0,'track_width_mm':0.20,
      'connections':{'+1V8':{'u2_12_mm':[11.1875,30.95],'c113_1_mm':[12.245188,32.399818],'c113_value':'100nF X5R'}},
      'logical_connectivity_added':['U2.12/+1V8 <-> C113.1/+1V8'],
      'component_moves':[],'component_rotations':[],'accepted_route1u_geometry_modified':False,
      'ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD','route1n_chg5v_status':'REJECTED_AND_DEFERRED',
      'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__': main()
