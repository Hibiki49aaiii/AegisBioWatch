#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1au/AegisBioWatch-MainBoard-Route1au-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1au/routing-seed-r13-1au.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1av'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1av-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1av.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1av report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha:
        raise SystemExit('route1au report/PCB SHA mismatch in route1av report helper')
    out={
      'revision':'r13-route1av-u4-gnd-local',
      'source_route1au_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,
      'vias_added':1,
      'track_width_mm':0.30,
      'via_size_mm':0.60,
      'via_drill_mm':0.30,
      'connections':{
        'U4.8/GND':{
          'pad_mm':[23.005,14.400],
          'gnd_via_mm':[24.100,14.400],
          'target_reference':'continuous In1.Cu GND zone',
          'u4_value':'DRV2605LDGSR',
          'u4_7_net':'HAPTIC_OUT_P',
          'u4_8_net':'GND',
          'u4_9_net':'HAPTIC_OUT_N',
          'u4_7_pad_mm':[23.005,14.900],
          'u4_9_pad_mm':[23.005,13.900]
        }
      },
      'preflight':{
        'minimum_conservative_non_gnd_copper_gap_mm':0.2000,
        'limiting_objects':['U4.7/HAPTIC_OUT_P versus new F.Cu segment','U4.9/HAPTIC_OUT_N versus new F.Cu segment'],
        'via_to_adjacent_signal_pad_copper_gap_mm':0.2093,
        'track_length_mm':1.095,
        'screening_method':'accepted route1au PCB geometry; Shapely copper-shape distance including pads/tracks/vias',
        'rf_region':'untouched',
        'supplier_gated_region':'untouched'
      },
      'design_rationale':'Close only DRV2605L U4.8/GND with one 1.095 mm horizontal 0.30 mm F.Cu segment to a standard 0.60/0.30 mm through-via at (24.10,14.40), stitching into continuous In1.Cu GND. Accepted-route1au copper screening gives 0.200 mm minimum non-GND gap to the adjacent U4.7/HAPTIC_OUT_P and U4.9/HAPTIC_OUT_N pads, with approximately 0.2093 mm via-copper gap to those pads. R502 is deferred because PVSS1_LOCAL occupies its straightforward escape region; R303/R304 are deferred because they sit adjacent to the RF matching area. RF routing, supplier-gated interfaces, and all accepted route1au geometry remain unchanged. Executed KiCad DRC remains acceptance authority.',
      'logical_connectivity_added':['U4.8/GND -> continuous In1.Cu GND reference'],
      'u4_signal_pad_status':'UNCHANGED',
      'component_moves':[],
      'component_rotations':[],
      'accepted_route1au_geometry_modified':False,
      'sys_i2c_scl_status':'DEFERRED_GEOMETRY_GATED',
      'ldo2_in_status':'DEFERRED_GEOMETRY_CONSTRAINED_NO_VIA_IN_PAD',
      'route1n_chg5v_status':'REJECTED_AND_DEFERRED',
      'rf_routing_touched':False,
      'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC',
      'release_status':'NOT_FOR_GERBER',
      'report_process':'fresh_python_without_pcbnew'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
