#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1aj-accepted.sh

python3 -X faulthandler tools/materialize-pcb-r13-route1ak-q501-gnd.py \
  --route1aj-drc-json /tmp/route1aj.json \
  --route1aj-pin-net-audit /tmp/route1aj-audit.json

kicad-cli pcb drc --format json --severity-all \
  -o /tmp/route1ak.json \
  hardware/main-board/pcb/route-r13-1ak/AegisBioWatch-MainBoard-Route1ak-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py \
  --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml \
  --pcb hardware/main-board/pcb/route-r13-1ak/AegisBioWatch-MainBoard-Route1ak-r13.kicad_pcb \
  --output /tmp/route1ak-audit.json

python3 - <<'PY'
import hashlib
import json
from pathlib import Path

d=json.load(open('/tmp/route1ak.json'))
a=json.load(open('/tmp/route1ak-audit.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1ak/routing-seed-r13-1ak.json'))
pcb=Path('hardware/main-board/pcb/route-r13-1ak/AegisBioWatch-MainBoard-Route1ak-r13.kicad_pcb')
out={
  'rule_violations':len(d.get('violations',[])),
  'unconnected_items':len(d.get('unconnected_items',[])),
  'pin_net_audit':a.get('result'),
  'audited_nodes':a.get('audited_present_source_nodes'),
  'added_segments':r.get('track_segments_added'),
  'vias_added':r.get('vias_added'),
  'component_moves':r.get('component_moves'),
  'component_rotations':r.get('component_rotations'),
  'source_route1aj_sha256':r.get('source_route1aj_sha256'),
  'pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),
  'q501_value':r.get('connections',{}).get('Q501.2/GND',{}).get('q501_value'),
  'q501_1_net':r.get('connections',{}).get('Q501.2/GND',{}).get('q501_1_net'),
  'q501_3_net':r.get('connections',{}).get('Q501.2/GND',{}).get('q501_3_net'),
}
print(json.dumps(out,indent=2))
Path('/tmp/route1ak-summary.json').write_text(json.dumps(out,indent=2))
if out['rule_violations']!=0 or out['unconnected_items']!=138:
    raise SystemExit('route1ak DRC/ratsnest gate failed')
if out['pin_net_audit']!='PASS' or out['audited_nodes']!=268:
    raise SystemExit('route1ak audit gate failed')
if out['added_segments']!=1 or out['vias_added']!=1:
    raise SystemExit('route1ak routing scope gate failed')
if out['component_moves']!=[] or out['component_rotations']!=[]:
    raise SystemExit('route1ak placement scope gate failed')
if out['source_route1aj_sha256']!='87979eb6e898aceb9769eafcc7cefb643ef571d4f3f0253256bad560beca9eb1':
    raise SystemExit('route1ak accepted source byte gate failed')
if out['pcb_sha256']!='254c5861aef41cb0b083779183dbb089e4ce807b1015df2d033a3e64ba265601':
    raise SystemExit('route1ak accepted PCB byte gate failed')
if out['q501_value']!='2N7002-CLASS' or out['q501_1_net']!='CHG_SENSE_GATE' or out['q501_3_net']!='CHG_PRESENT_N':
    raise SystemExit('route1ak Q501 identity/net gate failed')
PY
