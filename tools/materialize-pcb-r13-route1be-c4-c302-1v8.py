#!/usr/bin/env python3
"""r13 route-1be: connect C4.1/+1V8 to C302.1/+1V8 with one diagonal F.Cu segment.

Source: accepted route-1bd (0 violations / 119 unconnected / 268-node
physical audit PASS). Phase-A geometry probe established exact endpoint and
corridor occupancy. This increment adds exactly one 0.30 mm F.Cu segment and
zero vias. Existing C4/C302 GND escapes and all other accepted geometry remain.
"""
from __future__ import annotations
import argparse,faulthandler,hashlib,json,os,shutil,sys
from pathlib import Path
import pcbnew  # type: ignore

faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bd'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1bd-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1bd-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1bd.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1be'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1be-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1be-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1be-report.py'

TRACK_WIDTH=0.30
START=(41.005,14.975)
END=(40.305,19.585)
C4_GND_PAD=(41.645,14.975)
C4_GND_VIA=(42.25,14.975)
C302_GND_PAD=(41.265,19.585)
C302_GND_VIA=(41.90,19.585)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pads(fp,n): return [p for p in fp.Pads() if str(p.GetNumber())==str(n)]
def pos(p): return (round(mm(p.GetPosition().x),6),round(mm(p.GetPosition().y),6))
def one_pad(fp,n):
    ps=pads(fp,n)
    if len(ps)!=1: raise SystemExit(f'route1be {fp.GetReference()}.{n} cardinality gate failed: {len(ps)}')
    return ps[0]
def same_pt(a,b,tol=0.001): return abs(a[0]-b[0])<=tol and abs(a[1]-b[1])<=tol
def item_pt(v): return (round(mm(v.x),6),round(mm(v.y),6))

def source_copper_gate(board):
    c4_track=False; c302_track=False; c4_via=False; c302_via=False
    for item in board.GetTracks():
        net=item.GetNetname() if hasattr(item,'GetNetname') else ''
        if isinstance(item,pcbnew.PCB_VIA):
            p=item_pt(item.GetPosition())
            if net=='GND' and same_pt(p,C4_GND_VIA): c4_via=True
            if net=='GND' and same_pt(p,C302_GND_VIA): c302_via=True
        else:
            if net!='GND': continue
            a=item_pt(item.GetStart()); b=item_pt(item.GetEnd())
            ends={a,b}
            if C4_GND_PAD in ends and C4_GND_VIA in ends: c4_track=True
            if C302_GND_PAD in ends and C302_GND_VIA in ends: c302_track=True
    if not all((c4_track,c302_track,c4_via,c302_via)):
        raise SystemExit(f'route1be source GND escape gate failed: c4_track={c4_track} c302_track={c302_track} c4_via={c4_via} c302_via={c302_via}')

def add_track(board,net,a,b):
    t=pcbnew.PCB_TRACK(board)
    t.SetLayer(pcbnew.F_Cu); t.SetNet(net); t.SetWidth(iu(TRACK_WIDTH))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1])))
    t.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1])))
    board.Add(t)
    return 1

def refill(board):
    zs=pcbnew.ZONES()
    for z in board.Zones(): zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs):
        raise SystemExit('route1be zone refill failed')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--route1bd-drc-json',required=True)
    ap.add_argument('--route1bd-pin-net-audit',required=True)
    args=ap.parse_args()

    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1bd report/PCB SHA mismatch')
    d=loadj(args.route1bd_drc_json); a=loadj(args.route1bd_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=119:
        raise SystemExit('route1bd DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268:
        raise SystemExit('route1bd pin/net gate failed')

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={f.GetReference():f for f in board.GetFootprints()}
    c4=fps.get('C4'); c302=fps.get('C302')
    if c4 is None or c302 is None: raise SystemExit('route1be missing C4/C302')
    if c4.GetValue()!='100nF' or c302.GetValue()!='1uF':
        raise SystemExit(f'route1be value gate failed: C4={c4.GetValue()!r} C302={c302.GetValue()!r}')

    c4p1=one_pad(c4,'1'); c4p2=one_pad(c4,'2')
    c302p1=one_pad(c302,'1'); c302p2=one_pad(c302,'2')
    if (c4p1.GetNetname(),c4p2.GetNetname(),c302p1.GetNetname(),c302p2.GetNetname())!=('+1V8','GND','+1V8','GND'):
        raise SystemExit('route1be pad net gate failed')
    if pos(c4p1)!=START or pos(c302p1)!=END:
        raise SystemExit(f'route1be +1V8 endpoint gate failed: C4.1={pos(c4p1)} C302.1={pos(c302p1)}')
    if pos(c4p2)!=C4_GND_PAD or pos(c302p2)!=C302_GND_PAD:
        raise SystemExit(f'route1be GND pad gate failed: C4.2={pos(c4p2)} C302.2={pos(c302p2)}')

    source_copper_gate(board)

    net=board.FindNet('+1V8')
    if net is None: raise SystemExit('route1be +1V8 net reacquire failed')
    added=add_track(board,net,START,END)
    if added!=1: raise SystemExit(f'route1be routing scope gate failed: segments={added}')

    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1be SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])

if __name__=='__main__':
    main()
