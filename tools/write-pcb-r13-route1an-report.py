#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1am/AegisBioWatch-MainBoard-Route1am-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1am/routing-seed-r13-1am.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1an'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1an-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1an.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1an report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1am report/PCB SHA mismatch in route1an report helper')
    out={
      'revision':'r13-route1an-j2-gnd-local','source_route1am_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':1,'track_width_mm':0.30,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'J2.3/GND':{'pad_mm':[7.025,11.7725],'gnd_via_mm':[7.025,11.0225],'target_reference':'continuous In1.Cu GND zone','j2_value':'BATTERY_PACK_300mAh_3WIRE','j2_1_net':'VBAT','j2_2_net':'BAT_NTC'}},
      'design_rationale':'Route J2.3/GND outward, away from the connector-body F.Cu keepout. Conservative accepted-route1am all-copper screening gives approximately 0.5298 mm minimum pessimistic non-GND copper gap, limited by J2.2/BAT_NTC. The candidate track/via stays on the y<12.1975 side of the J2 F.Cu keepout, whose adjacent boundary is y=12.1975, and remains far from the board edge. Executed KiCad DRC remains the acceptance authority.',
      'logical_connectivity_added':['J2.3/GND -> continuous In1.Cu GND reference'],
      'j2_1_status':'UNCHANGED_VBAT','j2_2_status':'UNCHANGED_BAT_NTC','battery_policy_status':'UNCHANGED_J2_GND_ROUTING_ONLY',
      'component_moves':[],'component_rotations':[],'accepted_route1am_geometry_modified':False,
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED','ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
