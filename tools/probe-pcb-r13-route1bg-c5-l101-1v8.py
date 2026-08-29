#!/usr/bin/env python3
"""Read-only route-1bg probe for C5.1/+1V8 -> L101.2/+1V8."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pcbnew  # type: ignore

ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bf'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1bf-r13.kicad_pcb'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1bf.json'

START=(9.255,22.225)
END=(8.964712,24.126353)
TRACK_WIDTH=0.30
RULE_CLEARANCE=0.10
MARGIN=TRACK_WIDTH/2.0+RULE_CLEARANCE
ENVELOPE=(min(START[0],END[0])-MARGIN,min(START[1],END[1])-MARGIN,
          max(START[0],END[0])+MARGIN,max(START[1],END[1])+MARGIN)


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def pt(v): return [round(mm(v.x),6),round(mm(v.y),6)]
def rect(o):
    b=o.GetBoundingBox()
    return [round(mm(b.GetX()),6),round(mm(b.GetY()),6),round(mm(b.GetRight()),6),round(mm(b.GetBottom()),6)]
def intersects(a,b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])
def track_rect(t):
    a=pt(t.GetStart()); b=pt(t.GetEnd()); h=mm(t.GetWidth())/2
    return [min(a[0],b[0])-h,min(a[1],b[1])-h,max(a[0],b[0])+h,max(a[1],b[1])+h]
def one_pad(fp,n):
    ps=[p for p in fp.Pads() if str(p.GetNumber())==str(n)]
    if len(ps)!=1: raise SystemExit(f'{fp.GetReference()}.{n} cardinality gate failed: {len(ps)}')
    return ps[0]
def same(a,b,tol=0.001): return abs(a[0]-b[0])<=tol and abs(a[1]-b[1])<=tol

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--route1bf-drc-json',required=True)
    ap.add_argument('--route1bf-pin-net-audit',required=True)
    ap.add_argument('--output',required=True)
    args=ap.parse_args()

    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1bg probe route1bf report/PCB SHA mismatch')
    d=loadj(args.route1bf_drc_json); a=loadj(args.route1bf_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=117:
        raise SystemExit('route1bg probe route1bf DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268:
        raise SystemExit('route1bg probe route1bf pin/net gate failed')

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={f.GetReference():f for f in board.GetFootprints()}
    c5=fps.get('C5'); l101=fps.get('L101'); c107=fps.get('C107')
    if c5 is None or l101 is None or c107 is None: raise SystemExit('route1bg missing C5/L101/C107')
    if c5.GetValue()!='100nF' or l101.GetValue()!='2.2uH / DCR<400mR':
        raise SystemExit(f'route1bg value gate failed C5={c5.GetValue()!r} L101={l101.GetValue()!r}')

    c51=one_pad(c5,'1'); c52=one_pad(c5,'2'); l1=one_pad(l101,'1'); l2=one_pad(l101,'2'); c1071=one_pad(c107,'1')
    observed={
      'C5.1':{'net':c51.GetNetname(),'position_mm':pt(c51.GetPosition()),'bbox_mm':rect(c51)},
      'C5.2':{'net':c52.GetNetname(),'position_mm':pt(c52.GetPosition()),'bbox_mm':rect(c52)},
      'L101.1':{'net':l1.GetNetname(),'position_mm':pt(l1.GetPosition()),'bbox_mm':rect(l1)},
      'L101.2':{'net':l2.GetNetname(),'position_mm':pt(l2.GetPosition()),'bbox_mm':rect(l2)},
      'C107.1':{'net':c1071.GetNetname(),'position_mm':pt(c1071.GetPosition()),'bbox_mm':rect(c1071)}
    }
    expected={
      'C5.1':('+1V8',[9.255,22.225]),
      'C5.2':('GND',[9.895,22.225]),
      'L101.1':('PMIC_SW1',[7.514712,24.126353]),
      'L101.2':('+1V8',[8.964712,24.126353]),
      'C107.1':('+1V8',[10.407553,23.51711])
    }
    for key,(net,pos) in expected.items():
        if observed[key]['net']!=net or observed[key]['position_mm']!=pos:
            raise SystemExit(f'route1bg endpoint/net gate failed {key}: {observed[key]}')

    blockers=[]; same_net_context=[]
    target_pads={('C5','1'),('L101','2')}
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if not p.IsOnLayer(pcbnew.F_Cu): continue
            key=(fp.GetReference(),str(p.GetNumber()))
            if key in target_pads: continue
            pb=rect(p)
            if not intersects(pb,ENVELOPE): continue
            rec={'kind':'pad','reference':fp.GetReference(),'pad':str(p.GetNumber()),
                 'net':p.GetNetname(),'bbox_mm':pb}
            if p.GetNetname()=='+1V8': same_net_context.append(rec)
            else: blockers.append(rec)

    existing_rail_to_c107=False
    for item in board.GetTracks():
        net=item.GetNetname() if hasattr(item,'GetNetname') else ''
        if isinstance(item,pcbnew.PCB_VIA):
            rb=rect(item)
            if not intersects(rb,ENVELOPE): continue
            rec={'kind':'via','net':net,'position_mm':pt(item.GetPosition()),'bbox_mm':rb}
            if net=='+1V8': same_net_context.append(rec)
            else: blockers.append(rec)
        else:
            if item.GetLayer()!=pcbnew.F_Cu: continue
            tr=track_rect(item)
            a0=pt(item.GetStart()); b0=pt(item.GetEnd())
            if net=='+1V8' and ((same(a0,list(END)) and same(b0,[10.407553,23.51711])) or
                                (same(b0,list(END)) and same(a0,[10.407553,23.51711]))):
                existing_rail_to_c107=True
            if not intersects(tr,ENVELOPE): continue
            rec={'kind':'track','net':net,'start_mm':a0,'end_mm':b0,'width_mm':round(mm(item.GetWidth()),6),
                 'bbox_mm':[round(x,6) for x in tr]}
            if net=='+1V8': same_net_context.append(rec)
            else: blockers.append(rec)

    if not existing_rail_to_c107: raise SystemExit('route1bg accepted L101.2->C107.1 +1V8 rail gate failed')
    if blockers: raise SystemExit('route1bg direct corridor blocked: '+json.dumps(blockers,indent=2))

    out={
      'revision':'r13-route1bg-c5-l101-1v8-geometry-probe',
      'source_route1bf_sha256':srcsha,
      'source_gate':{'rule_violations':0,'unconnected_items':117,'pin_net_audit':'PASS','audited_nodes':268},
      'board_modified':False,
      'C5_value':c5.GetValue(),'L101_value':l101.GetValue(),
      'pads':observed,
      'candidate':{'start_mm':list(START),'end_mm':list(END),'track_width_mm':TRACK_WIDTH,
                   'length_mm':1.923385,'rule_clearance_mm':RULE_CLEARANCE,'envelope_mm':list(ENVELOPE)},
      'existing_l101_to_c107_rail_preserved':existing_rail_to_c107,
      'unrelated_blockers':blockers,'unrelated_blocker_count':len(blockers),
      'same_net_context':same_net_context,
      'release_status':'NOT_FOR_GERBER'
    }
    Path(args.output).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
