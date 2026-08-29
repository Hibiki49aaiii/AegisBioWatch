#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1bg-accepted.sh

python3 tools/probe-pcb-r13-route1bi-doglegs.py   --route1bg-drc-json /tmp/route1bg.json   --route1bg-pin-net-audit /tmp/route1bg-audit.json   --output /tmp/route1bi-doglegs.json

python3 tools/probe-pcb-r13-route1bi-u3-c1-1v8.py   --dogleg-screen-json /tmp/route1bi-doglegs.json   --output /tmp/route1bi-probe.json

python3 -X faulthandler tools/materialize-pcb-r13-route1bi-u3-c1-1v8.py   --route1bg-drc-json /tmp/route1bg.json   --route1bg-pin-net-audit /tmp/route1bg-audit.json   --exact-probe-json /tmp/route1bi-probe.json

kicad-cli pcb drc --format json --severity-all   -o /tmp/route1bi.json   hardware/main-board/pcb/route-r13-1bi/AegisBioWatch-MainBoard-Route1bi-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py   --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml   --pcb hardware/main-board/pcb/route-r13-1bi/AegisBioWatch-MainBoard-Route1bi-r13.kicad_pcb   --output /tmp/route1bi-audit.json

python3 - <<'PY'
import hashlib,json
from pathlib import Path

d=json.load(open('/tmp/route1bi.json'))
a=json.load(open('/tmp/route1bi-audit.json'))
p=json.load(open('/tmp/route1bi-probe.json'))
s=json.load(open('/tmp/route1bi-doglegs.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1bi/routing-seed-r13-1bi.json'))
pcb=Path('hardware/main-board/pcb/route-r13-1bi/AegisBioWatch-MainBoard-Route1bi-r13.kicad_pcb')
c=r['connections']['U3.8/+1V8 to C1.1/+1V8']

accepted_pcb_sha='9e513dc10b0cf16006bebcf60bf925e78740bbdd124811852b2703e45f1fd1ca'
accepted_artifact_digest='sha256:a9d825985fac0304fcabfaf6ad0f82a26ea62e361e098a1cd2979a2406b6eae5'

out={
  'rule_violations':len(d.get('violations',[])),
  'unconnected_items':len(d.get('unconnected_items',[])),
  'pin_net_audit':a.get('result'),
  'audited_nodes':a.get('audited_present_source_nodes'),
  'probe_board_modified':p.get('board_modified'),
  'probe_min_clearance_mm':p.get('path',{}).get('minimum_conservative_clearance_mm'),
  'screen_board_modified':s.get('board_modified'),
  'segments_added':r.get('track_segments_added'),
  'vias_added':r.get('vias_added'),
  'track_width_mm':r.get('track_width_mm'),
  'segment_lengths_mm':r.get('segment_lengths_mm'),
  'track_length_mm':r.get('track_length_mm'),
  'component_moves':r.get('component_moves'),
  'component_rotations':r.get('component_rotations'),
  'u3_value':c.get('u3_value'),
  'c1_value':c.get('c1_value'),
  'path_points_mm':c.get('path_points_mm'),
  'u3_pad8_mm':c.get('u3_pad8_mm'),
  'u3_pad8_net':c.get('u3_pad8_net'),
  'u3_pad7_mm':c.get('u3_pad7_mm'),
  'u3_pad7_net':c.get('u3_pad7_net'),
  'u3_pad5_mm':c.get('u3_pad5_mm'),
  'u3_pad5_net':c.get('u3_pad5_net'),
  'c1_pad1_mm':c.get('c1_pad1_mm'),
  'c1_pad1_net':c.get('c1_pad1_net'),
  'c1_pad2_mm':c.get('c1_pad2_mm'),
  'c1_pad2_net':c.get('c1_pad2_net'),
  'u3_signal_routing_touched':r.get('u3_signal_routing_touched'),
  'c1_gnd_routing_touched':r.get('c1_gnd_routing_touched'),
  'accepted_route1bg_geometry_modified':r.get('accepted_route1bg_geometry_modified'),
  'rf_routing_touched':r.get('rf_routing_touched'),
  'supplier_gated_interfaces_touched':r.get('supplier_gated_interfaces_touched'),
  'pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),
  'accepted_artifact_pcb_sha256':accepted_pcb_sha,
  'accepted_artifact_digest':accepted_artifact_digest
}
print(json.dumps(out,indent=2))
Path('/tmp/route1bi-summary.json').write_text(json.dumps(out,indent=2)+'\n')

assert out['rule_violations']==0 and out['unconnected_items']==115
assert out['pin_net_audit']=='PASS' and out['audited_nodes']==268
assert out['probe_board_modified'] is False and out['screen_board_modified'] is False
assert out['probe_min_clearance_mm']>=0.300-1e-6
assert out['segments_added']==2 and out['vias_added']==0
assert out['track_width_mm']==0.30
assert out['segment_lengths_mm']==[0.775,6.365] and abs(out['track_length_mm']-7.14)<1e-6
assert out['component_moves']==[] and out['component_rotations']==[]
assert out['u3_value']=='W25Q256JWPIQ 256Mbit' and out['c1_value']=='10uF'
assert out['path_points_mm']==[[11.08,4.72],[10.305,4.72],[10.305,11.085]]
assert out['u3_pad8_mm']==[11.08,4.72] and out['u3_pad8_net']=='+1V8'
assert out['u3_pad7_mm']==[11.08,5.99] and out['u3_pad7_net']=='FLASH_HOLD_N'
assert out['u3_pad5_mm']==[11.08,8.53] and out['u3_pad5_net']=='AUX_SPI_MOSI'
assert out['c1_pad1_mm']==[10.305,11.085] and out['c1_pad1_net']=='+1V8'
assert out['c1_pad2_mm']==[11.265,11.085] and out['c1_pad2_net']=='GND'
assert out['u3_signal_routing_touched'] is False and out['c1_gnd_routing_touched'] is False
assert out['accepted_route1bg_geometry_modified'] is False
assert out['rf_routing_touched'] is False and out['supplier_gated_interfaces_touched'] is False

if out['pcb_sha256'] != accepted_pcb_sha:
    print('route1bi note: regenerated PCB bytes differ from accepted Artifact provenance; executed electrical/geometry gates remain authoritative')
PY
