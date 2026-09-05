#!/usr/bin/env python3
"""Broad read-only screening of ordinary route-1bg ratsnest pairs for route-1bi."""
from __future__ import annotations
import argparse, hashlib, json, math, re
from pathlib import Path
import pcbnew  # type: ignore

ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bg'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1bg-r13.kicad_pcb'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1bg.json'
WIDTH=0.30
RULE=0.10
MAX_LENGTH=12.0
EPS=1e-9

EXCLUDED_REFS={'U1','J3','J5','J6','J7','C7','C8','C9','C10','C11','C12','C401'}
EXCLUDED_NETS={
 'RF_A','RF_B','RF_ANT','RF_MCU','NRF_DECA_RF','BIO_SW','DISP_SW',
 'CHG_5V','LDO2_IN','PMIC_SW1','PMIC_SW2','PVSS1_LOCAL','SYS_I2C_SCL'
}
EXCLUDED_NET_PREFIXES=('NRF_XC','NRF_XL')

PAD_RE=re.compile(r'^Pad\s+(\S+)\s+\[([^\]]+)\]\s+of\s+(\S+)\s+on\s+Top_layer$')
NET_RE=re.compile(r'\[([^\]]+)\]')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def xy(v): return (round(mm(v.x),6),round(mm(v.y),6))
def bbox(i):
 b=i.GetBoundingBox()
 return (mm(b.GetX()),mm(b.GetY()),mm(b.GetRight()),mm(b.GetBottom()))
