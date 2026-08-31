#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1bl-accepted.sh

python3 tools/probe-pcb-r13-route1bm-r305-u4-vsys-haptic.py \
  --route1bl-drc-json /tmp/route1bl.json \
  --route1bl-pin-net-audit /tmp/route1bl-audit.json \
  --output /tmp/route1bm-probe.json

python3 -X faulthandler tools/materialize-pcb-r13-route1bm-r305-u4-vsys-haptic.py \
  --route1bl-drc-json /tmp/route1bl.json \
  --route1bl-pin-net-audit /tmp/route1bl-audit.json \
  --exact-probe-json /tmp/route1bm-probe.json

python3 - <<'PY'
import collections,json
from pathlib import Path
import pcbnew

src=pcbnew.LoadBoard('hardware/main-board/pcb/route-r13-1bl/AegisBioWatch-MainBoard-Route1bl-r13.kicad_pcb')
out=pcbnew.LoadBoard('hardware/main-board/pcb/route-r13-1bm/AegisBioWatch-MainBoard-Route1bm-r13.kicad_pcb')

def mm(v): return round(float(pcbnew.ToMM(v)),6)
def xy(v): return (mm(v.x),mm(v.y))
def canon(a,b): return tuple(sorted((a,b)))

def track_sig(item):
    if isinstance(item,pcbnew.PCB_VIA):
        return ('VIA',item.GetNetname(),xy(item.GetPosition()),mm(item.GetDrillValue()))
    return (type(item).__name__,item.GetNetname(),int(item.GetLayer()),canon(xy(item.GetStart()),xy(item.GetEnd())),mm(item.GetWidth()))

