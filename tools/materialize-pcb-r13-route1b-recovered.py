#!/usr/bin/env python3
"""r13 route-1b: legal nPM1300 SW1/SW2 breakout only.

This intentionally replaces the over-broad first route attempt.  It adds only
SW1 and SW2 copper, using 0.20 mm QFN neck-down traces and doglegs outside the
0.5 mm-pitch U2 pad row.  VOUT, VSYS, PVSS trees and GND stitching remain for
later routing stages so each stage can be proven by KiCad DRC independently.

No RF or supplier-gated interface is touched. Geometry is a planning seed, not
fabrication authority.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path
import pcbnew  # type: ignore

ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/placement-r13'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Placement-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Placement-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'placement-implementation-r13.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1b'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1b-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1b-r13.kicad_pro'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1b.json'
WIDTH=0.20


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))

def pads(fp,num): return [p for p in fp.Pads() if str(p.GetNumber())==str(num)]
def point(fp,num):
    ps=pads(fp,num)
    if not ps: raise SystemExit(f'{fp.GetReference()} missing pad {num}')
    x=sum(mm(p.GetPosition().x) for p in ps)/len(ps); y=sum(mm(p.GetPosition().y) for p in ps)/len(ps)
    return (x,y)

def add_track(board,net,a,b,width=WIDTH):
    if abs(a[0]-b[0])<1e-9 and abs(a[1]-b[1])<1e-9: return 0
    t=pcbnew.PCB_TRACK(board); t.SetLayer(pcbnew.F_Cu); t.SetNet(net); t.SetWidth(iu(width))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1]))); board.Add(t); return 1

def route_poly(board, net, pts):
    return sum(add_track(board,net,a,b) for a,b in zip(pts,pts[1:]))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--placement-drc-json',required=True); ap.add_argument('--placement-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); pcbsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=pcbsha: raise SystemExit('placement report/PCB SHA mismatch')
    d=loadj(args.placement_drc_json); a=loadj(args.placement_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=186: raise SystemExit('placement DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('placement pin/net gate failed')

    b=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in b.GetFootprints()}
    u2,l101,l102=fps['U2'],fps['L101'],fps['L102']
    p3,p5=point(u2,'3'),point(u2,'5'); l1=point(l101,'1'); l2=point(l102,'1')
    n1=pads(u2,'3')[0].GetNet(); n2=pads(u2,'5')[0].GetNet()
    if n1.GetNetname()!='PMIC_SW1' or n2.GetNetname()!='PMIC_SW2': raise SystemExit('SW net gate failed')

    # U2 left-edge pads are 0.5 mm pitch and 0.8 x 0.25 mm. Escape 0.80 mm
    # directly outward before changing Y, keeping the 0.20 mm trace away from
    # adjacent QFN pads. SW1 then runs vertically in the clear channel toward L101.
    xesc=p3[0]-0.80
    sw1=[p3,(xesc,p3[1]),(xesc,l1[1]),l1]

    # SW2 uses the same outward escape but crosses below the C103/C104 row before
    # approaching L102, avoiding NT102 near y=32.045 mm.
    xesc2=p5[0]-0.80; ydog=30.65
    sw2=[p5,(xesc2,p5[1]),(xesc2,ydog),(l2[0],ydog),l2]
    segs=route_poly(b,n1,sw1)+route_poly(b,n2,sw2)
    b.SynchronizeNetsAndNetClasses(True); b.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),b): raise SystemExit('SaveBoard failed')
    shutil.copy2(SRC_PRO,OUT_PRO)
    out={'revision':'r13-route1b-sw-only','source_placement_sha256':pcbsha,'output_sha256':sha(OUT_PCB),'track_width_mm':WIDTH,'track_segments_added':segs,'vias_added':0,'routed_nets':['PMIC_SW1','PMIC_SW2'],'sw1_points_mm':sw1,'sw2_points_mm':sw2,'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,'routing_status':'STARTED_SW_ONLY','validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
