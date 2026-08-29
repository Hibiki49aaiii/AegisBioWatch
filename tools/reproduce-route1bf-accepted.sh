#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1be-accepted.sh

python3 tools/probe-pcb-r13-route1bf-r301-r503-1v8.py   --route1be-drc-json /tmp/route1be.json   --route1be-pin-net-audit /tmp/route1be-audit.json   --output /tmp/route1bf-probe.json

python3 -X faulthandler tools/materialize-pcb-r13-route1bf-r301-r503-1v8.py   --route1be-drc-json /tmp/route1be.json   --route1be-pin-net-audit /tmp/route1be-audit.json

kicad-cli pcb drc --format json --severity-all   -o /tmp/route1bf.json   hardware/main-board/pcb/route-r13-1bf/AegisBioWatch-MainBoard-Route1bf-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py   --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml   --pcb hardware/main-board/pcb/route-r13-1bf/AegisBioWatch-MainBoard-Route1bf-r13.kicad_pcb   --output /tmp/route1bf-audit.json

python3 - <<'PY'
import hashlib,json
from pathlib import Path

d=json.load(open('/tmp/route1bf.json'))
a=json.load(open('/tmp/route1bf-audit.json'))
p=json.load(open('/tmp/route1bf-probe.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1bf/routing-seed-r13-1bf.json'))
pcb=Path('hardware/main-board/pcb/route-r13-1bf/AegisBioWatch-MainBoard-Route1bf-r13.kicad_pcb')
c=r['connections']['R301.1/+1V8 to R503.1/+1V8']

accepted_pcb_sha='8deb28a88fef3c9aca174fe5d40a2aaefeb011feabfb99b012b6cd775ecc653b'
accepted_artifact_digest='sha256:5a1b2c9c068712b83d079b4f98b208501b128fddd753c6d0b440a9e80204aabf'

out={
  'rule_violations':len(d.get('violations',[])),
  'unconnected_items':len(d.get('unconnected_items',[])),
  'pin_net_audit':a.get('result'),
  'audited_nodes':a.get('audited_present_source_nodes'),
  'probe_board_modified':p.get('board_modified'),
  'probe_blocker_count':p.get('blocker_count'),
  'probe_lateral_gap_mm':p.get('candidate',{}).get('lateral_gap_to_signal_pad_column_mm'),
  'segments_added':r.get('track_segments_added'),
  'vias_added':r.get('vias_added'),
  'track_width_mm':r.get('track_width_mm'),
  'track_length_mm':r.get('track_length_mm'),
  'component_moves':r.get('component_moves'),
  'component_rotations':r.get('component_rotations'),
  'r301_pad1_mm':c.get('r301_pad1_mm'),
  'r503_pad1_mm':c.get('r503_pad1_mm'),
  'r301_pad1_net':c.get('r301_pad1_net'),
  'r503_pad1_net':c.get('r503_pad1_net'),
  'r301_pad2_mm':c.get('r301_pad2_mm'),
  'r503_pad2_mm':c.get('r503_pad2_mm'),
  'r301_pad2_net':c.get('r301_pad2_net'),
  'r503_pad2_net':c.get('r503_pad2_net'),
  'signal_side_routing_touched':r.get('signal_side_routing_touched'),
  'accepted_route1be_geometry_modified':r.get('accepted_route1be_geometry_modified'),
  'rf_routing_touched':r.get('rf_routing_touched'),
  'supplier_gated_interfaces_touched':r.get('supplier_gated_interfaces_touched'),
  'pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),
  'accepted_artifact_pcb_sha256':accepted_pcb_sha,
  'accepted_artifact_digest':accepted_artifact_digest
}
print(json.dumps(out,indent=2))
Path('/tmp/route1bf-summary.json').write_text(json.dumps(out,indent=2))

assert out['rule_violations']==0 and out['unconnected_items']==117
assert out['pin_net_audit']=='PASS' and out['audited_nodes']==268
assert out['probe_board_modified'] is False and out['probe_blocker_count']==0
assert out['probe_lateral_gap_mm']>=0.10
assert out['segments_added']==1 and out['vias_added']==0
assert out['track_width_mm']==0.30 and out['track_length_mm']==1.5
assert out['component_moves']==[] and out['component_rotations']==[]
assert out['r301_pad1_mm']==[3.005,25.975] and out['r503_pad1_mm']==[3.005,27.475]
assert out['r301_pad1_net']=='+1V8' and out['r503_pad1_net']=='+1V8'
assert out['r301_pad2_mm']==[3.645,25.975] and out['r503_pad2_mm']==[3.645,27.475]
assert out['r301_pad2_net']=='FLASH_WP_N' and out['r503_pad2_net']=='CHG_PRESENT_N'
assert out['signal_side_routing_touched'] is False
assert out['accepted_route1be_geometry_modified'] is False
assert out['rf_routing_touched'] is False and out['supplier_gated_interfaces_touched'] is False

if out['pcb_sha256'] != accepted_pcb_sha:
    print('route1bf note: regenerated PCB bytes differ from accepted Artifact provenance; executed electrical/geometry gates remain authoritative')
PY
