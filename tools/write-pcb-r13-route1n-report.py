#!/usr/bin/env python3
"""Write route-1n metadata in a fresh Python process with no pcbnew/SWIG state."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1m/AegisBioWatch-MainBoard-Route1m-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1m/routing-seed-r13-1m.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1n'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1n-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1n.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1n report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1m report/PCB SHA mismatch in route1n helper')
    out={
      'revision':'r13-route1n-chg5v-local-decoupling','source_route1m_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':2,'vias_added':1,'chg_track_width_mm':0.40,'gnd_track_width_mm':0.40,'via_size_mm':0.60,'via_drill_mm':0.30,
      'c101':{'value':'1.0uF X5R 10V','center_mm':[17.141428,28.799501],
        'orientation_from_deg':90.0,'orientation_to_deg':270.0,
        'chg5v_pad_after_rotation_mm':[17.141428,28.024501],'gnd_pad_after_rotation_mm':[17.141428,29.574501],
        'u2_21_chg5v_mm':[13.8875,28.25],'gnd_via_mm':[18.25,29.575],'gnd_reference':'continuous In1.Cu GND zone'},
      'logical_connectivity_added':['U2.21/CHG_5V <-> C101.1/CHG_5V','C101.2/GND -> continuous GND reference'],
      'remote_chg5v_r501_d101_deferred':True,'dock_5v_raw_deferred':True,
      'component_moves':[],
      'component_rotations':{'C101':{'from_deg':90.0,'to_deg':270.0,'center_mm':[17.141428,28.799501]}},
      'accepted_vbat_vsys_pvss_geometry_modified':False,'in1_gnd_plane_preserved_and_refilled':True,
      'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
