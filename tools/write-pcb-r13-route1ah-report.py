#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1ag/AegisBioWatch-MainBoard-Route1ag-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1ag/routing-seed-r13-1ag.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ah'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ah-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1ah.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1ah report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1ag report/PCB SHA mismatch in route1ah report helper')
    out={
      'revision':'r13-route1ah-c305-gnd-local','source_route1ag_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':1,'track_width_mm':0.30,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'C305.2/GND':{'pad_mm':[7.765,22.335],'gnd_via_mm':[8.40,22.335],'target_reference':'continuous In1.Cu GND zone','c305_value':'1uF','c305_1_net':'VSYS_HAPTIC'}},
      'design_rationale':'Give the second VSYS_HAPTIC local decoupling capacitor its own short standard-rule GND return. Conservative all-layer preflight gives about 0.215 mm minimum clearance to the accepted B.Cu VSYS trunk at the proposed via, above the 0.10 mm rule.',
      'logical_connectivity_added':['C305.2/GND -> continuous In1.Cu GND reference'],
      'vsys_haptic_status':'UNCHANGED_PENDING_SEPARATE_VALIDATION','component_moves':[],'component_rotations':[],
      'accepted_route1ag_geometry_modified':False,'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED',
      'ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD','route1n_chg5v_status':'REJECTED_AND_DEFERRED',
      'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,'validation_status':'PENDING_EXECUTED_KICAD_DRC',
      'release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
