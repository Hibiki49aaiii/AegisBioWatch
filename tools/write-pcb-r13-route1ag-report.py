#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1af/AegisBioWatch-MainBoard-Route1af-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1af/routing-seed-r13-1af.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ag'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ag-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1ag.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1ag report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1af report/PCB SHA mismatch in route1ag report helper')
    out={
      'revision':'r13-route1ag-c304-gnd-local','source_route1af_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':1,'track_width_mm':0.30,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'C304.2/GND':{'pad_mm':[16.645,23.725],'gnd_via_mm':[17.25,23.725],'target_reference':'continuous In1.Cu GND zone','c304_value':'100nF','c304_1_net':'VSYS_HAPTIC'}},
      'design_rationale':'Give the VSYS_HAPTIC local decoupling capacitor an independent short standard-rule GND return to the right. This avoids the RF/MCU decoupling region and leaves accepted route1af copper unchanged.',
      'logical_connectivity_added':['C304.2/GND -> continuous In1.Cu GND reference'],
      'vsys_haptic_status':'UNCHANGED_PENDING_SEPARATE_VALIDATION','component_moves':[],'component_rotations':[],
      'accepted_route1af_geometry_modified':False,'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED',
      'ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD','route1n_chg5v_status':'REJECTED_AND_DEFERRED',
      'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,'validation_status':'PENDING_EXECUTED_KICAD_DRC',
      'release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
