#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1r-accepted.sh

python3 -X faulthandler tools/materialize-pcb-r13-route1s-r105-vsys.py \
  --route1r-drc-json /tmp/route1r.json \
  --route1r-pin-net-audit /tmp/route1r-audit.json

kicad-cli pcb drc --format json --severity-all \
  -o /tmp/route1s.json \
  hardware/main-board/pcb/route-r13-1s/AegisBioWatch-MainBoard-Route1s-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py \
  --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml \
  --pcb hardware/main-board/pcb/route-r13-1s/AegisBioWatch-MainBoard-Route1s-r13.kicad_pcb \
  --output /tmp/route1s-audit.json

python3 - <<'PY'
import json
from pathlib import Path

d=json.load(open('/tmp/route1s.json'))
a=json.load(open('/tmp/route1s-audit.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1s/routing-seed-r13-1s.json'))
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
Path('/tmp/route1s-summary.json').write_text(json.dumps(out,indent=2))
if out['rule_violations']!=0 or out['unconnected_items']!=156:
    raise SystemExit('route1s DRC/ratsnest gate failed')
if out['pin_net_audit']!='PASS' or out['audited_nodes']!=268:
    raise SystemExit('route1s audit gate failed')
if out['added_segments']!=5 or out['vias_added']!=1:
    raise SystemExit('route1s routing scope gate failed')
if out['component_moves']!=[] or out['component_rotations']!=[]:
    raise SystemExit('route1s placement scope gate failed')
PY
