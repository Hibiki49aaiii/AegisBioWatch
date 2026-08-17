#!/usr/bin/env bash
set -euo pipefail
bash tools/reproduce-route1z-accepted.sh
python3 -X faulthandler tools/materialize-pcb-r13-route1aa-c109-gnd.py \
  --route1z-drc-json /tmp/route1z.json \
  --route1z-pin-net-audit /tmp/route1z-audit.json
kicad-cli pcb drc --format json --severity-all \
  -o /tmp/route1aa.json \
  hardware/main-board/pcb/route-r13-1aa/AegisBioWatch-MainBoard-Route1aa-r13.kicad_pcb
python3 tools/audit-pcb-pin-nets.py \
  --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml \
  --pcb hardware/main-board/pcb/route-r13-1aa/AegisBioWatch-MainBoard-Route1aa-r13.kicad_pcb \
  --output /tmp/route1aa-audit.json
python3 - <<'PY'
import json
from pathlib import Path
d=json.load(open('/tmp/route1aa.json')); a=json.load(open('/tmp/route1aa-audit.json')); r=json.load(open('hardware/main-board/pcb/route-r13-1aa/routing-seed-r13-1aa.json'))
out={'rule_violations':len(d.get('violations',[])),'unconnected_items':len(d.get('unconnected_items',[])),'pin_net_audit':a.get('result'),'audited_nodes':a.get('audited_present_source_nodes'),'added_segments':r.get('track_segments_added'),'vias_added':r.get('vias_added'),'component_moves':r.get('component_moves'),'component_rotations':r.get('component_rotations')}
print(json.dumps(out,indent=2)); Path('/tmp/route1aa-summary.json').write_text(json.dumps(out,indent=2))
if out['rule_violations']!=0 or out['unconnected_items']!=148: raise SystemExit('route1aa DRC/ratsnest gate failed')
if out['pin_net_audit']!='PASS' or out['audited_nodes']!=268: raise SystemExit('route1aa audit gate failed')
if out['added_segments']!=1 or out['vias_added']!=1: raise SystemExit('route1aa routing scope gate failed')
if out['component_moves']!=[] or out['component_rotations']!=[]: raise SystemExit('route1aa placement scope gate failed')
PY
