#!/usr/bin/env python3
"""r13 route-1ak: close Q501.2/GND directly into continuous In1.Cu GND.

Source: executed-KiCad-clean route-1aj (0 violations / 139 unconnected /
268-node physical audit PASS). Q501 is the CHG_PRESENT_N / CHG_SENSE_GATE
2N7002-class sense transistor. This increment adds one short leftward F.Cu
segment and one standard through via while leaving both signal pins and all
accepted route-1aj geometry otherwise unchanged.
"""
from __future__ import annotations
import argparse,faulthandler,hashlib,json,os,shutil,sys
from pathlib import Path
import pcbnew  # type: ignore
faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1aj'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1aj-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1aj-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1aj.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ak'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ak-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1ak-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1ak-report.py'
TRACK_WIDTH=0.30
GND_VIA=(17.65,19.525)
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
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1ak zone refill failed')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1aj-drc-json',required=True); ap.add_argument('--route1aj-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1aj report/PCB SHA mismatch')
    d=loadj(args.route1aj_drc_json); a=loadj(args.route1aj_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=139: raise SystemExit('route1aj DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1aj pin/net gate failed')
    board=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in board.GetFootprints()}
    q501=fps.get('Q501')
    if q501 is None: raise SystemExit('route1ak missing Q501')
    gates={'Q501.1':pads(q501,'1')[0].GetNetname(),'Q501.2':pads(q501,'2')[0].GetNetname(),'Q501.3':pads(q501,'3')[0].GetNetname(),'Q501.value':q501.GetValue()}
    expected={'Q501.1':'CHG_SENSE_GATE','Q501.2':'GND','Q501.3':'CHG_PRESENT_N','Q501.value':'2N7002-CLASS'}
    if gates!=expected: raise SystemExit(f'route1ak Q501 net/value gate failed: {gates}')
    gnd_pad=point(q501,'2')
    if abs(gnd_pad[0]-18.6175)>0.001 or abs(gnd_pad[1]-19.525)>0.001: raise SystemExit(f'route1ak Q501.2 geometry gate failed: {gnd_pad}')
    net=board.FindNet('GND')
    if net is None: raise SystemExit('route1ak GND net reacquire failed')
    added=add_track(board,net,gnd_pad,GND_VIA); vias=add_via(board,net,GND_VIA)
    if added!=1 or vias!=1: raise SystemExit(f'route1ak routing scope gate failed: segments={added} vias={vias}')
    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1ak SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])
if __name__=='__main__': main()
