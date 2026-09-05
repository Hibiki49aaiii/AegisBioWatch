#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1bf/AegisBioWatch-MainBoard-Route1bf-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1bf/routing-seed-r13-1bf.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bg'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1bg-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1bg.json'
START=[9.255,22.225]; END=[8.964712,24.126353]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1bf report/PCB SHA mismatch in route1bg helper')
    out={
      'revision':'r13-route1bg-c5-l101-1v8-local',
      'source_route1bf_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':0,'track_width_mm':0.30,
      'track_length_mm':round(math.dist(START,END),6),
      'connections':{'C5.1/+1V8 to L101.2/+1V8':{
        'c5_value':'100nF','l101_value':'2.2uH / DCR<400mR',
        'c5_pad1_mm':START,'l101_pad2_mm':END,
        'c5_pad1_net':'+1V8','l101_pad2_net':'+1V8',
        'c5_pad2_mm':[9.895,22.225],'c5_pad2_net':'GND',
        'l101_pad1_mm':[7.514712,24.126353],'l101_pad1_net':'PMIC_SW1',
        'c107_pad1_mm':[10.407553,23.51711],'c107_pad1_net':'+1V8'}},
      'existing_l101_to_c107_rail_status':'UNCHANGED',
      'component_moves':[],'component_rotations':[],
      'accepted_route1bf_geometry_modified':False,
      'c5_gnd_routing_touched':False,'pmic_sw1_routing_touched':False,
      'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED',
      'ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED',
      'validation_status':'PENDING_EXECUTED_KICAD_DRC',
      'release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
