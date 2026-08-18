#!/usr/bin/env python3
"""r13 route-1ac: close C110.2/GND directly into continuous In1.Cu GND.

Source: executed-KiCad-clean route-1ab (0 violations / 147 unconnected /
268-node physical audit PASS). This keeps the second DISP_SW local capacitor
return independent from neighboring nRF/display copper. One short F.Cu segment
and one standard through via are added; DISP_SW is untouched.
"""
from __future__ import annotations
import argparse,faulthandler,hashlib,json,os,shutil,sys
from pathlib import Path
import pcbnew  # type: ignore
faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ab'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1ab-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1ab-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1ab.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ac'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ac-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1ac-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1ac-report.py'
TRACK_WIDTH=0.30
GND_VIA=(15.75,20.43)
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
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1ac zone refill failed')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1ab-drc-json',required=True); ap.add_argument('--route1ab-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1ab report/PCB SHA mismatch')
    d=loadj(args.route1ab_drc_json); a=loadj(args.route1ab_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=147: raise SystemExit('route1ab DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1ab pin/net gate failed')
    board=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in board.GetFootprints()}
    c110=fps.get('C110')
    if c110 is None: raise SystemExit('route1ac missing C110')
    gates={'C110.1':pads(c110,'1')[0].GetNetname(),'C110.2':pads(c110,'2')[0].GetNetname(),'C110.value':c110.GetValue()}
    expected={'C110.1':'DISP_SW','C110.2':'GND','C110.value':'10uF X5R 25V'}
    if gates!=expected: raise SystemExit(f'route1ac C110 net/value gate failed: {gates}')
    gnd_pad=point(c110,'2')
    if abs(gnd_pad[0]-15.020113)>0.001 or abs(gnd_pad[1]-20.427633)>0.001: raise SystemExit(f'route1ac C110.2 geometry gate failed: {gnd_pad}')
    net=board.FindNet('GND')
    if net is None: raise SystemExit('route1ac GND net reacquire failed')
    added=add_track(board,net,gnd_pad,GND_VIA); vias=add_via(board,net,GND_VIA)
    if added!=1 or vias!=1: raise SystemExit(f'route1ac routing scope gate failed: segments={added} vias={vias}')
    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1ac SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])
if __name__=='__main__': main()
