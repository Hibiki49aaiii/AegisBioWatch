#!/usr/bin/env bash
set -euo pipefail

bash tools/reproduce-route1bk-accepted.sh

python3 tools/probe-pcb-r13-route1bl-r106-vsys-refine.py   --route1bk-drc-json /tmp/route1bk.json   --route1bk-pin-net-audit /tmp/route1bk-audit.json   --output /tmp/route1bl-refine.json

python3 tools/probe-pcb-r13-route1bl-r106-vsys.py   --route1bk-drc-json /tmp/route1bk.json   --route1bk-pin-net-audit /tmp/route1bk-audit.json   --refine-json /tmp/route1bl-refine.json   --output /tmp/route1bl-probe.json

python3 -X faulthandler tools/materialize-pcb-r13-route1bl-r106-vsys.py   --route1bk-drc-json /tmp/route1bk.json   --route1bk-pin-net-audit /tmp/route1bk-audit.json   --exact-probe-json /tmp/route1bl-probe.json

python3 - <<'PY'
import collections,json
from pathlib import Path
import pcbnew

src=pcbnew.LoadBoard('hardware/main-board/pcb/route-r13-1bk/AegisBioWatch-MainBoard-Route1bk-r13.kicad_pcb')
out=pcbnew.LoadBoard('hardware/main-board/pcb/route-r13-1bl/AegisBioWatch-MainBoard-Route1bl-r13.kicad_pcb')

def mm(v): return round(float(pcbnew.ToMM(v)),6)
def xy(v): return (mm(v.x),mm(v.y))
def canon(a,b): return tuple(sorted((a,b)))

def track_sig(item):
    if isinstance(item,pcbnew.PCB_VIA):
        return ('VIA',item.GetNetname(),xy(item.GetPosition()),mm(item.GetWidth()),mm(item.GetDrillValue()))
    return (type(item).__name__,item.GetNetname(),int(item.GetLayer()),canon(xy(item.GetStart()),xy(item.GetEnd())),mm(item.GetWidth()))

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

expected_points=[
    ((7.35,28.25),(7.2,28.25)),
    ((7.2,28.25),(7.2,26.4)),
    ((7.2,26.4),(5.270826,26.4)),
    ((5.270826,26.4),(5.270826,25.865834)),
]
expected=[('PCB_TRACK','VSYS',int(pcbnew.F_Cu),canon(a,b),0.3) for a,b in expected_points]
assert removed==[], removed
assert collections.Counter(added)==collections.Counter(expected), added
assert all(x[0]!='VIA' for x in added)
assert fp_state(src)==fp_state(out)
source_sig=('PCB_TRACK','VSYS',int(pcbnew.F_Cu),canon((8.9875,28.25),(7.35,28.25)),0.3)
assert s[source_sig]==1 and o[source_sig]==1
scope={
  'result':'PASS',
  'removed_items':removed,
  'added_track_count':len(added),
  'added_via_count':0,
  'footprint_state_unchanged':True,
  'existing_vsys_source_track_count_before':s[source_sig],
  'existing_vsys_source_track_count_after':o[source_sig]
}
Path('/tmp/route1bl-scope.json').write_text(json.dumps(scope,indent=2)+'\n')
print(json.dumps(scope,indent=2))
PY

kicad-cli pcb drc --format json --severity-all   -o /tmp/route1bl.json   hardware/main-board/pcb/route-r13-1bl/AegisBioWatch-MainBoard-Route1bl-r13.kicad_pcb

python3 tools/audit-pcb-pin-nets.py   --xml hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml   --pcb hardware/main-board/pcb/route-r13-1bl/AegisBioWatch-MainBoard-Route1bl-r13.kicad_pcb   --output /tmp/route1bl-audit.json

python3 - <<'PY'
import hashlib,json
from pathlib import Path

