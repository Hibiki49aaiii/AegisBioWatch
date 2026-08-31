#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1bm-accepted.sh

python3 tools/probe-pcb-r13-route1bn-r403-1v8.py \
  --route1bm-drc-json /tmp/route1bm.json \
  --route1bm-pin-net-audit /tmp/route1bm-audit.json \
  --output /tmp/route1bn-probe.json

python3 -X faulthandler tools/materialize-pcb-r13-route1bn-r403-1v8.py \
  --route1bm-drc-json /tmp/route1bm.json \
  --route1bm-pin-net-audit /tmp/route1bm-audit.json \
  --exact-probe-json /tmp/route1bn-probe.json

python3 - <<'PY'
import collections,json,math
from pathlib import Path
import pcbnew

src=pcbnew.LoadBoard('hardware/main-board/pcb/route-r13-1bm/AegisBioWatch-MainBoard-Route1bm-r13.kicad_pcb')
out=pcbnew.LoadBoard('hardware/main-board/pcb/route-r13-1bn/AegisBioWatch-MainBoard-Route1bn-r13.kicad_pcb')

def mm(v): return round(float(pcbnew.ToMM(v)),6)
def xy(v): return (mm(v.x),mm(v.y))
def canon(a,b): return tuple(sorted((a,b)))
def near(a,b,tol=0.002): return math.dist(a,b)<=tol

def track_sig(item):
    if isinstance(item,pcbnew.PCB_VIA):
        return ('VIA',item.GetNetname(),xy(item.GetPosition()),mm(item.GetDrillValue()))
    return (type(item).__name__,item.GetNetname(),int(item.GetLayer()),canon(xy(item.GetStart()),xy(item.GetEnd())),mm(item.GetWidth()))

def fp_state(board):
    d={}
    for fp in board.GetFootprints():
        o=fp.GetOrientation()
        deg=float(o.AsDegrees()) if hasattr(o,'AsDegrees') else float(fp.GetOrientationDegrees())
        d[fp.GetReference()]=(xy(fp.GetPosition()),round(deg,6))
    return d

def source_hits(board):
    hits=[]
    ep=(41.005,14.975)
    for item in board.GetTracks():
        if isinstance(item,pcbnew.PCB_VIA) or item.GetLayer()!=pcbnew.F_Cu or item.GetNetname()!='+1V8':
            continue
        a,b=xy(item.GetStart()),xy(item.GetEnd())
        if (near(a,ep) or near(b,ep)) and abs(float(pcbnew.ToMM(item.GetLength()))-4.6628)<=0.002:
            hits.append((a,b,mm(item.GetWidth()),round(float(pcbnew.ToMM(item.GetLength())),6)))
    return hits

s=collections.Counter(track_sig(x) for x in src.GetTracks())
o=collections.Counter(track_sig(x) for x in out.GetTracks())
removed=list((s-o).elements())
added=list((o-s).elements())

points=[
    ((41.005,14.975),(41.005,15.65)),
    ((41.005,15.65),(39.6,15.65)),
    ((39.6,15.65),(39.6,25.975)),
    ((39.6,25.975),(40.255,25.975)),
]
expected=[('PCB_TRACK','+1V8',int(pcbnew.F_Cu),canon(a,b),0.3) for a,b in points]
assert removed==[], removed
assert collections.Counter(added)==collections.Counter(expected), added
assert all(x[0]!='VIA' for x in added)
assert fp_state(src)==fp_state(out)
before_source=source_hits(src)
after_source=source_hits(out)
assert len(before_source)==1 and len(after_source)==1, {'before':before_source,'after':after_source}

scope={
  'result':'PASS',
  'removed_items':removed,
  'added_items':added,
  'added_track_count':len(added),
  'added_via_count':0,
  'footprint_state_unchanged':True,
  'source_1v8_track_preserved':True,
  'source_1v8_track_before':before_source[0],
  'source_1v8_track_after':after_source[0],
}
Path('/tmp/route1bn-scope.json').write_text(json.dumps(scope,indent=2)+'\n')
print(json.dumps(scope,indent=2))
PY

kicad-cli pcb drc --format json --severity-all \
  -o /tmp/route1bn.json \
  hardware/main-board/pcb/route-r13-1bn/AegisBioWatch-MainBoard-Route1bn-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py \
  --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml \
  --pcb hardware/main-board/pcb/route-r13-1bn/AegisBioWatch-MainBoard-Route1bn-r13.kicad_pcb \
  --output /tmp/route1bn-audit.json

python3 - <<'PY'
import hashlib,json
from pathlib import Path

