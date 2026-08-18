#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1aj/AegisBioWatch-MainBoard-Route1aj-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1aj/routing-seed-r13-1aj.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ak'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ak-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1ak.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1ak report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1aj report/PCB SHA mismatch in route1ak report helper')
    out={
      'revision':'r13-route1ak-q501-gnd-local','source_route1aj_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':1,'track_width_mm':0.30,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'Q501.2/GND':{'pad_mm':[18.6175,19.525],'gnd_via_mm':[17.65,19.525],'target_reference':'continuous In1.Cu GND zone','q501_value':'2N7002-CLASS','q501_1_net':'CHG_SENSE_GATE','q501_3_net':'CHG_PRESENT_N'}},
      'design_rationale':'Give Q501 source/GND a dedicated short standard-rule return. The via is placed left of Q501, away from the nearby nRF DCDC inductor region; conservative preflight geometry found approximately 0.95 mm minimum clearance to any non-GND copper using an intentionally pessimistic pad-radius model.',
      'logical_connectivity_added':['Q501.2/GND -> continuous In1.Cu GND reference'],
      'chg_sense_gate_status':'UNCHANGED_PENDING_SEPARATE_VALIDATION','chg_present_n_status':'UNCHANGED_PENDING_SEPARATE_VALIDATION',
      'component_moves':[],'component_rotations':[],'accepted_route1aj_geometry_modified':False,
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED','ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
