#!/usr/bin/env python3
"""r13 route-1at: close J8.5/GND directly into continuous In1.Cu GND.

Source: executed-KiCad-clean route-1as (0 violations / 130 unconnected /
268-node physical audit PASS). This increment routes only J8.5/GND with one
short rightward F.Cu segment and one standard through via. All J8 signal pads
and accepted route-1as geometry remain unchanged.
"""
from __future__ import annotations
import argparse,faulthandler,hashlib,json,os,shutil,sys
from pathlib import Path
import pcbnew  # type: ignore

faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1as'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1as-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1as-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1as.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1at'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1at-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1at-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1at-report.py'
TRACK_WIDTH=0.30
GND_VIA=(15.25,15.26)
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
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1at zone refill failed')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--route1as-drc-json',required=True)
    ap.add_argument('--route1as-pin-net-audit',required=True)
    args=ap.parse_args()

    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1as report/PCB SHA mismatch')
    d=loadj(args.route1as_drc_json); a=loadj(args.route1as_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=130: raise SystemExit('route1as DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1as pin/net gate failed')

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={f.GetReference():f for f in board.GetFootprints()}
    j8=fps.get('J8')
    if j8 is None: raise SystemExit('route1at missing J8')
    expected={'J8.value':'TC2030_SWD_6','J8.1':'+1V8','J8.2':'SWDIO','J8.3':'NRF_RESET_N','J8.4':'SWDCLK','J8.5':'GND','J8.6':'SWO'}
    gates={'J8.value':j8.GetValue()}
    for n in ('1','2','3','4','5','6'):
        ps=pads(j8,n)
        if len(ps)!=1: raise SystemExit(f'route1at J8 pad {n} cardinality gate failed')
        gates[f'J8.{n}']=ps[0].GetNetname()
    if gates!=expected: raise SystemExit(f'route1at J8 net/value gate failed: {gates}')

    gnd_pad=point(j8,'5')
    if abs(gnd_pad[0]-14.645)>0.001 or abs(gnd_pad[1]-15.26)>0.001:
        raise SystemExit(f'route1at J8.5 geometry gate failed: {gnd_pad}')
    net=board.FindNet('GND')
    if net is None: raise SystemExit('route1at GND net reacquire failed')
    added=add_track(board,net,gnd_pad,GND_VIA)
    vias=add_via(board,net,GND_VIA)
    if added!=1 or vias!=1: raise SystemExit(f'route1at routing scope gate failed: segments={added} vias={vias}')

    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1at SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])

if __name__=='__main__':
    main()
