#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1bd-accepted.sh

python3 tools/probe-pcb-r13-route1be-c4-c302-1v8.py   --route1bd-drc-json /tmp/route1bd.json   --route1bd-pin-net-audit /tmp/route1bd-audit.json   --output /tmp/route1be-probe.json

python3 -X faulthandler tools/materialize-pcb-r13-route1be-c4-c302-1v8.py   --route1bd-drc-json /tmp/route1bd.json   --route1bd-pin-net-audit /tmp/route1bd-audit.json

kicad-cli pcb drc --format json --severity-all   -o /tmp/route1be.json   hardware/main-board/pcb/route-r13-1be/AegisBioWatch-MainBoard-Route1be-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py   --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml   --pcb hardware/main-board/pcb/route-r13-1be/AegisBioWatch-MainBoard-Route1be-r13.kicad_pcb   --output /tmp/route1be-audit.json

python3 - <<'PY'
import hashlib,json
from pathlib import Path

d=json.load(open('/tmp/route1be.json'))
a=json.load(open('/tmp/route1be-audit.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1be/routing-seed-r13-1be.json'))
p=json.load(open('/tmp/route1be-probe.json'))
pcb=Path('hardware/main-board/pcb/route-r13-1be/AegisBioWatch-MainBoard-Route1be-r13.kicad_pcb')
c=r['connections']['C4.1/+1V8 to C302.1/+1V8']

accepted_pcb_sha='2fecba8eb68ad4997f7e5179d46b972cd1d8c1aebeea24b98a81f24659d07a90'
accepted_artifact_digest='sha256:6c5ced92fef8bd2060f14a2f944bba592e50fe48948aa87d93cdde682a11b029'

out={
  'rule_violations':len(d.get('violations',[])),
  'unconnected_items':len(d.get('unconnected_items',[])),
  'pin_net_audit':a.get('result'),
  'audited_nodes':a.get('audited_present_source_nodes'),
  'segments_added':r.get('track_segments_added'),
  'vias_added':r.get('vias_added'),
  'track_width_mm':r.get('track_width_mm'),
  'track_length_mm':r.get('track_length_mm'),
  'component_moves':r.get('component_moves'),
  'component_rotations':r.get('component_rotations'),
  'c4_pad1_mm':c.get('c4_pad1_mm'),
  'c302_pad1_mm':c.get('c302_pad1_mm'),
  'c4_pad1_net':c.get('c4_pad1_net'),
  'c302_pad1_net':c.get('c302_pad1_net'),
  'c4_gnd_escape_status':r.get('c4_gnd_escape_status'),
  'c302_gnd_escape_status':r.get('c302_gnd_escape_status'),
  'accepted_route1bd_geometry_modified':r.get('accepted_route1bd_geometry_modified'),
  'rf_routing_touched':r.get('rf_routing_touched'),
  'supplier_gated_interfaces_touched':r.get('supplier_gated_interfaces_touched'),
  'probe_board_modified':p.get('board_modified'),
  'pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),
  'accepted_artifact_pcb_sha256':accepted_pcb_sha,
  'accepted_artifact_digest':accepted_artifact_digest
}
print(json.dumps(out,indent=2))
Path('/tmp/route1be-summary.json').write_text(json.dumps(out,indent=2))

assert out['rule_violations']==0 and out['unconnected_items']==118
assert out['pin_net_audit']=='PASS' and out['audited_nodes']==268
assert out['segments_added']==1 and out['vias_added']==0 and out['track_width_mm']==0.30
assert out['component_moves']==[] and out['component_rotations']==[]
assert out['c4_pad1_mm']==[41.005,14.975] and out['c302_pad1_mm']==[40.305,19.585]
assert out['c4_pad1_net']=='+1V8' and out['c302_pad1_net']=='+1V8'
assert out['c4_gnd_escape_status']=='UNCHANGED' and out['c302_gnd_escape_status']=='UNCHANGED'
assert out['accepted_route1bd_geometry_modified'] is False
assert out['rf_routing_touched'] is False and out['supplier_gated_interfaces_touched'] is False
assert out['probe_board_modified'] is False

if out['pcb_sha256'] != accepted_pcb_sha:
    print('route1be note: regenerated PCB bytes differ from accepted Artifact provenance; executed electrical/geometry gates remain authoritative')
PY
