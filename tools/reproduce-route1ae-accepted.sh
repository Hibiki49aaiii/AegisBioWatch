#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1ad-accepted.sh

python3 -X faulthandler tools/materialize-pcb-r13-route1ae-c301-gnd.py \
  --route1ad-drc-json /tmp/route1ad.json \
  --route1ad-pin-net-audit /tmp/route1ad-audit.json

kicad-cli pcb drc --format json --severity-all \
  -o /tmp/route1ae.json \
  hardware/main-board/pcb/route-r13-1ae/AegisBioWatch-MainBoard-Route1ae-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py \
  --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml \
  --pcb hardware/main-board/pcb/route-r13-1ae/AegisBioWatch-MainBoard-Route1ae-r13.kicad_pcb \
  --output /tmp/route1ae-audit.json

python3 - <<'PY'
import json
from pathlib import Path

d=json.load(open('/tmp/route1ae.json'))
a=json.load(open('/tmp/route1ae-audit.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1ae/routing-seed-r13-1ae.json'))
out={
  'rule_violations':len(d.get('violations',[])),
  'unconnected_items':len(d.get('unconnected_items',[])),
  'pin_net_audit':a.get('result'),
  'audited_nodes':a.get('audited_present_source_nodes'),
  'added_segments':r.get('track_segments_added'),
  'vias_added':r.get('vias_added'),
  'component_moves':r.get('component_moves'),
  'component_rotations':r.get('component_rotations'),
}
print(json.dumps(out,indent=2))
Path('/tmp/route1ae-summary.json').write_text(json.dumps(out,indent=2))
if out['rule_violations']!=0 or out['unconnected_items']!=144:
    raise SystemExit('route1ae DRC/ratsnest gate failed')
if out['pin_net_audit']!='PASS' or out['audited_nodes']!=268:
    raise SystemExit('route1ae audit gate failed')
if out['added_segments']!=1 or out['vias_added']!=1:
    raise SystemExit('route1ae routing scope gate failed')
if out['component_moves']!=[] or out['component_rotations']!=[]:
    raise SystemExit('route1ae placement scope gate failed')
PY
