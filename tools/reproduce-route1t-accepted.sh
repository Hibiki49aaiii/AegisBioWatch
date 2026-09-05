#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1s-accepted.sh

python3 -X faulthandler tools/materialize-pcb-r13-route1t-r106-vsys.py \
  --route1s-drc-json /tmp/route1s.json \
  --route1s-pin-net-audit /tmp/route1s-audit.json

kicad-cli pcb drc --format json --severity-all \
  -o /tmp/route1t.json \
  hardware/main-board/pcb/route-r13-1t/AegisBioWatch-MainBoard-Route1t-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py \
  --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml \
  --pcb hardware/main-board/pcb/route-r13-1t/AegisBioWatch-MainBoard-Route1t-r13.kicad_pcb \
  --output /tmp/route1t-audit.json

python3 - <<'PY'
import json
from pathlib import Path

d=json.load(open('/tmp/route1t.json'))
a=json.load(open('/tmp/route1t-audit.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1t/routing-seed-r13-1t.json'))
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
Path('/tmp/route1t-summary.json').write_text(json.dumps(out,indent=2))
if out['rule_violations']!=0 or out['unconnected_items']!=155:
    raise SystemExit('route1t DRC/ratsnest gate failed')
if out['pin_net_audit']!='PASS' or out['audited_nodes']!=268:
    raise SystemExit('route1t audit gate failed')
if out['added_segments']!=4 or out['vias_added']!=1:
    raise SystemExit('route1t routing scope gate failed')
if out['component_moves']!=[] or out['component_rotations']!=[]:
    raise SystemExit('route1t placement scope gate failed')
PY
