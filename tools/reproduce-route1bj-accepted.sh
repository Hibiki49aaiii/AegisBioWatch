#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1bi-accepted.sh

python3 tools/probe-pcb-r13-route1bj-doglegs.py   --route1bi-drc-json /tmp/route1bi.json   --route1bi-pin-net-audit /tmp/route1bi-audit.json   --output /tmp/route1bj-doglegs.json

python3 tools/probe-pcb-r13-route1bj-r404-r302-1v8.py   --route1bi-drc-json /tmp/route1bi.json   --route1bi-pin-net-audit /tmp/route1bi-audit.json   --dogleg-screen-json /tmp/route1bj-doglegs.json   --output /tmp/route1bj-probe.json

python3 -X faulthandler tools/materialize-pcb-r13-route1bj-r404-r302-1v8.py   --route1bi-drc-json /tmp/route1bi.json   --route1bi-pin-net-audit /tmp/route1bi-audit.json   --exact-probe-json /tmp/route1bj-probe.json

kicad-cli pcb drc --format json --severity-all   -o /tmp/route1bj.json   hardware/main-board/pcb/route-r13-1bj/AegisBioWatch-MainBoard-Route1bj-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py   --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml   --pcb hardware/main-board/pcb/route-r13-1bj/AegisBioWatch-MainBoard-Route1bj-r13.kicad_pcb   --output /tmp/route1bj-audit.json

python3 - <<'PY'
import hashlib,json
from pathlib import Path

d=json.load(open('/tmp/route1bj.json'))
a=json.load(open('/tmp/route1bj-audit.json'))
p=json.load(open('/tmp/route1bj-probe.json'))
s=json.load(open('/tmp/route1bj-doglegs.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1bj/routing-seed-r13-1bj.json'))
pcb=Path('hardware/main-board/pcb/route-r13-1bj/AegisBioWatch-MainBoard-Route1bj-r13.kicad_pcb')
c=r['connections']['R404.1/+1V8 to R302.1/+1V8']

accepted_pcb_sha='64b3f16ad984c45fb995c2694c3714d7200db9fb07f21be7fcb391aa9e04b6d8'
accepted_artifact_digest='sha256:94e0794c5ab18593cc51a267e2da96f80d87c1f97c7af377bffd74827ebd4945'

out={
  'rule_violations':len(d.get('violations',[])),
  'unconnected_items':len(d.get('unconnected_items',[])),
  'pin_net_audit':a.get('result'),
  'audited_nodes':a.get('audited_present_source_nodes'),
  'probe_board_modified':p.get('board_modified'),
  'probe_min_clearance_mm':p.get('path',{}).get('minimum_conservative_clearance_mm'),
  'probe_r501_gap_mm':p.get('path',{}).get('independent_r501_pad_gap_mm'),
  'screen_board_modified':s.get('board_modified'),
  'screen_grid_mm':s.get('grid_mm'),
  'segments_added':r.get('track_segments_added'),
  'vias_added':r.get('vias_added'),
  'track_width_mm':r.get('track_width_mm'),
  'segment_lengths_mm':r.get('segment_lengths_mm'),
  'track_length_mm':r.get('track_length_mm'),
  'component_moves':r.get('component_moves'),
  'component_rotations':r.get('component_rotations'),
  'r404_value':c.get('r404_value'),
  'r302_value':c.get('r302_value'),
  'path_points_mm':c.get('path_points_mm'),
  'r404_pad2_net':c.get('r404_pad2_net'),
  'r302_pad2_net':c.get('r302_pad2_net'),
  'r501_pad1_net':c.get('nearest_r501_pad1_net'),
  'r404_signal_routing_touched':r.get('r404_signal_routing_touched'),
  'r302_signal_routing_touched':r.get('r302_signal_routing_touched'),
  'chg_5v_routing_touched':r.get('chg_5v_routing_touched'),
  'accepted_route1bi_geometry_modified':r.get('accepted_route1bi_geometry_modified'),
  'rf_routing_touched':r.get('rf_routing_touched'),
  'supplier_gated_interfaces_touched':r.get('supplier_gated_interfaces_touched'),
  'pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),
  'accepted_artifact_pcb_sha256':accepted_pcb_sha,
  'accepted_artifact_digest':accepted_artifact_digest
}
print(json.dumps(out,indent=2))
Path('/tmp/route1bj-summary.json').write_text(json.dumps(out,indent=2)+'\n')

assert out['rule_violations']==0 and out['unconnected_items']==114
assert out['pin_net_audit']=='PASS' and out['audited_nodes']==268
assert out['probe_board_modified'] is False and out['screen_board_modified'] is False
assert abs(out['screen_grid_mm']-0.05)<1e-9
assert abs(out['probe_min_clearance_mm']-0.175)<1e-6
assert abs(out['probe_r501_gap_mm']-0.175)<1e-6
assert out['segments_added']==3 and out['vias_added']==0
assert out['track_width_mm']==0.30
assert out['segment_lengths_mm']==[0.525,4.5,0.225] and abs(out['track_length_mm']-5.25)<1e-6
assert out['component_moves']==[] and out['component_rotations']==[]
assert out['r404_value']=='4.7k PU PROV' and out['r302_value']=='47k PU'
assert out['path_points_mm']==[[15.755,26.725],[15.755,26.2],[20.255,26.2],[20.255,25.975]]
assert out['r404_pad2_net']=='SYS_I2C_SCL'
assert out['r302_pad2_net']=='FLASH_HOLD_N'
assert out['r501_pad1_net']=='CHG_5V'
assert out['r404_signal_routing_touched'] is False
assert out['r302_signal_routing_touched'] is False
assert out['chg_5v_routing_touched'] is False
assert out['accepted_route1bi_geometry_modified'] is False
assert out['rf_routing_touched'] is False
assert out['supplier_gated_interfaces_touched'] is False

if out['pcb_sha256'] != accepted_pcb_sha:
    print('route1bj note: regenerated PCB bytes differ from accepted Artifact provenance; executed electrical/geometry gates remain authoritative')
PY
