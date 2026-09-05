#!/usr/bin/env python3
"""r13 route-1bc: close C2.1/+1V8 to C3.1/+1V8 with one direct F.Cu segment.

Source: accepted route-1bb (0 violations / 121 unconnected / 268-node
physical audit PASS). This increment adds only one 0.30 mm vertical F.Cu
segment between the existing +1V8 pads C2.1 and C3.1. No via, placement,
RF, PMIC/I2C-deferred, or supplier-gated geometry is changed.
"""
from __future__ import annotations
import argparse,faulthandler,hashlib,json,os,shutil,sys
from pathlib import Path
import pcbnew  # type: ignore

faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bb'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1bb-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1bb-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1bb.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1bc'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1bc-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1bc-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1bc-report.py'
TRACK_WIDTH=0.30
C2_P1=(41.005,11.975)
C3_P1=(41.005,13.475)
EXPECTED_C2_P2=(41.645,11.975)
EXPECTED_C3_P2=(41.645,13.475)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pads(fp,n): return [p for p in fp.Pads() if str(p.GetNumber())==str(n)]
def pos(p): return (round(mm(p.GetPosition().x),6),round(mm(p.GetPosition().y),6))
def one_pad(fp,n):
    ps=pads(fp,n)
    if len(ps)!=1: raise SystemExit(f'route1bc {fp.GetReference()}.{n} cardinality gate failed: {len(ps)}')
    return ps[0]
def add_track(board,net,a,b):
    t=pcbnew.PCB_TRACK(board)
    t.SetLayer(pcbnew.F_Cu); t.SetNet(net); t.SetWidth(iu(TRACK_WIDTH))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1])))
    t.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1])))
    board.Add(t)
    return 1
def refill(board):
    zs=pcbnew.ZONES()
    for z in board.Zones(): zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs):
        raise SystemExit('route1bc zone refill failed')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--route1bb-drc-json',required=True)
    ap.add_argument('--route1bb-pin-net-audit',required=True)
    args=ap.parse_args()

    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1bb report/PCB SHA mismatch')
    d=loadj(args.route1bb_drc_json); a=loadj(args.route1bb_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=121:
        raise SystemExit('route1bb DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268:
        raise SystemExit('route1bb pin/net gate failed')

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={f.GetReference():f for f in board.GetFootprints()}
    c2=fps.get('C2'); c3=fps.get('C3')
    if c2 is None or c3 is None: raise SystemExit('route1bc missing C2/C3')
    if c2.GetValue()!='100nF' or c3.GetValue()!='100nF':
        raise SystemExit(f'route1bc C2/C3 value gate failed: {c2.GetValue()!r}/{c3.GetValue()!r}')

    c2p1=one_pad(c2,'1'); c2p2=one_pad(c2,'2'); c3p1=one_pad(c3,'1'); c3p2=one_pad(c3,'2')
    if c2p1.GetNetname()!='+1V8' or c3p1.GetNetname()!='+1V8':
        raise SystemExit('route1bc +1V8 pad net gate failed')
    if c2p2.GetNetname()!='GND' or c3p2.GetNetname()!='GND':
        raise SystemExit('route1bc GND pad net gate failed')
    if pos(c2p1)!=C2_P1 or pos(c3p1)!=C3_P1:
        raise SystemExit(f'route1bc target coordinate gate failed: C2.1={pos(c2p1)} C3.1={pos(c3p1)}')
    if pos(c2p2)!=EXPECTED_C2_P2 or pos(c3p2)!=EXPECTED_C3_P2:
        raise SystemExit(f'route1bc adjacent GND coordinate gate failed: C2.2={pos(c2p2)} C3.2={pos(c3p2)}')

    net=board.FindNet('+1V8')
    if net is None: raise SystemExit('route1bc +1V8 net reacquire failed')
    added=add_track(board,net,C2_P1,C3_P1)
    if added!=1: raise SystemExit(f'route1bc routing scope gate failed: segments={added}')

    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1bc SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])

if __name__=='__main__':
    main()
