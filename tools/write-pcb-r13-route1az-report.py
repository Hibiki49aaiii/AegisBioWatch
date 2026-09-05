#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1ay/AegisBioWatch-MainBoard-Route1ay-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1ay/routing-seed-r13-1ay.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1az'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1az-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1az.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1az report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1ay report/PCB SHA mismatch in route1az report helper')
    out={
      'revision':'r13-route1az-r304-gnd-local',
      'source_route1ay_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':1,'track_width_mm':0.30,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'R304.2/GND':{
        'pad_mm':[25.395,25.975],'gnd_via_mm':[25.395,26.630],'target_reference':'continuous In1.Cu GND zone',
        'r304_value':'100k PD','r304_1_net':'HAPTIC_EN','r304_2_net':'GND',
        'r304_1_pad_mm':[24.755,25.975],'r304_2_pad_mm':[25.395,25.975]}},
      'preflight':{
        'minimum_conservative_non_gnd_copper_gap_mm':0.260,
        'limiting_object':'adjacent R304.1/HAPTIC_EN pad versus proposed GND track/via capsule',
        'minimum_other_component_non_gnd_copper_gap_mm':1.150,
        'other_component_limiting_object':'R1.2/NRF_RESET_N',
        'track_length_mm':0.655,
        'rf_routing_touched':False,'supplier_gated_region':'untouched'},
      'design_rationale':'Close only R304.2/GND at (25.395,25.975) with one 0.655 mm vertical 0.30 mm F.Cu segment to a standard 0.60/0.30 mm through-via at (25.395,26.630), stitching into continuous In1.Cu GND. Conservative preflight gives about 0.260 mm copper gap to paired R304.1/HAPTIC_EN and about 1.150 mm to the nearest non-GND copper on another component. R304.1, all accepted route1ay geometry, RF routing, and supplier-gated interfaces remain unchanged. Executed KiCad DRC remains acceptance authority.',
      'logical_connectivity_added':['R304.2/GND -> continuous In1.Cu GND reference'],
      'r304_signal_pad_status':'UNCHANGED',
      'component_moves':[],'component_rotations':[],'accepted_route1ay_geometry_modified':False,
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED','ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
