#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1p-accepted.sh

python3 -X faulthandler tools/materialize-pcb-r13-route1q-vset2-local.py \
  --route1p-drc-json /tmp/route1p.json \
  --route1p-pin-net-audit /tmp/route1p-audit.json

kicad-cli pcb drc --format json --severity-all \
  -o /tmp/route1q.json \
  hardware/main-board/pcb/route-r13-1q/AegisBioWatch-MainBoard-Route1q-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py \
  --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml \
  --pcb hardware/main-board/pcb/route-r13-1q/AegisBioWatch-MainBoard-Route1q-r13.kicad_pcb \
  --output /tmp/route1q-audit.json

python3 - <<'PY'
import json
from pathlib import Path

d=json.load(open('/tmp/route1q.json'))
a=json.load(open('/tmp/route1q-audit.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1q/routing-seed-r13-1q.json'))
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
Path('/tmp/route1q-summary.json').write_text(json.dumps(out,indent=2))
if out['rule_violations']!=0 or out['unconnected_items']!=158:
    raise SystemExit('route1q DRC/ratsnest gate failed')
if out['pin_net_audit']!='PASS' or out['audited_nodes']!=268:
    raise SystemExit('route1q audit gate failed')
if out['added_segments']!=4 or out['vias_added']!=1:
    raise SystemExit('route1q routing scope gate failed')
if out['component_moves']!=[] or out['component_rotations']!=[]:
    raise SystemExit('route1q placement scope gate failed')
PY
