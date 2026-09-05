#!/usr/bin/env python3
"""r13 route-1ax: close the upper J101.2/GND pad into continuous In1.Cu GND.

Source: executed-KiCad-clean route-1aw (0 violations / 126 unconnected /
268-node physical audit PASS). This increment routes only the upper GND terminal
of the J101 ship/wake switch with one short F.Cu segment and one standard
through-via. J101.1/SHIP_HOLD, the accepted lower J101.2/GND closure, all other
accepted route-1aw geometry, RF routing, and supplier-gated interfaces remain
unchanged.
"""
from __future__ import annotations
import argparse,faulthandler,hashlib,json,os,shutil,sys
from pathlib import Path
import pcbnew  # type: ignore

faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1aw'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1aw-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1aw-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1aw.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ax'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1ax-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1ax-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1ax-report.py'
TRACK_WIDTH=0.30
GND_VIA=(39.20,10.625)
VIA_SIZE=0.60
VIA_DRILL=0.30
TARGET_PAD=(38.475,10.625)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pads(fp,n): return [p for p in fp.Pads() if str(p.GetNumber())==str(n)]
def positions(fp,n):
    return sorted((round(mm(p.GetPosition().x),6),round(mm(p.GetPosition().y),6)) for p in pads(fp,n))
def add_track(board,net,a,b):
    t=pcbnew.PCB_TRACK(board); t.SetLayer(pcbnew.F_Cu); t.SetNet(net); t.SetWidth(iu(TRACK_WIDTH))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1]))); board.Add(t); return 1
def add_via(board,net,p):
    v=pcbnew.PCB_VIA(board); v.SetNet(net); v.SetPosition(pcbnew.VECTOR2I(iu(p[0]),iu(p[1])))
    v.SetWidth(iu(VIA_SIZE)); v.SetDrill(iu(VIA_DRILL)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); board.Add(v); return 1
def refill(board):
    zs=pcbnew.ZONES()
    for z in board.Zones(): zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1ax zone refill failed')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--route1aw-drc-json',required=True)
    ap.add_argument('--route1aw-pin-net-audit',required=True)
    args=ap.parse_args()

    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1aw report/PCB SHA mismatch')
    lower=rep.get('connections',{}).get('J101.2/GND lower',{})
    if lower.get('pad_mm')!=[38.475,15.025] or lower.get('gnd_via_mm')!=[39.2,15.025]:
        raise SystemExit('route1aw accepted lower J101.2 closure provenance gate failed')
    d=loadj(args.route1aw_drc_json); a=loadj(args.route1aw_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=126: raise SystemExit('route1aw DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1aw pin/net gate failed')

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={f.GetReference():f for f in board.GetFootprints()}
    j101=fps.get('J101')
    if j101 is None: raise SystemExit('route1ax missing J101')
    if j101.GetValue()!='EVQPLDA15_SHIP_WAKE': raise SystemExit(f'route1ax J101 value gate failed: {j101.GetValue()!r}')
    p1=pads(j101,'1'); p2=pads(j101,'2')
    if len(p1)!=2 or len(p2)!=2: raise SystemExit(f'route1ax J101 pad cardinality gate failed: pad1={len(p1)} pad2={len(p2)}')
    if any(p.GetNetname()!='SHIP_HOLD' for p in p1): raise SystemExit('route1ax J101.1 net gate failed')
    if any(p.GetNetname()!='GND' for p in p2): raise SystemExit('route1ax J101.2 net gate failed')
    p1pos=positions(j101,'1'); p2pos=positions(j101,'2')
    if p1pos!=[(34.775,10.625),(34.775,15.025)]: raise SystemExit(f'route1ax J101.1 geometry gate failed: {p1pos}')
    if p2pos!=[(38.475,10.625),(38.475,15.025)]: raise SystemExit(f'route1ax J101.2 geometry gate failed: {p2pos}')

    net=board.FindNet('GND')
    if net is None: raise SystemExit('route1ax GND net reacquire failed')
    added=add_track(board,net,TARGET_PAD,GND_VIA)
    vias=add_via(board,net,GND_VIA)
    if added!=1 or vias!=1: raise SystemExit(f'route1ax routing scope gate failed: segments={added} vias={vias}')

    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1ax SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])

if __name__=='__main__':
    main()
