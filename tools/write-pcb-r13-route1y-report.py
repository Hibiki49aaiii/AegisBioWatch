#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1x/AegisBioWatch-MainBoard-Route1x-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1x/routing-seed-r13-1x.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1y'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1y-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1y.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1y report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1x report/PCB SHA mismatch in route1y report helper')
    out={
      'revision':'r13-route1y-i2c-sda-local','source_route1x_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':5,'vias_added':2,'track_width_mm':0.20,'via_size_mm':0.45,'via_drill_mm':0.20,
      'connections':{'SYS_I2C_SDA':{'u2_13_mm':[11.6875,30.95],'fcu_p1_mm':[11.6875,31.48],'fcu_p2_mm':[11.80,31.56],'start_via_mm':[12.50,31.80],'end_via_mm':[12.05,33.45],'r103_2_mm':[12.214871,33.583282]}},
      'logical_connectivity_added':['U2.13/SYS_I2C_SDA <-> R103.2/SYS_I2C_SDA'],
      'route1x_pullup_geometry_modified':False,'i2c_scl_touched':False,'component_moves':[],'component_rotations':[],
      'ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD','route1n_chg5v_status':'REJECTED_AND_DEFERRED',
      'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