source=json.load(open('/tmp/route1bm.json'))
d=json.load(open('/tmp/route1bn.json'))
a=json.load(open('/tmp/route1bn-audit.json'))
p=json.load(open('/tmp/route1bn-probe.json'))
q=json.load(open('/tmp/route1bn-scope.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1bn/routing-seed-r13-1bn.json'))
pcb=Path('hardware/main-board/pcb/route-r13-1bn/AegisBioWatch-MainBoard-Route1bn-r13.kicad_pcb')
c=r['connections']['+1V8 source track to R403.1/+1V8']

out={
  'source_rule_violations':len(source.get('violations',[])),
  'source_unconnected_items':len(source.get('unconnected_items',[])),
  'rule_violations':len(d.get('violations',[])),
  'unconnected_items':len(d.get('unconnected_items',[])),
  'ratsnest_decrement':len(source.get('unconnected_items',[]))-len(d.get('unconnected_items',[])),
  'pin_net_audit':a.get('result'),
  'audited_nodes':a.get('audited_present_source_nodes'),
  'mismatches':a.get('mismatches',[]),
  'unexpected_pad_nets':a.get('unexpected_pad_nets',[]),
  'probe_board_modified':p.get('board_modified'),
  'probe_actual_drc_index':p.get('actual_drc_index'),
  'probe_min_clearance_mm':p.get('path',{}).get('minimum_conservative_clearance_mm'),
  'probe_nearest_unrelated_copper':p.get('path',{}).get('nearest_unrelated_copper'),
  'probe_co_limiting_clearances_mm':p.get('path',{}).get('co_limiting_clearances_mm'),
  'segments_added':r.get('track_segments_added'),
  'vias_added':r.get('vias_added'),
  'track_width_mm':r.get('track_width_mm'),
  'segment_lengths_mm':r.get('segment_lengths_mm'),
  'track_length_mm':r.get('track_length_mm'),
  'component_moves':r.get('component_moves'),
  'component_rotations':r.get('component_rotations'),
  'path_points_mm':c.get('path_points_mm'),
  'r403_pad1_net':c.get('r403_pad1_net'),
  'r403_pad2_net':c.get('r403_pad2_net'),
  'rf_routing_touched':r.get('rf_routing_touched'),
  'supplier_gated_interfaces_touched':r.get('supplier_gated_interfaces_touched'),
  'design_rule_waiver':r.get('design_rule_waiver'),
  'via_in_pad':r.get('via_in_pad'),
  'scope_result':q.get('result'),
  'scope_added_track_count':q.get('added_track_count'),
  'scope_added_via_count':q.get('added_via_count'),
  'scope_footprint_state_unchanged':q.get('footprint_state_unchanged'),
  'scope_source_track_preserved':q.get('source_1v8_track_preserved'),
  'pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),
}
print(json.dumps(out,indent=2))
Path('/tmp/route1bn-summary.json').write_text(json.dumps(out,indent=2)+'\n')

assert out['source_rule_violations']==0 and out['source_unconnected_items']==111
assert out['rule_violations']==0 and out['unconnected_items']==110 and out['ratsnest_decrement']==1
assert out['pin_net_audit']=='PASS' and out['audited_nodes']==268
assert out['mismatches']==[] and out['unexpected_pad_nets']==[]
assert out['probe_board_modified'] is False and out['probe_actual_drc_index']==13
assert abs(out['probe_min_clearance_mm']-0.26)<1e-6
assert out['probe_nearest_unrelated_copper'] in [
  {'kind':'pad','reference':'R403','pad':'2','net':'SYS_I2C_SDA'},
  {'kind':'pad','reference':'C4','pad':'2','net':'GND'},
]
assert out['probe_co_limiting_clearances_mm']=={
  'R403.2/SYS_I2C_SDA':0.26,
  'C4.2/GND':0.26,
}
assert out['segments_added']==4 and out['vias_added']==0 and out['track_width_mm']==0.30
assert out['segment_lengths_mm']==[0.675,1.405,10.325,0.655]
assert abs(out['track_length_mm']-13.06)<1e-6
assert out['component_moves']==[] and out['component_rotations']==[]
assert out['path_points_mm']==[[41.005,14.975],[41.005,15.65],[39.6,15.65],[39.6,25.975],[40.255,25.975]]
assert out['r403_pad1_net']=='+1V8' and out['r403_pad2_net']=='SYS_I2C_SDA'
assert out['rf_routing_touched'] is False and out['supplier_gated_interfaces_touched'] is False
assert out['design_rule_waiver'] is False and out['via_in_pad'] is False
assert out['scope_result']=='PASS'
assert out['scope_added_track_count']==4 and out['scope_added_via_count']==0
assert out['scope_footprint_state_unchanged'] is True and out['scope_source_track_preserved'] is True
assert r.get('output_sha256')==out['pcb_sha256']
PY
