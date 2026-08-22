#!/usr/bin/env python3
"""r13 route-1av: close U4.8/GND directly into continuous In1.Cu GND.

Source: executed-KiCad-clean route-1au (0 violations / 128 unconnected /
268-node physical audit PASS). This increment routes only the DRV2605L ground
pad U4.8 with one short F.Cu segment and one standard through via. U4.7 and
U4.9 signal pads, all accepted route-1au geometry, RF routing, and
supplier-gated interfaces remain unchanged.
"""
from __future__ import annotations
import argparse,faulthandler,hashlib,json,os,shutil,sys
from pathlib import Path
import pcbnew  # type: ignore

faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1au'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1au-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1au-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1au.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1av'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1av-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1av-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1av-report.py'
TRACK_WIDTH=0.30
GND_VIA=(24.10,14.40)
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
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1av zone refill failed')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--route1au-drc-json',required=True)
    ap.add_argument('--route1au-pin-net-audit',required=True)
    args=ap.parse_args()

    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1au report/PCB SHA mismatch')
    d=loadj(args.route1au_drc_json); a=loadj(args.route1au_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=128: raise SystemExit('route1au DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1au pin/net gate failed')

    board=pcbnew.LoadBoard(str(SRC_PCB))
    fps={f.GetReference():f for f in board.GetFootprints()}
    u4=fps.get('U4')
    if u4 is None: raise SystemExit('route1av missing U4')
    expected={'U4.value':'DRV2605LDGSR','U4.7':'HAPTIC_OUT_P','U4.8':'GND','U4.9':'HAPTIC_OUT_N'}
    gates={'U4.value':u4.GetValue()}
    for n in ('7','8','9'):
        ps=pads(u4,n)
        if len(ps)!=1: raise SystemExit(f'route1av U4 pad {n} cardinality gate failed')
        gates[f'U4.{n}']=ps[0].GetNetname()
    if gates!=expected: raise SystemExit(f'route1av U4 net/value gate failed: {gates}')

    p7=point(u4,'7'); gnd_pad=point(u4,'8'); p9=point(u4,'9')
    expected_points={'U4.7':(23.005,14.900),'U4.8':(23.005,14.400),'U4.9':(23.005,13.900)}
    for name,actual in [('U4.7',p7),('U4.8',gnd_pad),('U4.9',p9)]:
        ex=expected_points[name]
        if abs(actual[0]-ex[0])>0.001 or abs(actual[1]-ex[1])>0.001:
            raise SystemExit(f'route1av {name} geometry gate failed: {actual}')
    net=board.FindNet('GND')
    if net is None: raise SystemExit('route1av GND net reacquire failed')
    added=add_track(board,net,gnd_pad,GND_VIA)
    vias=add_via(board,net,GND_VIA)
    if added!=1 or vias!=1: raise SystemExit(f'route1av routing scope gate failed: segments={added} vias={vias}')

    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1av SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])

if __name__=='__main__':
    main()
