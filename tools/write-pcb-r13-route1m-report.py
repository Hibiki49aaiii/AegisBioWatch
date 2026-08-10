#!/usr/bin/env python3
"""Write route-1m metadata in a fresh Python process with no pcbnew/SWIG state."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1l/AegisBioWatch-MainBoard-Route1l-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1l/routing-seed-r13-1l.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1m'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1m-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1m.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1m report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1l report/PCB SHA mismatch in route1m helper')
    out={
      'revision':'r13-route1m-vbat-local-decoupling','source_route1l_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':3,'vias_added':1,'vbat_track_width_mm':0.40,'gnd_track_width_mm':0.40,'via_size_mm':0.60,'via_drill_mm':0.30,
      'c106':{'value':'2.2uF X7R 16V','center_mm':[15.522674,29.714978],
        'orientation_from_deg':90.0,'orientation_to_deg':270.0,
        'vbat_pad_after_rotation_mm':[15.522674,28.939978],'gnd_pad_after_rotation_mm':[15.522674,30.489978],
        'u2_19_vbat_mm':[13.8875,29.25],'vbat_escape_mm':[14.65,29.25],
        'gnd_via_mm':[16.85,30.49],'gnd_reference':'continuous In1.Cu GND zone'},
      'rejected_geometries':[
        {'strategy':'direct U2.19->C106.1 diagonal with source C106 orientation 90 deg','reason':'crossed adjacent U2.18/BAT_NTC'},
        {'strategy':'source orientation 90 deg with GND via (16.20,28.94)','reason':'intersected accepted route1l B.Cu VSYS trunk'},
        {'strategy':'source orientation 90 deg with GND via (16.65,28.94)','reason':'short/clearance to C101.1/CHG_5V'}
      ],
      'corrected_geometry':{'reason':'accepted route1l PCB physical pad geometry is authoritative; C106 is rotated in place so VBAT faces U2.19 and GND faces the open return corridor'},
      'logical_connectivity_added':['U2.19/VBAT <-> C106.1/VBAT','C106.2/GND -> continuous GND reference'],
      'battery_connector_deferred':True,'charger_input_deferred':True,
      'component_moves':[],
      'component_rotations':{'C106':{'from_deg':90.0,'to_deg':270.0,'center_mm':[15.522674,29.714978]}},
      'accepted_vsys_pvss_geometry_modified':False,'in1_gnd_plane_preserved_and_refilled':True,'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