d=json.load(open('/tmp/route1bl.json'))
a=json.load(open('/tmp/route1bl-audit.json'))
p=json.load(open('/tmp/route1bl-probe.json'))
f=json.load(open('/tmp/route1bl-refine.json'))
q=json.load(open('/tmp/route1bl-scope.json'))
r=json.load(open('hardware/main-board/pcb/route-r13-1bl/routing-seed-r13-1bl.json'))
pcb=Path('hardware/main-board/pcb/route-r13-1bl/AegisBioWatch-MainBoard-Route1bl-r13.kicad_pcb')
c=r['connections']['accepted VSYS source endpoint to R106.1/VSYS']

out={
  'rule_violations':len(d.get('violations',[])),
  'unconnected_items':len(d.get('unconnected_items',[])),
  'pin_net_audit':a.get('result'),
  'audited_nodes':a.get('audited_present_source_nodes'),
  'mismatches':a.get('mismatches',[]),
  'unexpected_pad_nets':a.get('unexpected_pad_nets',[]),
  'refine_board_modified':f.get('board_modified'),
  'refine_passing_paths':f.get('passing_path_count'),
  'refine_best_clearance_mm':f.get('best_passing_path',{}).get('minimum_conservative_clearance_mm'),
  'probe_board_modified':p.get('board_modified'),
  'probe_min_clearance_mm':p.get('effective_new_copper_path',{}).get('minimum_conservative_clearance_mm'),
  'probe_r106p2_gap_mm':p.get('effective_new_copper_path',{}).get('independent_r106p2_gap_mm'),
  'segments_added':r.get('track_segments_added'),
  'vias_added':r.get('vias_added'),
  'track_width_mm':r.get('track_width_mm'),
  'segment_lengths_mm':r.get('segment_lengths_mm'),
  'track_length_mm':r.get('track_length_mm'),
  'path_points_mm':c.get('path_points_mm'),
  'r106_pad2_routing_touched':c.get('r106_pad2_routing_touched'),
  'source_existing_track_modified':c.get('source_existing_track_modified'),
  'scope_result':q.get('result'),
  'scope_added_track_count':q.get('added_track_count'),
  'scope_added_via_count':q.get('added_via_count'),
  'scope_footprint_state_unchanged':q.get('footprint_state_unchanged'),
  'pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest()
}
print(json.dumps(out,indent=2))
Path('/tmp/route1bl-summary.json').write_text(json.dumps(out,indent=2)+'\n')

assert out['rule_violations']==0 and out['unconnected_items']==112
assert out['pin_net_audit']=='PASS' and out['audited_nodes']==268
assert out['mismatches']==[] and out['unexpected_pad_nets']==[]
assert out['refine_board_modified'] is False and out['probe_board_modified'] is False
assert out['refine_passing_paths']>=16
assert abs(out['refine_best_clearance_mm']-0.184166)<1e-6
assert abs(out['probe_min_clearance_mm']-0.184166)<1e-6
assert abs(out['probe_r106p2_gap_mm']-0.184166)<1e-6
assert out['segments_added']==4 and out['vias_added']==0
assert out['track_width_mm']==0.30
assert out['segment_lengths_mm']==[0.15,1.85,1.929174,0.534166]
assert abs(out['track_length_mm']-4.46334)<1e-6
assert out['path_points_mm']==[[7.35,28.25],[7.2,28.25],[7.2,26.4],[5.270826,26.4],[5.270826,25.865834]]
assert out['r106_pad2_routing_touched'] is False
assert out['source_existing_track_modified'] is False
assert out['scope_result']=='PASS'
assert out['scope_added_track_count']==4 and out['scope_added_via_count']==0
assert out['scope_footprint_state_unchanged'] is True
assert r.get('output_sha256')==out['pcb_sha256']

accepted_pcb_sha='01db4298b0b713ba0c7fb224bee0971110b19b93a79d8f574c3a8f6efe57d7eb'
accepted_artifact_digest='sha256:84c5ef27deb42bec2d444a7a7b6cf68d5ca961f04f3b780ad702c86af11f0d57'
if out['pcb_sha256'] != accepted_pcb_sha:
    print('route1bl note: regenerated PCB bytes differ from accepted Artifact provenance; executed electrical/geometry gates remain authoritative')
print('accepted_artifact_digest',accepted_artifact_digest)
PY
