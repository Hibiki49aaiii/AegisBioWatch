#!/usr/bin/env python3
"""Write route-1o metadata in a fresh Python process with no pcbnew/SWIG state."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1m/AegisBioWatch-MainBoard-Route1m-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1m/routing-seed-r13-1m.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1o'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1o-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1o.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1o report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1m report/PCB SHA mismatch in route1o helper')
    out={
      'revision':'r13-route1o-vbusout-sense-local-decoupling','source_route1m_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':5,'vias_added':3,'sense_track_width_mm':0.25,'gnd_track_width_mm':0.30,
      'sense_via_size_mm':0.45,'sense_via_drill_mm':0.20,'gnd_via_size_mm':0.60,'gnd_via_drill_mm':0.30,
      'c105':{'value':'1.0uF X5R 10V','center_mm':[16.185102,25.381239],
        'vbusout_sense_pad_mm':[15.410102,25.381239],'gnd_pad_mm':[16.960102,25.381239],
        'u2_22_vbusout_sense_mm':[13.8875,27.75],
        'sense_entry_via_mm':[14.05,27.75],'sense_bcu_corner_mm':[14.05,25.05],'sense_exit_via_mm':[15.00,25.05],
        'sense_crossing_layer':'B.Cu','gnd_via_mm':[17.70,25.38],'gnd_reference':'continuous In1.Cu GND zone'},
      'rejected_geometry':{'strategy':'Top-only dogleg at x=14.10','reason':'vertical VBUSOUT_SENSE segment bridged/shorted adjacent U2.23/CC1_NC and U2.24/CC2_NC; no waiver used'},
      'logical_connectivity_added':['U2.22/VBUSOUT_SENSE <-> C105.1/VBUSOUT_SENSE','C105.2/GND -> continuous GND reference'],
      'route1n_chg5v_candidate_status':'REJECTED_SEPARATE_STAGE',
      'component_moves':[],'component_rotations':[],
      'accepted_vbat_vsys_pvss_geometry_modified':False,'in1_gnd_plane_preserved_and_refilled':True,
      'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER','report_process':'fresh_python_without_pcbnew'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
