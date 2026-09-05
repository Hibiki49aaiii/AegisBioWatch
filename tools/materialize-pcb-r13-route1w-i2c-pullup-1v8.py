#!/usr/bin/env python3
"""r13 route-1w: connect the local +1V8 sides of R103 and R104.

Source: executed-KiCad-clean route-1v (0 violations / 153 unconnected /
268-node physical audit PASS). This increment touches only R103.1 and R104.1;
I2C pads R103.2/SDA and R104.2/SCL remain unchanged.
"""
from __future__ import annotations
import argparse, faulthandler, hashlib, json, os, shutil, sys
from pathlib import Path
import pcbnew  # type: ignore
faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1v'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1v-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1v-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1v.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1w'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1w-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1w-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1w-report.py'
TRACK_WIDTH=0.20

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
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1w zone refill failed')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1v-drc-json',required=True); ap.add_argument('--route1v-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1v report/PCB SHA mismatch')
    d=loadj(args.route1v_drc_json); a=loadj(args.route1v_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=153: raise SystemExit('route1v DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1v pin/net gate failed')
    board=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in board.GetFootprints()}
    r103=fps.get('R103'); r104=fps.get('R104')
    if r103 is None or r104 is None: raise SystemExit('route1w missing R103/R104')
    gates={'R103.1':pads(r103,'1')[0].GetNetname(),'R103.2':pads(r103,'2')[0].GetNetname(),'R104.1':pads(r104,'1')[0].GetNetname(),'R104.2':pads(r104,'2')[0].GetNetname()}
    expected={'R103.1':'+1V8','R103.2':'SYS_I2C_SDA','R104.1':'+1V8','R104.2':'SYS_I2C_SCL'}
    if gates!=expected: raise SystemExit(f'route1w net gate failed: {gates}')
    p103=point(r103,'1'); p104=point(r104,'1')
    if abs(p103[0]-12.214871)>0.001 or abs(p103[1]-34.223282)>0.001: raise SystemExit(f'route1w R103.1 geometry gate failed: {p103}')
    if abs(p104[0]-13.154075)>0.001 or abs(p104[1]-34.312249)>0.001: raise SystemExit(f'route1w R104.1 geometry gate failed: {p104}')
    net=board.FindNet('+1V8')
    if net is None: raise SystemExit('route1w +1V8 net reacquire failed')
    if add_track(board,net,p103,p104)!=1: raise SystemExit('route1w scope gate failed')
    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1w SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])
if __name__=='__main__': main()
