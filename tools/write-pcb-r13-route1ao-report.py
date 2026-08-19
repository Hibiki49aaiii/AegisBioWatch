#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC_PCB=ROOT/'hardware/main-board/pcb/route-r13-1an/AegisBioWatch-MainBoard-Route1an-r13.kicad_pcb'
SRC_REPORT=ROOT/'hardware/main-board/pcb/route-r13-1an/routing-seed-r13-1an.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ao'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ao-r13.kicad_pcb'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1ao.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if not SRC_PCB.is_file() or not SRC_REPORT.is_file() or not OUT_PCB.is_file():
        raise SystemExit('route1ao report inputs missing')
    src=json.loads(SRC_REPORT.read_text()); srcsha=sha(SRC_PCB)
    if src.get('output_sha256')!=srcsha:
        raise SystemExit('route1an report/PCB SHA mismatch in route1ao report helper')
    out={
      'revision':'r13-route1ao-u3-gnd-local',
      'source_route1an_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_segments_added':1,
      'vias_added':1,
      'track_width_mm':0.30,
      'via_size_mm':0.60,
      'via_drill_mm':0.30,
      'connections':{
        'U3.4/GND':{
          'pad_mm':[3.58,8.53],
          'gnd_via_mm':[2.8,8.53],
          'target_reference':'continuous In1.Cu GND zone',
          'u3_value':'W25Q256JWPIQ 256Mbit',
          'u3_1_net':'FLASH_CS_N',
          'u3_2_net':'AUX_SPI_MISO',
          'u3_3_net':'FLASH_WP_N',
          'u3_5_net':'AUX_SPI_MOSI',
          'u3_6_net':'AUX_SPI_SCK',
          'u3_7_net':'FLASH_HOLD_N',
          'u3_8_net':'+1V8'
        }
      },
      'design_rationale':'Route U3.4/GND toward decreasing X directly into the In1.Cu GND reference with one short F.Cu segment and one standard through via. Conservative accepted-route1an pad-envelope screening gives approximately 0.710 mm minimum pessimistic non-GND pad clearance, limited by U3.3/FLASH_WP_N. Proposed via copper remains approximately 0.500 mm from the x=2.0 mm board edge; existing routed non-GND tracks/vias are not limiting in this region. Executed KiCad DRC remains the acceptance authority.',
      'logical_connectivity_added':['U3.4/GND -> continuous In1.Cu GND reference'],
      'u3_signal_supply_pads_status':'UNCHANGED',
      'component_moves':[],
      'component_rotations':[],
      'accepted_route1an_geometry_modified':False,
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