def near(a,b,tol=0.002):
    return ((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5 <= tol

def bypass_hits(board,a,b):
    hits=[]
    for item in board.GetTracks():
        if isinstance(item,pcbnew.PCB_VIA) or item.GetLayer()!=pcbnew.F_Cu:
            continue
        if item.GetNetname()!='VSYS_HAPTIC' or abs(mm(item.GetWidth())-0.3)>1e-6:
            continue
        p,q=xy(item.GetStart()),xy(item.GetEnd())
        if (near(p,a) and near(q,b)) or (near(p,b) and near(q,a)):
            hits.append((p,q))
    return hits

def fp_state(board):
    d={}
    for fp in board.GetFootprints():
        o=fp.GetOrientation()
        deg=float(o.AsDegrees()) if hasattr(o,'AsDegrees') else float(fp.GetOrientationDegrees())
        d[fp.GetReference()]=(xy(fp.GetPosition()),round(deg,6))
    return d

s=collections.Counter(track_sig(x) for x in src.GetTracks())
o=collections.Counter(track_sig(x) for x in out.GetTracks())
removed=list((s-o).elements())
added=list((o-s).elements())

points=[
    ((31.315,18.595),(31.315,17.5)),
    ((31.315,17.5),(25.0,17.5)),
    ((25.0,17.5),(25.0,13.4)),
    ((25.0,13.4),(23.005,13.4)),
]
expected=[('PCB_TRACK','VSYS_HAPTIC',int(pcbnew.F_Cu),canon(a,b),0.3) for a,b in points]
assert removed==[], removed
assert collections.Counter(added)==collections.Counter(expected), added
assert all(x[0]!='VIA' for x in added)
assert fp_state(src)==fp_state(out)

bypass=[
    ((6.805,22.335),(6.805,21.65)),
    ((6.805,21.65),(16.005,21.65)),
    ((16.005,21.65),(16.005,23.725)),
]
bypass_evidence=[]
for a,b in bypass:
    before=bypass_hits(src,a,b)
    after=bypass_hits(out,a,b)
    assert len(before)==1 and len(after)==1, {'expected':[a,b],'before':before,'after':after}
    bypass_evidence.append({'expected':[a,b],'before':before[0],'after':after[0]})

scope={
  'result':'PASS',
  'removed_items':removed,
  'added_items':added,
  'added_track_count':len(added),
  'added_via_count':0,
  'footprint_state_unchanged':True,
  'accepted_route1bk_bypass_segments_preserved':True,
  'accepted_route1bk_bypass_tolerance_mm':0.002,
  'accepted_route1bk_bypass_evidence':bypass_evidence,
}
Path('/tmp/route1bm-scope.json').write_text(json.dumps(scope,indent=2)+'\n')
print(json.dumps(scope,indent=2))
PY

kicad-cli pcb drc --format json --severity-all \
  -o /tmp/route1bm.json \
  hardware/main-board/pcb/route-r13-1bm/AegisBioWatch-MainBoard-Route1bm-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py \
  --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml \
  --pcb hardware/main-board/pcb/route-r13-1bm/AegisBioWatch-MainBoard-Route1bm-r13.kicad_pcb \
  --output /tmp/route1bm-audit.json

python3 - <<'PY'
import hashlib,json
from pathlib import Path

d=json.load(open('/tmp/route1bm.json'))
a=json.load(open('/tmp/route1bm-audit.json'))
p=json.load(open('/tmp/route1bm-probe.json'))
q=json.load(open('/tmp/route1bm-scope.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1bm/routing-seed-r13-1bm.json'))
pcb=Path('hardware/main-board/pcb/route-r13-1bm/AegisBioWatch-MainBoard-Route1bm-r13.kicad_pcb')
c=r['connections']['R305.2/VSYS_HAPTIC to U4.10/VSYS_HAPTIC']

out={
  'rule_violations':len(d.get('violations',[])),
  'unconnected_items':len(d.get('unconnected_items',[])),
  'pin_net_audit':a.get('result'),
  'audited_nodes':a.get('audited_present_source_nodes'),
  'mismatches':a.get('mismatches',[]),
  'unexpected_pad_nets':a.get('unexpected_pad_nets',[]),
  'probe_board_modified':p.get('board_modified'),
  'probe_min_clearance_mm':p.get('path',{}).get('minimum_conservative_clearance_mm'),
  'probe_nearest_unrelated_copper':p.get('path',{}).get('nearest_unrelated_copper'),
  'segments_added':r.get('track_segments_added'),
  'vias_added':r.get('vias_added'),
  'track_width_mm':r.get('track_width_mm'),
  'segment_lengths_mm':r.get('segment_lengths_mm'),
  'track_length_mm':r.get('track_length_mm'),
  'component_moves':r.get('component_moves'),
  'component_rotations':r.get('component_rotations'),
  'path_points_mm':c.get('path_points_mm'),
  'r305_pad1_net':c.get('r305_pad1_net'),
  'r305_pad2_net':c.get('r305_pad2_net'),
  'u4_pad10_net':c.get('u4_pad10_net'),
  'accepted_route1bk_bypass_geometry_modified':r.get('accepted_route1bk_bypass_geometry_modified'),
  'rf_routing_touched':r.get('rf_routing_touched'),
  'supplier_gated_interfaces_touched':r.get('supplier_gated_interfaces_touched'),
  'design_rule_waiver':r.get('design_rule_waiver'),
  'via_in_pad':r.get('via_in_pad'),
  'scope_result':q.get('result'),
  'scope_added_track_count':q.get('added_track_count'),
  'scope_added_via_count':q.get('added_via_count'),
  'scope_footprint_state_unchanged':q.get('footprint_state_unchanged'),
  'scope_bypass_preserved':q.get('accepted_route1bk_bypass_segments_preserved'),
  'pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),
}
print(json.dumps(out,indent=2))
Path('/tmp/route1bm-summary.json').write_text(json.dumps(out,indent=2)+'\n')

assert out['rule_violations']==0 and out['unconnected_items']==111
assert out['pin_net_audit']=='PASS' and out['audited_nodes']==268
assert out['mismatches']==[] and out['unexpected_pad_nets']==[]
assert out['probe_board_modified'] is False
assert abs(out['probe_min_clearance_mm']-0.20)<1e-6
assert out['probe_nearest_unrelated_copper']=={'kind':'pad','reference':'U4','pad':'9','net':'HAPTIC_OUT_N'}
assert out['segments_added']==4 and out['vias_added']==0
assert out['track_width_mm']==0.30
assert out['segment_lengths_mm']==[1.095,6.315,4.1,1.995]
assert abs(out['track_length_mm']-13.505)<1e-6
assert out['component_moves']==[] and out['component_rotations']==[]
assert out['path_points_mm']==[[31.315,18.595],[31.315,17.5],[25.0,17.5],[25.0,13.4],[23.005,13.4]]
assert out['r305_pad1_net']=='VSYS'
assert out['r305_pad2_net']=='VSYS_HAPTIC'
assert out['u4_pad10_net']=='VSYS_HAPTIC'
assert out['accepted_route1bk_bypass_geometry_modified'] is False
assert out['rf_routing_touched'] is False
assert out['supplier_gated_interfaces_touched'] is False
assert out['design_rule_waiver'] is False
assert out['via_in_pad'] is False
assert out['scope_result']=='PASS'
assert out['scope_added_track_count']==4 and out['scope_added_via_count']==0
assert out['scope_footprint_state_unchanged'] is True
assert out['scope_bypass_preserved'] is True
assert r.get('output_sha256')==out['pcb_sha256']
PY
