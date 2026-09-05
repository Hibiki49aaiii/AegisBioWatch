#!/usr/bin/env bash
set -euo pipefail
bash tools/reproduce-route1w-accepted.sh
python3 -X faulthandler tools/materialize-pcb-r13-route1x-i2c-pullup-feed.py \
  --route1w-drc-json /tmp/route1w.json \
  --route1w-pin-net-audit /tmp/route1w-audit.json
kicad-cli pcb drc --format json --severity-all \
  -o /tmp/route1x.json \
  hardware/main-board/pcb/route-r13-1x/AegisBioWatch-MainBoard-Route1x-r13.kicad_pcb
python3 tools/audit-pcb-pin-nets.py \
  --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml \
  --pcb hardware/main-board/pcb/route-r13-1x/AegisBioWatch-MainBoard-Route1x-r13.kicad_pcb \
  --output /tmp/route1x-audit.json
python3 - <<'PY'
import json
from pathlib import Path
d=json.load(open('/tmp/route1x.json')); a=json.load(open('/tmp/route1x-audit.json')); r=json.load(open('hardware/main-board/pcb/route-r13-1x/routing-seed-r13-1x.json'))
out={'rule_violations':len(d.get('violations',[])),'unconnected_items':len(d.get('unconnected_items',[])),'pin_net_audit':a.get('result'),'audited_nodes':a.get('audited_present_source_nodes'),'added_segments':r.get('track_segments_added'),'vias_added':r.get('vias_added'),'component_moves':r.get('component_moves'),'component_rotations':r.get('component_rotations')}
print(json.dumps(out,indent=2)); Path('/tmp/route1x-summary.json').write_text(json.dumps(out,indent=2))
if out['rule_violations']!=0 or out['unconnected_items']!=151: raise SystemExit('route1x DRC/ratsnest gate failed')
if out['pin_net_audit']!='PASS' or out['audited_nodes']!=268: raise SystemExit('route1x audit gate failed')
if out['added_segments']!=4 or out['vias_added']!=0: raise SystemExit('route1x routing scope gate failed')
if out['component_moves']!=[] or out['component_rotations']!=[]: raise SystemExit('route1x placement scope gate failed')
PY
