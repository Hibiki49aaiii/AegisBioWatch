#!/usr/bin/env python3
"""r13 route-1am: close C1.2/GND directly into continuous In1.Cu GND.

Source: executed-KiCad-clean route-1al (0 violations / 137 unconnected /
268-node physical audit PASS). C1 is a 10 uF +1V8 decoupler. This increment
adds one short rightward F.Cu segment and one standard through via while
leaving C1.1/+1V8 and all accepted route-1al geometry otherwise unchanged.
"""
from __future__ import annotations
import argparse,faulthandler,hashlib,json,os,shutil,sys
from pathlib import Path
import pcbnew  # type: ignore
faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1al'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1al-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1al-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1al.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1am'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1am-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1am-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1am-report.py'
TRACK_WIDTH=0.30
GND_VIA=(12.15,11.085)
VIA_SIZE=0.60
VIA_DRILL=0.30

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pads(fp,n): return [p for p in fp.Pads() if str(p.GetNumber())==str(n)]
def point(fp,n):
    ps=pads(fp,n)
    if not ps: raise SystemExit(f'{fp.GetReference()} missing pad {n}')
    return (sum(mm(p.GetPosition().x) for p in ps)/len(ps),sum(mm(p.GetPosition().y) for p in ps)/len(ps))
def add_track(board,net,a,b):
    t=pcbnew.PCB_TRACK(board); t.SetLayer(pcbnew.F_Cu); t.SetNet(net); t.SetWidth(iu(TRACK_WIDTH))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1]))); board.Add(t); return 1
def add_via(board,net,p):
    v=pcbnew.PCB_VIA(board); v.SetNet(net); v.SetPosition(pcbnew.VECTOR2I(iu(p[0]),iu(p[1])))
    v.SetWidth(iu(VIA_SIZE)); v.SetDrill(iu(VIA_DRILL)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); board.Add(v); return 1
def refill(board):
    zs=pcbnew.ZONES()
    for z in board.Zones(): zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1am zone refill failed')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1al-drc-json',required=True); ap.add_argument('--route1al-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1al report/PCB SHA mismatch')
    d=loadj(args.route1al_drc_json); a=loadj(args.route1al_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=137: raise SystemExit('route1al DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1al pin/net gate failed')
    board=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in board.GetFootprints()}
    c1=fps.get('C1')
    if c1 is None: raise SystemExit('route1am missing C1')
    p1=pads(c1,'1'); p2=pads(c1,'2')
    if len(p1)!=1 or len(p2)!=1: raise SystemExit('route1am C1 pad cardinality gate failed')
    gates={'C1.1':p1[0].GetNetname(),'C1.2':p2[0].GetNetname(),'C1.value':c1.GetValue()}
    expected={'C1.1':'+1V8','C1.2':'GND','C1.value':'10uF'}
    if gates!=expected: raise SystemExit(f'route1am C1 net/value gate failed: {gates}')
    gnd_pad=point(c1,'2')
    if abs(gnd_pad[0]-11.265)>0.001 or abs(gnd_pad[1]-11.085)>0.001: raise SystemExit(f'route1am C1.2 geometry gate failed: {gnd_pad}')
    net=board.FindNet('GND')
    if net is None: raise SystemExit('route1am GND net reacquire failed')
    added=add_track(board,net,gnd_pad,GND_VIA); vias=add_via(board,net,GND_VIA)
    if added!=1 or vias!=1: raise SystemExit(f'route1am routing scope gate failed: segments={added} vias={vias}')
    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1am SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])
if __name__=='__main__': main()
