#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1bg-accepted.sh

set +e
python3 tools/probe-pcb-r13-route1bh-c301-r404-1v8.py   --route1bg-drc-json /tmp/route1bg.json   --route1bg-pin-net-audit /tmp/route1bg-audit.json   --output /tmp/route1bh-rejected-probe.json
rc=$?
set -e

if [ "$rc" -eq 0 ]; then
  echo "route1bh rejection reproduction unexpectedly passed" >&2
  exit 1
fi

python3 - <<'PY'
import json
p=json.load(open('/tmp/route1bh-rejected-probe.json'))
assert p['source_gate']=={
  'rule_violations':0,
  'unconnected_items':116,
  'pin_net_audit':'PASS',
  'audited_nodes':268
}
assert p['board_modified'] is False
assert p['C301_value']=='100nF'
assert p['R404_value']=='4.7k PU PROV'
assert p['candidate']['start_mm']==[13.755,23.725]
assert p['candidate']['end_mm']==[15.755,26.725]
assert p['minimum_conservative_unrelated_clearance_mm'] < 0.100
n=p['nearest_unrelated_copper']
assert n[0]['kind']=='pad' and n[0]['reference']=='C105' and n[0]['pad']=='1'
assert n[0]['net']=='VBUSOUT_SENSE'
assert abs(n[0]['conservative_clearance_mm'] - (-0.15)) < 1e-6
assert any(x.get('kind')=='pad' and x.get('reference')=='C301' and x.get('pad')=='2'
           and x.get('conservative_clearance_mm',999) < 0.100 for x in n)
print('route1bh rejection reproduced: PASS')
PY
