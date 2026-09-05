#!/usr/bin/env python3
"""r13 route-1bb: close the left J9.1/GND pad into continuous In1.Cu GND.

Source: accepted route-1ba (0 violations / 122 unconnected / 268-node
physical audit PASS). This increment routes only the left physical J9.1/GND
pad at (20.850,5.775) with one short horizontal F.Cu segment and one standard
through-via at (19.850,5.775). The accepted right J9.1/GND route, both
J9.2/SIDE_BUTTON pads, all accepted route-1ba geometry, RF routing, and
supplier-gated interfaces remain unchanged.
"""
from __future__ import annotations
import argparse,faulthandler,hashlib,json,os,shutil,sys
from pathlib import Path
import pcbnew  # type: ignore

faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1ba'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1ba-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1ba-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1ba.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bb'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1bb-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1bb-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1bb-report.py'
TRACK_WIDTH=0.30
TARGET_PAD=(20.850,5.775)
GND_VIA=(19.850,5.775)
VIA_SIZE=0.60
VIA_DRILL=0.30
EXPECTED_J9_P1=[(20.850,5.775),(26.000,5.775)]
EXPECTED_J9_P2=[(20.850,7.475),(26.000,7.475)]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pads(fp,n): return [p for p in fp.Pads() if str(p.GetNumber())==str(n)]
def pos(p): return (round(mm(p.GetPosition().x),6),round(mm(p.GetPosition().y),6))
def positions(fp,n): return sorted(pos(p) for p in pads(fp,n))
def add_track(board,net,a,b):
    t=pcbnew.PCB_TRACK(board); t.SetLayer(pcbnew.F_Cu); t.SetNet(net); t.SetWidth(iu(TRACK_WIDTH))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1]))); board.Add(t); return 1
def add_via(board,net,p):
    v=pcbnew.PCB_VIA(board); v.SetNet(net); v.SetPosition(pcbnew.VECTOR2I(iu(p[0]),iu(p[1])))
    v.SetWidth(iu(VIA_SIZE)); v.SetDrill(iu(VIA_DRILL)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); board.Add(v); return 1
def refill(board):
    zs=pcbnew.ZONES()
    for z in board.Zones(): zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1bb zone refill failed')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--route1ba-drc-json',required=True)
    ap.add_argument('--route1ba-pin-net-audit',required=True)
    args=ap.parse_args()

    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1ba report/PCB SHA mismatch')
    d=loadj(args.route1ba_drc_json); a=loadj(args.route1ba_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=122: raise SystemExit('route1ba DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1ba pin/net gate failed')

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={f.GetReference():f for f in board.GetFootprints()}
    j9=fps.get('J9')
    if j9 is None: raise SystemExit('route1bb missing J9')
    if j9.GetValue()!='EVQPUK02K_SIDE_BUTTON': raise SystemExit(f'route1bb J9 value gate failed: {j9.GetValue()!r}')
    p1=pads(j9,'1'); p2=pads(j9,'2')
    if len(p1)!=2 or len(p2)!=2: raise SystemExit(f'route1bb J9 duplicate-pad cardinality gate failed: pad1={len(p1)} pad2={len(p2)}')
    if any(p.GetNetname()!='GND' for p in p1): raise SystemExit('route1bb J9.1 net gate failed')
    if any(p.GetNetname()!='SIDE_BUTTON' for p in p2): raise SystemExit('route1bb J9.2 net gate failed')
    p1pos=positions(j9,'1'); p2pos=positions(j9,'2')
    if p1pos!=EXPECTED_J9_P1: raise SystemExit(f'route1bb J9.1 geometry gate failed: {p1pos}')
    if p2pos!=EXPECTED_J9_P2: raise SystemExit(f'route1bb J9.2 geometry gate failed: {p2pos}')
    target=[p for p in p1 if pos(p)==TARGET_PAD]
    if len(target)!=1: raise SystemExit(f'route1bb left J9.1 target cardinality gate failed: {len(target)}')

    net=board.FindNet('GND')
    if net is None: raise SystemExit('route1bb GND net reacquire failed')
    added=add_track(board,net,TARGET_PAD,GND_VIA)
    vias=add_via(board,net,GND_VIA)
    if added!=1 or vias!=1: raise SystemExit(f'route1bb routing scope gate failed: segments={added} vias={vias}')

    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1bb SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])

if __name__=='__main__':
    main()
