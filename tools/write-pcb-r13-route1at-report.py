#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1as/AegisBioWatch-MainBoard-Route1as-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1as/routing-seed-r13-1as.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1at'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1at-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1at.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1at report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha:
        raise SystemExit('route1as report/PCB SHA mismatch in route1at report helper')
    out={
      'revision':'r13-route1at-j8-gnd-local',
      'source_route1as_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,
      'vias_added':1,
      'track_width_mm':0.30,
      'via_size_mm':0.60,
      'via_drill_mm':0.30,
      'connections':{
        'J8.5/GND':{
          'pad_mm':[14.645,15.26],
          'gnd_via_mm':[14.645,16.00],
          'target_reference':'continuous In1.Cu GND zone',
          'j8_value':'TC2030_SWD_6',
          'j8_1_net':'+1V8',
          'j8_2_net':'SWDIO',
          'j8_3_net':'NRF_RESET_N',
          'j8_4_net':'SWDCLK',
          'j8_5_net':'GND',
          'j8_6_net':'SWO'
        }
      },
      'preflight':{
        'minimum_conservative_non_gnd_copper_gap_mm':0.7263,
        'limiting_object':'J8.3/NRF_RESET_N and J8.6/SWO',
        'track_length_mm':0.740,
        'nearest_npth_center_mm':[15.915,15.641],
        'via_to_nearest_npth_hole_edge_clearance_mm':0.6744,
        'hole_to_hole_required_mm':0.1995,
        'hole_to_hole_margin_mm':0.4749,
        'via_copper_to_j8_keepout_gap_mm':0.440,
        'rf_region':'untouched',
        'supplier_gated_region':'untouched'
      },
      'design_rationale':'The initial rightward via at (15.25,15.26) was rejected by executed KiCad DRC because it was too close to the J8 NPTH at (15.915,15.641). Move only the route1at via to (14.645,16.00) and use one vertical 0.30 mm F.Cu segment from J8.5/GND. Conservative geometry gives approximately 0.6744 mm drill-edge clearance to the nearest NPTH versus the 0.1995 mm hole-to-hole requirement, while the via copper remains approximately 0.44 mm outside the J8 via keepout. All SWD signal pads remain untouched and the increment is outside frozen RF and supplier-gated regions. Executed KiCad DRC remains the acceptance authority.',
      'logical_connectivity_added':['J8.5/GND -> continuous In1.Cu GND reference'],
      'j8_signal_pads_status':'UNCHANGED',
      'component_moves':[],
      'component_rotations':[],
      'accepted_route1as_geometry_modified':False,
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
