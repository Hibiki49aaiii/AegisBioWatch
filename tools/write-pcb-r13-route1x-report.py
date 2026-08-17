#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1w/AegisBioWatch-MainBoard-Route1w-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1w/routing-seed-r13-1w.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1x'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1x-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1x.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1x report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1w report/PCB SHA mismatch in route1x report helper')
    out={
      'revision':'r13-route1x-i2c-pullup-feed-in2-bridge','source_route1w_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':2,'track_width_mm':0.20,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'+1V8_pullup_feed':{'branch_via_mm':[12.684473,34.267766],'trunk_via_mm':[11.45,31.685729],'routing_layer':'In2.Cu','branch_via_location':'midpoint of accepted route-1w R103.1-R104.1 +1V8 segment','trunk_via_location':'on accepted route-1v U2.12-C113.1 +1V8 segment'}},
      'rejected_geometry':[
        {'workflow_run_id':31475815215,'geometry':'F.Cu x=11.60 corridor','rule_violations':2,'reason':'short to accepted C102.2/GND track/via area'},
        {'workflow_run_id':31476339486,'geometry':'F.Cu x=10.25 corridor','rule_violations':2,'reason':'short to accepted route-1j GND via (10.35,32.05)'}
      ],
      'design_rationale':'F.Cu local corridors are blocked by accepted GND vias; use two standard through vias and an otherwise-unused local In2.Cu corridor instead of forcing substandard clearance.',
      'logical_connectivity_added':['R103/R104 local +1V8 pull-up branch -> accepted route-1v +1V8 trunk'],
      'i2c_signal_pads_touched':False,'component_moves':[],'component_rotations':[],
      'accepted_route1w_geometry_modified':False,'ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
