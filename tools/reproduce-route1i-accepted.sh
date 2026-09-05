#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1h-accepted.sh

python3 -X faulthandler tools/materialize-pcb-r13-route1i-pvss-trees.py \
  --route1h-drc-json /tmp/route1h.json \
  --route1h-pin-net-audit /tmp/route1h-audit.json

kicad-cli pcb drc --format json --severity-all \
  -o /tmp/route1i.json \
  hardware/main-board/pcb/route-r13-1i/AegisBioWatch-MainBoard-Route1i-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py \
  --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml \
  --pcb hardware/main-board/pcb/route-r13-1i/AegisBioWatch-MainBoard-Route1i-r13.kicad_pcb \
  --output /tmp/route1i-audit.json

python3 - <<'PY'
import json
from pathlib import Path

d=json.load(open('/tmp/route1i.json'))
a=json.load(open('/tmp/route1i-audit.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1i/routing-seed-r13-1i.json'))
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
Path('/tmp/route1i-summary.json').write_text(json.dumps(out,indent=2))
if out['rule_violations']!=0 or out['unconnected_items']!=172:
    raise SystemExit('route1i DRC/ratsnest gate failed')
if out['pin_net_audit']!='PASS' or out['audited_nodes']!=268:
    raise SystemExit('route1i audit gate failed')
if out['added_segments']!=6 or out['vias_added']!=2 or out['component_moves']!=[]:
    raise SystemExit('route1i routing scope gate failed')
rot=out['component_rotations'] or {}
if sorted(rot)!=['NT101'] or rot['NT101'].get('from_deg')!=0.0 or rot['NT101'].get('to_deg')!=180.0:
    raise SystemExit('route1i rotation scope gate failed')
PY
