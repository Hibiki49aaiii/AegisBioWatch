#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1al/AegisBioWatch-MainBoard-Route1al-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1al/routing-seed-r13-1al.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1am'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1am-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1am.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1am report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1al report/PCB SHA mismatch in route1am report helper')
    out={
      'revision':'r13-route1am-c1-gnd-local','source_route1al_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':1,'track_width_mm':0.30,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'C1.2/GND':{'pad_mm':[11.265,11.085],'gnd_via_mm':[12.15,11.085],'target_reference':'continuous In1.Cu GND zone','c1_value':'10uF','c1_1_net':'+1V8'}},
      'design_rationale':'Give C1.2/GND a dedicated short standard-rule return. Conservative all-layer geometry preflight on the accepted route1al artifact gives approximately 0.3923 mm minimum pessimistic copper-to-copper gap to non-GND copper; the limiting model is the adjacent C1.1/+1V8 pad, leaving approximately 0.2923 mm margin beyond a 0.1000 mm clearance requirement. No candidate keepout or board-edge conflict was found. Executed KiCad DRC remains the acceptance authority.',
      'logical_connectivity_added':['C1.2/GND -> continuous In1.Cu GND reference'],
      'c1_1_status':'UNCHANGED_+1V8','component_moves':[],'component_rotations':[],'accepted_route1al_geometry_modified':False,
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED','ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
