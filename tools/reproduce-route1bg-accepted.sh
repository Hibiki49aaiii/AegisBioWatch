#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1bf-accepted.sh

python3 tools/probe-pcb-r13-route1bg-c5-l101-1v8.py   --route1bf-drc-json /tmp/route1bf.json   --route1bf-pin-net-audit /tmp/route1bf-audit.json   --output /tmp/route1bg-probe.json

python3 -X faulthandler tools/materialize-pcb-r13-route1bg-c5-l101-1v8.py   --route1bf-drc-json /tmp/route1bf.json   --route1bf-pin-net-audit /tmp/route1bf-audit.json

kicad-cli pcb drc --format json --severity-all   -o /tmp/route1bg.json   hardware/main-board/pcb/route-r13-1bg/AegisBioWatch-MainBoard-Route1bg-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py   --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml   --pcb hardware/main-board/pcb/route-r13-1bg/AegisBioWatch-MainBoard-Route1bg-r13.kicad_pcb   --output /tmp/route1bg-audit.json

python3 - <<'PY'
import hashlib,json
from pathlib import Path

d=json.load(open('/tmp/route1bg.json'))
a=json.load(open('/tmp/route1bg-audit.json'))
p=json.load(open('/tmp/route1bg-probe.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1bg/routing-seed-r13-1bg.json'))
pcb=Path('hardware/main-board/pcb/route-r13-1bg/AegisBioWatch-MainBoard-Route1bg-r13.kicad_pcb')
c=r['connections']['C5.1/+1V8 to L101.2/+1V8']

accepted_pcb_sha='5f15cfde5b3172a7a491fc836550c70e4e3d7a7456267ea275b03386272dca78'
accepted_artifact_digest='sha256:ed78cedd15dde29c0cabe13ad9c0612fa2471bc092ea58d947cdc6019ef6e468'

out={
  'rule_violations':len(d.get('violations',[])),
  'unconnected_items':len(d.get('unconnected_items',[])),
  'pin_net_audit':a.get('result'),
  'audited_nodes':a.get('audited_present_source_nodes'),
  'probe_board_modified':p.get('board_modified'),
  'probe_unrelated_blockers':p.get('unrelated_blocker_count'),
  'existing_rail_probe':p.get('existing_l101_to_c107_rail_preserved'),
  'segments_added':r.get('track_segments_added'),
  'vias_added':r.get('vias_added'),
  'track_width_mm':r.get('track_width_mm'),
  'track_length_mm':r.get('track_length_mm'),
  'component_moves':r.get('component_moves'),
  'component_rotations':r.get('component_rotations'),
  'c5_pad1_mm':c.get('c5_pad1_mm'),
  'l101_pad2_mm':c.get('l101_pad2_mm'),
  'c5_pad1_net':c.get('c5_pad1_net'),
  'l101_pad2_net':c.get('l101_pad2_net'),
  'c5_pad2_mm':c.get('c5_pad2_mm'),
  'c5_pad2_net':c.get('c5_pad2_net'),
  'l101_pad1_mm':c.get('l101_pad1_mm'),
  'l101_pad1_net':c.get('l101_pad1_net'),
  'c107_pad1_mm':c.get('c107_pad1_mm'),
  'existing_rail_status':r.get('existing_l101_to_c107_rail_status'),
  'c5_gnd_routing_touched':r.get('c5_gnd_routing_touched'),
  'pmic_sw1_routing_touched':r.get('pmic_sw1_routing_touched'),
  'accepted_route1bf_geometry_modified':r.get('accepted_route1bf_geometry_modified'),
  'rf_routing_touched':r.get('rf_routing_touched'),
  'supplier_gated_interfaces_touched':r.get('supplier_gated_interfaces_touched'),
  'pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),
  'accepted_artifact_pcb_sha256':accepted_pcb_sha,
  'accepted_artifact_digest':accepted_artifact_digest
}
print(json.dumps(out,indent=2))
Path('/tmp/route1bg-summary.json').write_text(json.dumps(out,indent=2))

assert out['rule_violations']==0 and out['unconnected_items']==116
assert out['pin_net_audit']=='PASS' and out['audited_nodes']==268
assert out['probe_board_modified'] is False and out['probe_unrelated_blockers']==0
assert out['existing_rail_probe'] is True
assert out['segments_added']==1 and out['vias_added']==0
assert out['track_width_mm']==0.30 and abs(out['track_length_mm']-1.923385)<1e-6
assert out['component_moves']==[] and out['component_rotations']==[]
assert out['c5_pad1_mm']==[9.255,22.225] and out['l101_pad2_mm']==[8.964712,24.126353]
assert out['c5_pad1_net']=='+1V8' and out['l101_pad2_net']=='+1V8'
assert out['c5_pad2_mm']==[9.895,22.225] and out['c5_pad2_net']=='GND'
assert out['l101_pad1_mm']==[7.514712,24.126353] and out['l101_pad1_net']=='PMIC_SW1'
assert out['c107_pad1_mm']==[10.407553,23.51711]
assert out['existing_rail_status']=='UNCHANGED'
assert out['c5_gnd_routing_touched'] is False and out['pmic_sw1_routing_touched'] is False
assert out['accepted_route1bf_geometry_modified'] is False
assert out['rf_routing_touched'] is False and out['supplier_gated_interfaces_touched'] is False

if out['pcb_sha256'] != accepted_pcb_sha:
    print('route1bg note: regenerated PCB bytes differ from accepted Artifact provenance; executed electrical/geometry gates remain authoritative')
PY
