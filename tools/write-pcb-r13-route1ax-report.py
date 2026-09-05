#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1aw/AegisBioWatch-MainBoard-Route1aw-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1aw/routing-seed-r13-1aw.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ax'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ax-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1ax.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1ax report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1aw report/PCB SHA mismatch in route1ax report helper')
    out={
      'revision':'r13-route1ax-j101-upper-gnd-local',
      'source_route1aw_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':1,'track_width_mm':0.30,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'J101.2/GND upper':{
        'pad_mm':[38.475,10.625],'gnd_via_mm':[39.20,10.625],'target_reference':'continuous In1.Cu GND zone',
        'j101_value':'EVQPLDA15_SHIP_WAKE','j101_1_net':'SHIP_HOLD','j101_2_net':'GND',
        'j101_1_pads_mm':[[34.775,10.625],[34.775,15.025]],'j101_2_pads_mm':[[38.475,10.625],[38.475,15.025]],
        'target_pad':'upper J101.2 terminal'}},
      'preflight':{
        'minimum_conservative_non_gnd_copper_gap_mm':1.42,
        'limiting_object':'D102.1/DOCK_5V_RAW versus the proposed via/track capsule',
        'track_length_mm':0.725,'via_copper_to_board_edge_gap_mm':3.50,
        'rf_region':'untouched','supplier_gated_region':'untouched'},
      'design_rationale':'Close only the upper J101.2/GND terminal at (38.475,10.625) with one 0.725 mm horizontal 0.30 mm F.Cu segment to a standard 0.60/0.30 mm through-via at (39.20,10.625), stitching into continuous In1.Cu GND. Conservative all-local-copper preflight gives about 1.42 mm minimum non-GND copper gap, limited by D102.1/DOCK_5V_RAW, and 3.50 mm via-copper clearance to the right board edge. J101.1/SHIP_HOLD, the accepted lower J101.2/GND closure, all other accepted route1aw geometry, RF routing, and supplier-gated interfaces remain unchanged. Executed KiCad DRC remains acceptance authority.',
      'logical_connectivity_added':['upper J101.2/GND -> continuous In1.Cu GND reference'],
      'j101_signal_pads_status':'UNCHANGED','j101_lower_gnd_closure_status':'RETAINED',
      'component_moves':[],'component_rotations':[],'accepted_route1aw_geometry_modified':False,
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED','ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
