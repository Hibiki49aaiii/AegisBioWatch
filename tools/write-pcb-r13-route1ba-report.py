#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1az/AegisBioWatch-MainBoard-Route1az-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1az/routing-seed-r13-1az.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ba'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ba-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1ba.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1ba report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1az report/PCB SHA mismatch in route1ba report helper')
    out={
      'revision':'r13-route1ba-j9-right-gnd-local',
      'source_route1az_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':1,'track_width_mm':0.30,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'J9.1/GND right pad':{
        'pad_mm':[26.000,5.775],'gnd_via_mm':[27.000,5.775],'target_reference':'continuous In1.Cu GND zone',
        'j9_value':'EVQPUK02K_SIDE_BUTTON','j9_1_net':'GND','j9_2_net':'SIDE_BUTTON',
        'j9_1_pad_positions_mm':[[20.850,5.775],[26.000,5.775]],
        'j9_2_pad_positions_mm':[[20.850,7.475],[26.000,7.475]],
        'target_physical_pad':'right J9.1/GND'}},
      'preflight':{
        'minimum_conservative_non_gnd_copper_gap_mm':0.931,
        'limiting_object':'right J9.2/SIDE_BUTTON pad versus proposed GND via/track',
        'nearby_non_gnd_routed_track_or_via_detected':False,
        'track_length_mm':1.000,
        'rf_routing_touched':False,'supplier_gated_region':'untouched'},
      'design_rationale':'Close only the right physical J9.1/GND pad at (26.000,5.775) with one 1.000 mm horizontal 0.30 mm F.Cu segment to a standard 0.60/0.30 mm through-via at (27.000,5.775), stitching into continuous In1.Cu GND. Accepted route1az Artifact preflight found about 0.931 mm conservative clearance to the nearest non-GND pad (right J9.2/SIDE_BUTTON) and no local non-GND routed track/via. The left J9.1 pad, both SIDE_BUTTON pads, all accepted route1az geometry, RF routing, and supplier-gated interfaces remain unchanged. Executed KiCad DRC remains acceptance authority.',
      'logical_connectivity_added':['right J9.1/GND -> continuous In1.Cu GND reference'],
      'left_j9_1_gnd_pad_status':'UNCHANGED','j9_side_button_pads_status':'UNCHANGED',
      'component_moves':[],'component_rotations':[],'accepted_route1az_geometry_modified':False,
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED','ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
