#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1v/AegisBioWatch-MainBoard-Route1v-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1v/routing-seed-r13-1v.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1w'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1w-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1w.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1w report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1v report/PCB SHA mismatch in route1w report helper')
    out={
      'revision':'r13-route1w-i2c-pullup-1v8-local','source_route1v_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':0,'track_width_mm':0.20,
      'connections':{'+1V8_pullup_local':{'r103_1_mm':[12.214871,34.223282],'r104_1_mm':[13.154075,34.312249]}},
      'logical_connectivity_added':['R103.1/+1V8 <-> R104.1/+1V8'],
      'i2c_signal_pads_touched':False,'component_moves':[],'component_rotations':[],
      'accepted_route1v_geometry_modified':False,'ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
