#!/usr/bin/env python3
"""r13 route-1y: connect U2.13/SYS_I2C_SDA to R103.2/SYS_I2C_SDA.

Source: executed-KiCad-clean route-1x (0 violations / 151 unconnected /
268-node physical audit PASS).

The F.Cu escape stays to the right of the accepted route-1v +1V8 trace while
remaining left/below the adjacent U2.14/SCL pad, then changes to B.Cu at a
standard 0.45/0.20 mm signal via. The B.Cu segment avoids the accepted C102/
route-1j GND vias and route-1l VSYS trunk, then returns to F.Cu beside R103.2.
No component or accepted copper is moved.
"""
from __future__ import annotations
import argparse, faulthandler, hashlib, json, os, shutil, sys
from pathlib import Path
import pcbnew  # type: ignore
faulthandler.enable()

ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1x'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1x-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1x-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1x.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1y'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1y-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1y-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1y-report.py'
TRACK_WIDTH=0.20
VIA_SIZE=0.45
VIA_DRILL=0.20
P1=(11.6875,31.48)
P2=(11.80,31.56)
START_VIA=(12.50,31.80)
END_VIA=(12.05,33.45)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pads(fp,n): return [p for p in fp.Pads() if str(p.GetNumber())==str(n)]
def point(fp,n):
    ps=pads(fp,n)
    if not ps: raise SystemExit(f'{fp.GetReference()} missing pad {n}')
    return (sum(mm(p.GetPosition().x) for p in ps)/len(ps),sum(mm(p.GetPosition().y) for p in ps)/len(ps))
def add_track(board,net,a,b,layer):
    t=pcbnew.PCB_TRACK(board); t.SetLayer(layer); t.SetNet(net); t.SetWidth(iu(TRACK_WIDTH))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1]))); board.Add(t); return 1
def add_via(board,net,p):
    v=pcbnew.PCB_VIA(board); v.SetNet(net); v.SetPosition(pcbnew.VECTOR2I(iu(p[0]),iu(p[1])))
    v.SetWidth(iu(VIA_SIZE)); v.SetDrill(iu(VIA_DRILL)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); board.Add(v); return 1
def refill(board):
    zs=pcbnew.ZONES()
    for z in board.Zones(): zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1y zone refill failed')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1x-drc-json',required=True); ap.add_argument('--route1x-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1x report/PCB SHA mismatch')
    d=loadj(args.route1x_drc_json); a=loadj(args.route1x_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=151: raise SystemExit('route1x DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1x pin/net gate failed')
    board=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in board.GetFootprints()}
    u2=fps.get('U2'); r103=fps.get('R103')
    if u2 is None or r103 is None: raise SystemExit('route1y missing U2/R103')
    gates={'U2.13':pads(u2,'13')[0].GetNetname(),'U2.14':pads(u2,'14')[0].GetNetname(),'R103.1':pads(r103,'1')[0].GetNetname(),'R103.2':pads(r103,'2')[0].GetNetname()}
    expected={'U2.13':'SYS_I2C_SDA','U2.14':'SYS_I2C_SCL','R103.1':'+1V8','R103.2':'SYS_I2C_SDA'}
    if gates!=expected: raise SystemExit(f'route1y net gate failed: {gates}')
    start=point(u2,'13'); target=point(r103,'2')
    if abs(start[0]-11.6875)>0.001 or abs(start[1]-30.95)>0.001: raise SystemExit(f'route1y U2.13 geometry gate failed: {start}')
    if abs(target[0]-12.214871)>0.001 or abs(target[1]-33.583282)>0.001: raise SystemExit(f'route1y R103.2 geometry gate failed: {target}')
    net=board.FindNet('SYS_I2C_SDA')
    if net is None: raise SystemExit('route1y SDA net reacquire failed')
    added=0; vias=0
    added+=add_track(board,net,start,P1,pcbnew.F_Cu)
    added+=add_track(board,net,P1,P2,pcbnew.F_Cu)
    added+=add_track(board,net,P2,START_VIA,pcbnew.F_Cu)
    vias+=add_via(board,net,START_VIA)
    added+=add_track(board,net,START_VIA,END_VIA,pcbnew.B_Cu)
    vias+=add_via(board,net,END_VIA)
    added+=add_track(board,net,END_VIA,target,pcbnew.F_Cu)
    if added!=5 or vias!=2: raise SystemExit(f'route1y scope gate failed: segments={added} vias={vias}')
    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1y SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])
if __name__=='__main__': main()
