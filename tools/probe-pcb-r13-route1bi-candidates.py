#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import pcbnew  # type: ignore

ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bg'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1bg-r13.kicad_pcb'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1bg.json'
WIDTH=0.30
RULE=0.10
EPS=1e-9

CANDIDATES=[
 {'id':'c1-j8-1v8','net':'+1V8','start':[10.305,11.085],'end':[12.105,15.26],'semantics':'C1.1 to J8.1 SWD power'},
 {'id':'r302-r404-1v8','net':'+1V8','start':[20.255,25.975],'end':[15.755,26.725],'semantics':'R302.1 to R404.1 pull-up rail'},
 {'id':'pmic-1v8-track-bridge','net':'+1V8','start':[11.1875,30.95],'end':[8.9875,26.75],'semantics':'upper PMIC +1V8 track to lower rail'},
 {'id':'pullup-island-to-1v8-rail','net':'+1V8','start':[3.005,25.975],'end':[8.9875,26.75],'semantics':'route1bf pull-up island to lower +1V8 rail'},
 {'id':'j101-ship-hold-duplicate','net':'SHIP_HOLD','start':[34.775,10.625],'end':[34.775,15.025],'semantics':'J101 duplicate SHIP_HOLD terminals'},
 {'id':'j9-side-button-duplicate','net':'SIDE_BUTTON','start':[20.85,7.475],'end':[26.0,7.475],'semantics':'J9 duplicate SIDE_BUTTON terminals'},
 {'id':'vsys-track-bridge','net':'VSYS','start':[5.270826,25.865834],'end':[8.9875,28.25],'semantics':'VSYS track island bridge'},
]

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
 es=list(zip(cs,cs[1:]+cs[:1]))
 if any(intersect(a,b,c,d) for c,d in es): return 0.0
 return min(prect(a,r),prect(b,r),*(pseg(c,a,b) for c in cs))

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--route1bg-drc-json',required=True)
 ap.add_argument('--route1bg-pin-net-audit',required=True)
 ap.add_argument('--output',required=True)
 args=ap.parse_args()
 rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
 if rep.get('output_sha256')!=srcsha: raise SystemExit('route1bi screen source SHA gate failed')
 d=loadj(args.route1bg_drc_json); a=loadj(args.route1bg_pin_net_audit)
 if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=116: raise SystemExit('route1bi screen DRC source gate failed')
 if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1bi screen audit source gate failed')
 board=pcbnew.LoadBoard(str(SRC_PCB))
 results=[]
 for cand in CANDIDATES:
  A=tuple(cand['start']); B=tuple(cand['end']); net=cand['net']; half=WIDTH/2
  hits=[]
  for fp in board.GetFootprints():
   for p in fp.Pads():
    if not p.IsOnLayer(pcbnew.F_Cu): continue
    if p.GetNetname()==net: continue
    r=bbox(p); clr=srect(A,B,r)-half
    hits.append({'kind':'pad','reference':fp.GetReference(),'pad':str(p.GetNumber()),'net':p.GetNetname(),'clearance_mm':round(clr,6),'bbox_mm':[round(x,6) for x in r]})
  for item in board.GetTracks():
   n=item.GetNetname() if hasattr(item,'GetNetname') else ''
   if n==net: continue
   if isinstance(item,pcbnew.PCB_VIA):
    pos=xy(item.GetPosition()); r=bbox(item); radius=max(r[2]-r[0],r[3]-r[1])/2
    clr=pseg(pos,A,B)-radius-half
    hits.append({'kind':'via','net':n,'position_mm':list(pos),'clearance_mm':round(clr,6)})
   else:
    if item.GetLayer()!=pcbnew.F_Cu: continue
    x=xy(item.GetStart()); y=xy(item.GetEnd()); w=mm(item.GetWidth())
    clr=sseg(A,B,x,y)-w/2-half
    hits.append({'kind':'track','net':n,'start_mm':list(x),'end_mm':list(y),'width_mm':round(w,6),'clearance_mm':round(clr,6)})
  hits.sort(key=lambda x:x['clearance_mm'])
  minc=hits[0]['clearance_mm'] if hits else 999.0
  results.append({
   **cand,
   'width_mm':WIDTH,
   'length_mm':round(math.dist(A,B),6),
   'minimum_conservative_clearance_mm':minc,
   'rule_pass':minc+1e-6>=RULE,
   'nearest_unrelated_copper':hits[:8],
  })
 results.sort(key=lambda x:(not x['rule_pass'],-x['minimum_conservative_clearance_mm'],x['length_mm']))
 out={
  'revision':'r13-route1bi-multi-candidate-screen',
  'source_route1bg_sha256':srcsha,
  'source_gate':{'rule_violations':0,'unconnected_items':116,'pin_net_audit':'PASS','audited_nodes':268},
  'board_modified':False,
  'rule_clearance_mm':RULE,
  'candidate_count':len(results),
  'ranked_candidates':results,
  'passing_candidate_ids':[x['id'] for x in results if x['rule_pass']],
  'release_status':'NOT_FOR_GERBER'
 }
 Path(args.output).write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
 if len(results)!=7: raise SystemExit('route1bi screen candidate count gate failed')

if __name__=='__main__': main()
