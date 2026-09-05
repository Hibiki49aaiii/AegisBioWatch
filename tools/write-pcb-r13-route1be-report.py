#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1bd/AegisBioWatch-MainBoard-Route1bd-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1bd/routing-seed-r13-1bd.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1be'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1be-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1be.json'
START=[41.005,14.975]; END=[40.305,19.585]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1be report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha:
        raise SystemExit('route1bd report/PCB SHA mismatch in route1be report helper')
    out={
      'revision':'r13-route1be-c4-c302-1v8-local',
      'source_route1bd_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':0,'track_width_mm':0.30,
      'track_length_mm':round(math.dist(START,END),6),
      'connections':{'C4.1/+1V8 to C302.1/+1V8':{
        'c4_value':'100nF','c302_value':'1uF',
        'c4_pad1_mm':START,'c302_pad1_mm':END,
        'c4_pad1_net':'+1V8','c302_pad1_net':'+1V8',
        'c4_pad2_mm':[41.645,14.975],'c302_pad2_mm':[41.265,19.585],
        'c4_pad2_net':'GND','c302_pad2_net':'GND'}},
      'phase_a_probe':{
        'workflow_run_id':33240365333,'job_id':99068549793,'artifact_id':9711188488,
        'artifact_digest':'sha256:8473817094d4dcb0709a5556c344456420a494287c8b5fbdd84929cc8481bdc4',
        'route_option':'A_SINGLE_DIRECT_FCU_DIAGONAL'},
      'preserved_gnd_escapes':{
        'C4.2_to_via':[[41.645,14.975],[42.25,14.975]],
        'C302.2_to_via':[[41.265,19.585],[41.90,19.585]]},
      'design_rationale':'Phase-A executed probe measured C302.1 at (40.305,19.585) and found no intervening F.Cu track in the direct corridor. Add one direct diagonal 0.30 mm F.Cu +1V8 segment from C4.1 to C302.1, with no vias or placement changes.',
      'logical_connectivity_added':['C4.1/+1V8 -> C302.1/+1V8'],
      'component_moves':[],'component_rotations':[],'accepted_route1bd_geometry_modified':False,
      'c4_gnd_escape_status':'UNCHANGED','c302_gnd_escape_status':'UNCHANGED',
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED','ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__': main()
