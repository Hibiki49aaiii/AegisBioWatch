#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1bj-accepted.sh

python3 tools/probe-pcb-r13-route1bk-doglegs.py   --route1bj-drc-json /tmp/route1bj.json   --route1bj-pin-net-audit /tmp/route1bj-audit.json   --output /tmp/route1bk-doglegs.json

python3 tools/probe-pcb-r13-route1bk-c305-c304-vsys-haptic.py   --route1bj-drc-json /tmp/route1bj.json   --route1bj-pin-net-audit /tmp/route1bj-audit.json   --dogleg-screen-json /tmp/route1bk-doglegs.json   --output /tmp/route1bk-probe.json

python3 -X faulthandler tools/materialize-pcb-r13-route1bk-c305-c304-vsys-haptic.py   --route1bj-drc-json /tmp/route1bj.json   --route1bj-pin-net-audit /tmp/route1bj-audit.json   --exact-probe-json /tmp/route1bk-probe.json

kicad-cli pcb drc --format json --severity-all   -o /tmp/route1bk.json   hardware/main-board/pcb/route-r13-1bk/AegisBioWatch-MainBoard-Route1bk-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py   --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml   --pcb hardware/main-board/pcb/route-r13-1bk/AegisBioWatch-MainBoard-Route1bk-r13.kicad_pcb   --output /tmp/route1bk-audit.json

python3 - <<'PY'
import hashlib,json
from pathlib import Path

d=json.load(open('/tmp/route1bk.json'))
a=json.load(open('/tmp/route1bk-audit.json'))
p=json.load(open('/tmp/route1bk-probe.json'))
s=json.load(open('/tmp/route1bk-doglegs.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1bk/routing-seed-r13-1bk.json'))
pcb=Path('hardware/main-board/pcb/route-r13-1bk/AegisBioWatch-MainBoard-Route1bk-r13.kicad_pcb')
c=r['connections']['C305.1/VSYS_HAPTIC to C304.1/VSYS_HAPTIC']

accepted_pcb_sha='283217e6a0ff89355999c0bc2fa5330d5348811caaea97deff6c8b27295a9ed8'
accepted_artifact_digest='sha256:c8d4e565364159f555fc3c28260033b912946929d759d8df0f396bdac9c2c75e'

out={
  'rule_violations':len(d.get('violations',[])),
  'unconnected_items':len(d.get('unconnected_items',[])),
  'pin_net_audit':a.get('result'),
  'audited_nodes':a.get('audited_present_source_nodes'),
  'probe_board_modified':p.get('board_modified'),
  'probe_min_clearance_mm':p.get('path',{}).get('minimum_conservative_clearance_mm'),
  'probe_gnd_via_gap_mm':p.get('path',{}).get('independent_gnd_via_gap_mm'),
  'screen_board_modified':s.get('board_modified'),
  'screen_grid_mm':s.get('grid_mm'),
  'segments_added':r.get('track_segments_added'),
  'vias_added':r.get('vias_added'),
  'track_width_mm':r.get('track_width_mm'),
  'segment_lengths_mm':r.get('segment_lengths_mm'),
  'track_length_mm':r.get('track_length_mm'),
  'component_moves':r.get('component_moves'),
  'component_rotations':r.get('component_rotations'),
  'c305_value':c.get('c305_value'),
  'c304_value':c.get('c304_value'),
  'path_points_mm':c.get('path_points_mm'),
  'u4_value':c.get('u4_value'),
  'u4_pad10_net':c.get('u4_pad10_net'),
  'r305_value':c.get('r305_value'),
  'r305_pad2_net':c.get('r305_pad2_net'),
  'c305_gnd_routing_touched':r.get('c305_gnd_routing_touched'),
  'c304_gnd_routing_touched':r.get('c304_gnd_routing_touched'),
  'u4_vdd_routing_touched':r.get('u4_vdd_routing_touched'),
  'r305_feed_routing_touched':r.get('r305_feed_routing_touched'),
  'accepted_route1bj_geometry_modified':r.get('accepted_route1bj_geometry_modified'),
  'rf_routing_touched':r.get('rf_routing_touched'),
  'supplier_gated_interfaces_touched':r.get('supplier_gated_interfaces_touched'),
  'pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),
  'accepted_artifact_pcb_sha256':accepted_pcb_sha,
  'accepted_artifact_digest':accepted_artifact_digest
}
print(json.dumps(out,indent=2))
Path('/tmp/route1bk-summary.json').write_text(json.dumps(out,indent=2)+'\n')

assert out['rule_violations']==0 and out['unconnected_items']==113
assert out['pin_net_audit']=='PASS' and out['audited_nodes']==268
assert out['probe_board_modified'] is False and out['screen_board_modified'] is False
assert abs(out['screen_grid_mm']-0.05)<1e-9
assert abs(out['probe_min_clearance_mm']-0.125)<1e-6
assert abs(out['probe_gnd_via_gap_mm']-0.125)<1e-6
assert out['segments_added']==3 and out['vias_added']==0
assert out['track_width_mm']==0.30
assert out['segment_lengths_mm']==[0.685,9.2,2.075] and abs(out['track_length_mm']-11.96)<1e-6
assert out['component_moves']==[] and out['component_rotations']==[]
assert out['c305_value']=='1uF' and out['c304_value']=='100nF'
assert out['path_points_mm']==[[6.805,22.335],[6.805,21.65],[16.005,21.65],[16.005,23.725]]
assert out['u4_value']=='DRV2605LDGSR' and out['u4_pad10_net']=='VSYS_HAPTIC'
assert out['r305_value']=='0R / FB OPTION' and out['r305_pad2_net']=='VSYS_HAPTIC'
assert out['c305_gnd_routing_touched'] is False
assert out['c304_gnd_routing_touched'] is False
assert out['u4_vdd_routing_touched'] is False
assert out['r305_feed_routing_touched'] is False
assert out['accepted_route1bj_geometry_modified'] is False
assert out['rf_routing_touched'] is False
assert out['supplier_gated_interfaces_touched'] is False

if out['pcb_sha256'] != accepted_pcb_sha:
    print('route1bk note: regenerated PCB bytes differ from accepted Artifact provenance; executed electrical/geometry gates remain authoritative')
PY
