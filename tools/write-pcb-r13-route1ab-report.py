#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1aa/AegisBioWatch-MainBoard-Route1aa-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1aa/routing-seed-r13-1aa.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ab'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ab-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1ab.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file(): raise SystemExit('route1ab report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha: raise SystemExit('route1aa report/PCB SHA mismatch in route1ab report helper')
    out={
      'revision':'r13-route1ab-c112-gnd-local','source_route1aa_sha256':srcsha,'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,'vias_added':1,'track_width_mm':0.30,'via_size_mm':0.60,'via_drill_mm':0.30,
      'connections':{'C112.2/GND':{'pad_mm':[11.761586,19.095759],'gnd_via_mm':[12.55,19.10],'target_reference':'continuous In1.Cu GND zone'}},
      'design_rationale':'Use a dedicated short GND via for the BIO_SW local capacitor rather than daisy-chaining into neighboring display/nRF decoupling grounds.',
      'logical_connectivity_added':['C112.2/GND -> continuous In1.Cu GND reference'],
      'bio_sw_status':'UNCHANGED_PENDING_SEPARATE_VALIDATION',
      'i2c_scl_status':'DEFERRED_GEOMETRY_GATED','ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED','rf_routing_touched':False,'supplier_gated_interfaces_touched':False,
      'component_moves':[],'component_rotations':[],'accepted_route1aa_geometry_modified':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
