#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1l-accepted.sh

python3 -X faulthandler tools/materialize-pcb-r13-route1m-vbat-local.py \
  --route1l-drc-json /tmp/route1l.json \
  --route1l-pin-net-audit /tmp/route1l-audit.json

kicad-cli pcb drc --format json --severity-all \
  -o /tmp/route1m.json \
  hardware/main-board/pcb/route-r13-1m/AegisBioWatch-MainBoard-Route1m-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py \
  --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml \
  --pcb hardware/main-board/pcb/route-r13-1m/AegisBioWatch-MainBoard-Route1m-r13.kicad_pcb \
  --output /tmp/route1m-audit.json

python3 - <<'PY'
import json
from pathlib import Path

d=json.load(open('/tmp/route1m.json'))
a=json.load(open('/tmp/route1m-audit.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1m/routing-seed-r13-1m.json'))
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
Path('/tmp/route1m-summary.json').write_text(json.dumps(out,indent=2))
if out['rule_violations']!=0 or out['unconnected_items']!=164:
    raise SystemExit('route1m DRC/ratsnest gate failed')
if out['pin_net_audit']!='PASS' or out['audited_nodes']!=268:
    raise SystemExit('route1m audit gate failed')
if out['added_segments']!=3 or out['vias_added']!=1 or out['component_moves']!=[]:
    raise SystemExit('route1m routing/move scope gate failed')
rot=out['component_rotations'] or {}
if sorted(rot)!=['C106'] or rot['C106'].get('from_deg')!=90.0 or rot['C106'].get('to_deg')!=270.0:
    raise SystemExit('route1m rotation scope gate failed')
PY
