#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1ax/AegisBioWatch-MainBoard-Route1ax-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1ax/routing-seed-r13-1ax.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ay'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ay-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1ay.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1ay report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1ax report/PCB SHA mismatch in route1ay report helper')
    out={
      'revision':'r13-route1ay-r303-gnd-local',
      'source_route1ax_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':1,'track_width_mm':0.30,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'R303.2/GND':{
        'pad_mm':[23.145,25.975],'gnd_via_mm':[23.145,26.630],'target_reference':'continuous In1.Cu GND zone',
        'r303_value':'100k PD','r303_1_net':'HAPTIC_TRIG','r303_2_net':'GND',
        'r303_1_pad_mm':[22.505,25.975],'r303_2_pad_mm':[23.145,25.975]}},
      'preflight':{
        'minimum_conservative_non_gnd_copper_gap_mm':0.260,
        'limiting_object':'adjacent R303.1/HAPTIC_TRIG pad versus proposed GND track/via capsule',
        'minimum_other_component_non_gnd_copper_gap_mm':1.150,
        'other_component_limiting_object':'L4.2/RF_ANT',
        'track_length_mm':0.655,
        'rf_routing_touched':False,'supplier_gated_region':'untouched'},
      'design_rationale':'Close only R303.2/GND at (23.145,25.975) with one 0.655 mm vertical 0.30 mm F.Cu segment to a standard 0.60/0.30 mm through-via at (23.145,26.630), stitching into continuous In1.Cu GND. Conservative preflight gives about 0.260 mm copper gap to the paired R303.1/HAPTIC_TRIG pad and about 1.150 mm to the nearest non-GND copper on another component. R303.1, all accepted route1ax geometry, RF routing, and supplier-gated interfaces remain unchanged. Executed KiCad DRC remains acceptance authority.',
      'logical_connectivity_added':['R303.2/GND -> continuous In1.Cu GND reference'],
      'r303_signal_pad_status':'UNCHANGED',
      'component_moves':[],'component_rotations':[],'accepted_route1ax_geometry_modified':False,
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED','ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
