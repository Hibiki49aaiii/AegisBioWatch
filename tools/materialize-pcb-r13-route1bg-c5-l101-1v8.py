#!/usr/bin/env python3
"""r13 route-1bg: connect C5.1/+1V8 to L101.2/+1V8 with one F.Cu segment."""
from __future__ import annotations
import argparse,faulthandler,hashlib,json,os,shutil,sys
from pathlib import Path
import pcbnew  # type: ignore

faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bf'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1bf-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1bf-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1bf.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bg'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1bg-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1bg-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1bg-report.py'
START=(9.255,22.225); END=(8.964712,24.126353); TRACK_WIDTH=0.30

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pt(p): return (round(mm(p.GetPosition().x),6),round(mm(p.GetPosition().y),6))
def one(fp,n):
    ps=[p for p in fp.Pads() if str(p.GetNumber())==str(n)]
    if len(ps)!=1: raise SystemExit(f'{fp.GetReference()}.{n} cardinality gate failed: {len(ps)}')
    return ps[0]
def itempt(v): return (round(mm(v.x),6),round(mm(v.y),6))
def same(a,b,tol=0.001): return abs(a[0]-b[0])<=tol and abs(a[1]-b[1])<=tol

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--route1bf-drc-json',required=True)
    ap.add_argument('--route1bf-pin-net-audit',required=True)
    args=ap.parse_args()

    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1bf report/PCB SHA mismatch')
    d=loadj(args.route1bf_drc_json); a=loadj(args.route1bf_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=117: raise SystemExit('route1bf DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1bf pin/net gate failed')

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={f.GetReference():f for f in board.GetFootprints()}
    c5=fps.get('C5'); l101=fps.get('L101'); c107=fps.get('C107')
    if c5 is None or l101 is None or c107 is None: raise SystemExit('route1bg missing C5/L101/C107')
    if c5.GetValue()!='100nF' or l101.GetValue()!='2.2uH / DCR<400mR': raise SystemExit('route1bg value gate failed')
    c51,c52,l1,l2,c1071=one(c5,'1'),one(c5,'2'),one(l101,'1'),one(l101,'2'),one(c107,'1')
    if (c51.GetNetname(),c52.GetNetname(),l1.GetNetname(),l2.GetNetname(),c1071.GetNetname())!=('+1V8','GND','PMIC_SW1','+1V8','+1V8'):
        raise SystemExit('route1bg net gate failed')
    if pt(c51)!=START or pt(c52)!=(9.895,22.225) or pt(l1)!=(7.514712,24.126353) or pt(l2)!=END or pt(c1071)!=(10.407553,23.51711):
        raise SystemExit(f'route1bg coordinate gate failed C5.1={pt(c51)} C5.2={pt(c52)} L101.1={pt(l1)} L101.2={pt(l2)} C107.1={pt(c1071)}')

    rail=False
    for item in board.GetTracks():
        if isinstance(item,pcbnew.PCB_VIA) or item.GetLayer()!=pcbnew.F_Cu or item.GetNetname()!='+1V8': continue
        x=itempt(item.GetStart()); y=itempt(item.GetEnd())
        if (same(x,END) and same(y,(10.407553,23.51711))) or (same(y,END) and same(x,(10.407553,23.51711))):
            rail=True
            break
    if not rail: raise SystemExit('route1bg existing L101.2->C107.1 +1V8 rail gate failed')

    net=board.FindNet('+1V8')
    if net is None: raise SystemExit('route1bg +1V8 net reacquire failed')
    t=pcbnew.PCB_TRACK(board); t.SetLayer(pcbnew.F_Cu); t.SetNet(net); t.SetWidth(iu(TRACK_WIDTH))
    t.SetStart(pcbnew.VECTOR2I(iu(START[0]),iu(START[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(END[0]),iu(END[1])))
    board.Add(t)

    zs=pcbnew.ZONES()
    for z in board.Zones(): zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1bg zone refill failed')
    board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()

    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1bg SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])

if __name__=='__main__': main()
