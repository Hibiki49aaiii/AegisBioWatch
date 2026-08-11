#!/usr/bin/env python3
"""r13 route-1x: connect the R103/R104 +1V8 pull-up branch to C113.1/+1V8.

Source: executed-KiCad-clean route-1w (0 violations / 152 unconnected /
268-node physical audit PASS). The path escapes left from R103.1, drops clear
of R103.2/SDA, then joins the accepted C113.1 +1V8 node. No I2C signal pad,
via, or placement is modified.
"""
from __future__ import annotations
import argparse,faulthandler,hashlib,json,os,shutil,sys
from pathlib import Path
import pcbnew  # type: ignore
faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1w'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1w-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1w-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1w.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1x'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1x-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1x-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1x-report.py'
TRACK_WIDTH=0.20
BEND1=(11.60,34.223282)
BEND2=(11.60,32.399818)

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
def refill(board):
    zs=pcbnew.ZONES()
    for z in board.Zones(): zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1x zone refill failed')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1w-drc-json',required=True); ap.add_argument('--route1w-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1w report/PCB SHA mismatch')
    d=loadj(args.route1w_drc_json); a=loadj(args.route1w_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=152: raise SystemExit('route1w DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1w pin/net gate failed')
    board=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in board.GetFootprints()}
    r103=fps.get('R103'); c113=fps.get('C113')
    if r103 is None or c113 is None: raise SystemExit('route1x missing R103/C113')
    gates={'R103.1':pads(r103,'1')[0].GetNetname(),'R103.2':pads(r103,'2')[0].GetNetname(),'C113.1':pads(c113,'1')[0].GetNetname(),'C113.2':pads(c113,'2')[0].GetNetname()}
    expected={'R103.1':'+1V8','R103.2':'SYS_I2C_SDA','C113.1':'+1V8','C113.2':'GND'}
    if gates!=expected: raise SystemExit(f'route1x net gate failed: {gates}')
    p103=point(r103,'1'); target=point(c113,'1')
    if abs(p103[0]-12.214871)>0.001 or abs(p103[1]-34.223282)>0.001: raise SystemExit(f'route1x R103.1 geometry gate failed: {p103}')
    if abs(target[0]-12.245188)>0.001 or abs(target[1]-32.399818)>0.001: raise SystemExit(f'route1x C113.1 geometry gate failed: {target}')
    net=board.FindNet('+1V8')
    if net is None: raise SystemExit('route1x +1V8 net reacquire failed')
    added=0
    added+=add_track(board,net,p103,BEND1)
    added+=add_track(board,net,BEND1,BEND2)
    added+=add_track(board,net,BEND2,target)
    if added!=3: raise SystemExit('route1x scope gate failed')
    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1x SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])
if __name__=='__main__': main()
