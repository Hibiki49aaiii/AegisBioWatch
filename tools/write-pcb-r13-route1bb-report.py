#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1ba/AegisBioWatch-MainBoard-Route1ba-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1ba/routing-seed-r13-1ba.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bb'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1bb-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1bb.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1bb report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1ba report/PCB SHA mismatch in route1bb report helper')
    out={
      'revision':'r13-route1bb-j9-left-gnd-local',
      'source_route1ba_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':1,'track_width_mm':0.30,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'J9.1/GND left pad':{
        'pad_mm':[20.850,5.775],'gnd_via_mm':[19.850,5.775],'target_reference':'continuous In1.Cu GND zone',
        'j9_value':'EVQPUK02K_SIDE_BUTTON','j9_1_net':'GND','j9_2_net':'SIDE_BUTTON',
        'j9_1_pad_positions_mm':[[20.850,5.775],[26.000,5.775]],
        'j9_2_pad_positions_mm':[[20.850,7.475],[26.000,7.475]],
        'target_physical_pad':'left J9.1/GND'}},
      'preflight':{
        'candidate_basis':'same duplicate-pad family as accepted route1ba; executed KiCad DRC is authoritative',
        'track_length_mm':1.000,
        'rf_routing_touched':False,'supplier_gated_region':'untouched'},
      'design_rationale':'Close only the left physical J9.1/GND pad at (20.850,5.775) with one 1.000 mm horizontal 0.30 mm F.Cu segment to a standard 0.60/0.30 mm through-via at (19.850,5.775), stitching into continuous In1.Cu GND. No clearance assumption is promoted from symmetry; executed KiCad DRC decides acceptance. The accepted right J9.1 route, both SIDE_BUTTON pads, all accepted route1ba geometry, RF routing, and supplier-gated interfaces remain unchanged.',
      'logical_connectivity_added':['left J9.1/GND -> continuous In1.Cu GND reference'],
      'right_j9_1_route1ba_status':'UNCHANGED','j9_side_button_pads_status':'UNCHANGED',
      'component_moves':[],'component_rotations':[],'accepted_route1ba_geometry_modified':False,
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED','ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
