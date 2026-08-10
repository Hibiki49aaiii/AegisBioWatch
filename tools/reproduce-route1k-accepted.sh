#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1j-accepted.sh

python3 -X faulthandler tools/materialize-pcb-r13-route1k-c114-vsys.py \
  --route1j-drc-json /tmp/route1j.json \
  --route1j-pin-net-audit /tmp/route1j-audit.json

kicad-cli pcb drc --format json --severity-all \
  -o /tmp/route1k.json \
  hardware/main-board/pcb/route-r13-1k/AegisBioWatch-MainBoard-Route1k-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py \
  --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml \
  --pcb hardware/main-board/pcb/route-r13-1k/AegisBioWatch-MainBoard-Route1k-r13.kicad_pcb \
  --output /tmp/route1k-audit.json

python3 - <<'PY'
import json
from pathlib import Path

d=json.load(open('/tmp/route1k.json'))
a=json.load(open('/tmp/route1k-audit.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1k/routing-seed-r13-1k.json'))
out={
  'rule_violations':len(d.get('violations',[])),
  'unconnected_items':len(d.get('unconnected_items',[])),
  'pin_net_audit':a.get('result'),
  'audited_nodes':a.get('audited_present_source_nodes'),
  'added_segments':r.get('track_segments_added'),
  'vias_added':r.get('vias_added'),
  'component_moves':r.get('component_moves'),
}
print(json.dumps(out,indent=2))
Path('/tmp/route1k-summary.json').write_text(json.dumps(out,indent=2))
if out['rule_violations']!=0 or out['unconnected_items']!=168:
    raise SystemExit('route1k DRC/ratsnest gate failed')
if out['pin_net_audit']!='PASS' or out['audited_nodes']!=268:
    raise SystemExit('route1k audit gate failed')
if out['added_segments']!=4 or out['vias_added']!=1:
    raise SystemExit('route1k routing scope gate failed')
moves=out['component_moves'] or []
if len(moves)!=1 or moves[0].get('ref')!='C114':
    raise SystemExit('route1k placement scope gate failed')
PY