def orient(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def onseg(a,b,p):
 return min(a[0],b[0])-EPS<=p[0]<=max(a[0],b[0])+EPS and min(a[1],b[1])-EPS<=p[1]<=max(a[1],b[1])+EPS and abs(orient(a,b,p))<=EPS
def intersect(a,b,c,d):
 o1,o2,o3,o4=orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
 if ((o1>EPS and o2<-EPS) or (o1<-EPS and o2>EPS)) and ((o3>EPS and o4<-EPS) or (o3<-EPS and o4>EPS)): return True
 return onseg(a,b,c) or onseg(a,b,d) or onseg(c,d,a) or onseg(c,d,b)
def pseg(p,a,b):
 vx,vy=b[0]-a[0],b[1]-a[1]; wx,wy=p[0]-a[0],p[1]-a[1]; vv=vx*vx+vy*vy
 if vv<=EPS: return math.dist(p,a)
 t=max(0,min(1,(wx*vx+wy*vy)/vv)); q=(a[0]+t*vx,a[1]+t*vy)
 return math.dist(p,q)
def sseg(a,b,c,d):
 if intersect(a,b,c,d): return 0.0
 return min(pseg(a,c,d),pseg(b,c,d),pseg(c,a,b),pseg(d,a,b))
def pinrect(p,r): return r[0]-EPS<=p[0]<=r[2]+EPS and r[1]-EPS<=p[1]<=r[3]+EPS
def prect(p,r):
 dx=max(r[0]-p[0],0,p[0]-r[2]); dy=max(r[1]-p[1],0,p[1]-r[3]); return math.hypot(dx,dy)
def srect(a,b,r):
 if pinrect(a,r) or pinrect(b,r): return 0.0
 cs=[(r[0],r[1]),(r[2],r[1]),(r[2],r[3]),(r[0],r[3])]
 if any(intersect(a,b,c,d) for c,d in zip(cs,cs[1:]+cs[:1])): return 0.0
 return min(prect(a,r),prect(b,r),*(pseg(c,a,b) for c in cs))

def endpoint(desc,pos):
 m=PAD_RE.match(desc)
 if m:
  return {'kind':'pad','pad':m.group(1),'net':m.group(2),'ref':m.group(3),'description':desc,'pos':[pos['x'],pos['y']]}
 nm=NET_RE.search(desc)
 return {'kind':'track' if desc.startswith('Track ') else 'other','pad':None,'net':nm.group(1) if nm else None,'ref':None,'description':desc,'pos':[pos['x'],pos['y']]}

def excluded(c):
 a,b=c['a'],c['b']; net=c['net']
 if net in EXCLUDED_NETS or any(net.startswith(p) for p in EXCLUDED_NET_PREFIXES): return 'excluded_net'
 if a['ref'] in EXCLUDED_REFS or b['ref'] in EXCLUDED_REFS: return 'excluded_ref'
 if a['kind']=='other' or b['kind']=='other': return 'unsupported_endpoint'
 if 'Top_layer' not in a['description'] or 'Top_layer' not in b['description']: return 'non_top_layer'
 if a['ref'] and b['ref'] and a['ref']==b['ref'] and a['pad']==b['pad']: return 'duplicate_terminal_same_component'
 if c['length_mm']>MAX_LENGTH: return 'too_long'
 return None

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--route1bg-drc-json',required=True)
 ap.add_argument('--route1bg-pin-net-audit',required=True)
 ap.add_argument('--output',required=True)
 args=ap.parse_args()
 rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
 if rep.get('output_sha256')!=srcsha: raise SystemExit('broad screen source SHA gate failed')
 d=loadj(args.route1bg_drc_json); au=loadj(args.route1bg_pin_net_audit)
 if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=116: raise SystemExit('broad screen DRC gate failed')
 if au.get('result')!='PASS' or au.get('audited_present_source_nodes')!=268: raise SystemExit('broad screen audit gate failed')

 raw=[]
 for idx,u in enumerate(d['unconnected_items']):
  if len(u.get('items',[]))!=2: continue
  x,y=u['items']
  a=endpoint(x['description'],x['pos']); b=endpoint(y['description'],y['pos'])
  if not a['net'] or a['net']!=b['net']: continue
  dist=math.dist(a['pos'],b['pos'])
  c={'drc_index':idx,'net':a['net'],'a':a,'b':b,'length_mm':round(dist,6)}
  c['exclusion_reason']=excluded(c)
  raw.append(c)

 board=pcbnew.LoadBoard(str(SRC_PCB))
 evaluated=[]
 for c in raw:
  if c['exclusion_reason']: continue
  A=tuple(c['a']['pos']); B=tuple(c['b']['pos']); net=c['net']; half=WIDTH/2
  hits=[]
  for fp in board.GetFootprints():
   for p in fp.Pads():
    if not p.IsOnLayer(pcbnew.F_Cu) or p.GetNetname()==net: continue
    r=bbox(p); clr=srect(A,B,r)-half
    hits.append({'kind':'pad','reference':fp.GetReference(),'pad':str(p.GetNumber()),'net':p.GetNetname(),'clearance_mm':round(clr,6)})
  for item in board.GetTracks():
   n=item.GetNetname() if hasattr(item,'GetNetname') else ''
   if n==net: continue
   if isinstance(item,pcbnew.PCB_VIA):
    p=xy(item.GetPosition()); r=bbox(item); radius=max(r[2]-r[0],r[3]-r[1])/2
    clr=pseg(p,A,B)-radius-half
    hits.append({'kind':'via','net':n,'position_mm':list(p),'clearance_mm':round(clr,6)})
   else:
    if item.GetLayer()!=pcbnew.F_Cu: continue
    x=xy(item.GetStart()); y=xy(item.GetEnd()); w=mm(item.GetWidth())
    clr=sseg(A,B,x,y)-w/2-half
    hits.append({'kind':'track','net':n,'start_mm':list(x),'end_mm':list(y),'width_mm':round(w,6),'clearance_mm':round(clr,6)})
  hits.sort(key=lambda z:z['clearance_mm'])
  minc=hits[0]['clearance_mm'] if hits else 999.0
  evaluated.append({**c,'width_mm':WIDTH,'minimum_conservative_clearance_mm':minc,'rule_pass':minc+1e-6>=RULE,'nearest_unrelated_copper':hits[:6]})

 passing=[x for x in evaluated if x['rule_pass']]
 passing.sort(key=lambda x:(x['length_mm'],-x['minimum_conservative_clearance_mm']))
 failing=[x for x in evaluated if not x['rule_pass']]
 failing.sort(key=lambda x:(-x['minimum_conservative_clearance_mm'],x['length_mm']))
 excluded_rows=[x for x in raw if x['exclusion_reason']]

 out={
  'revision':'r13-route1bi-broad-direct-screen',
  'source_route1bg_sha256':srcsha,
  'source_gate':{'rule_violations':0,'unconnected_items':116,'pin_net_audit':'PASS','audited_nodes':268},
  'board_modified':False,
  'track_width_mm':WIDTH,'rule_clearance_mm':RULE,'max_length_mm':MAX_LENGTH,
  'raw_pair_count':len(raw),'evaluated_count':len(evaluated),'excluded_count':len(excluded_rows),
  'passing_count':len(passing),
  'passing_candidates':passing,
  'top_failing_candidates':failing[:20],
  'exclusion_summary':{},
  'release_status':'NOT_FOR_GERBER'
 }
 for x in excluded_rows:
  r=x['exclusion_reason']; out['exclusion_summary'][r]=out['exclusion_summary'].get(r,0)+1
 Path(args.output).write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({
  'source_gate':out['source_gate'],'evaluated_count':out['evaluated_count'],'passing_count':out['passing_count'],
  'passing':[{'drc_index':x['drc_index'],'net':x['net'],'a':x['a']['description'],'b':x['b']['description'],'length_mm':x['length_mm'],'clearance_mm':x['minimum_conservative_clearance_mm']} for x in passing[:20]],
  'top_failing':[{'drc_index':x['drc_index'],'net':x['net'],'length_mm':x['length_mm'],'clearance_mm':x['minimum_conservative_clearance_mm']} for x in failing[:10]],
  'exclusions':out['exclusion_summary']
 },indent=2))
 if out['board_modified'] is not False or out['raw_pair_count']<100: raise SystemExit('broad screen state gate failed')

if __name__=='__main__': main()
