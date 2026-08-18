#!/usr/bin/env python3
"""r13 route-1z: close C101.2/GND to the accepted local GND via.

Source: executed-KiCad-clean route-1y (0 violations / 150 unconnected /
268-node physical audit PASS).

C101 is rotated such that C101.1/CHG_5V lies directly between C101.2/GND and
accepted GND via (16.85,30.49); therefore a direct segment is forbidden. This
increment escapes right to x=17.95, drops below the CHG_5V pad, then returns to
the existing GND via. CHG_5V geometry is not modified.

KiCad may choose a different same-net ratsnest peer when a board is regenerated,
so source validation intentionally does not require C101.2 to be paired with one
specific GND via in the DRC JSON. Instead it independently proves that C101.2 is
still reported unconnected and that the intended accepted GND via exists on the
source PCB with the correct net and coordinates.
"""
from __future__ import annotations
import argparse, faulthandler, hashlib, json, os, shutil, sys
from pathlib import Path
import pcbnew  # type: ignore
faulthandler.enable()

ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1y'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1y-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1y-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1y.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1z'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1z-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1z-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1z-report.py'
TRACK_WIDTH=0.30
BEND1=(17.95,28.024501)
BEND2=(17.95,30.49)
GND_VIA=(16.85,30.49)


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
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1z zone refill failed')
def has_unconnected_c101_gnd_pad(d):
    want=('Pad 2 [GND] of C101',17.141428,28.024501)
    for u in d.get('unconnected_items',[]):
        for it in u.get('items',[]):
            p=it.get('pos',{})
            desc=it.get('description','')
            x=float(p.get('x',999)); y=float(p.get('y',999))
            if want[0] in desc and abs(x-want[1])<0.001 and abs(y-want[2])<0.001:
                return True
    return False
def has_target_gnd_via(board):
    for item in board.GetTracks():
        if not isinstance(item, pcbnew.PCB_VIA):
            continue
        p=item.GetPosition()
        x=mm(p.x); y=mm(p.y)
        if abs(x-GND_VIA[0])<0.001 and abs(y-GND_VIA[1])<0.001 and item.GetNetname()=='GND':
            return True
    return False


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1y-drc-json',required=True); ap.add_argument('--route1y-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1y report/PCB SHA mismatch')
    d=loadj(args.route1y_drc_json); a=loadj(args.route1y_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=150: raise SystemExit('route1y DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1y pin/net gate failed')
    if not has_unconnected_c101_gnd_pad(d): raise SystemExit('route1z source gap gate failed: C101.2/GND is not present in route1y unconnected evidence')

    board=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in board.GetFootprints()}
    c101=fps.get('C101')
    if c101 is None: raise SystemExit('route1z missing C101')
    gates={'C101.1':pads(c101,'1')[0].GetNetname(),'C101.2':pads(c101,'2')[0].GetNetname()}
    if gates!={'C101.1':'CHG_5V','C101.2':'GND'}: raise SystemExit(f'route1z C101 net gate failed: {gates}')
    gnd_pad=point(c101,'2'); chg_pad=point(c101,'1')
    if abs(gnd_pad[0]-17.141428)>0.001 or abs(gnd_pad[1]-28.024501)>0.001: raise SystemExit(f'route1z C101.2 geometry gate failed: {gnd_pad}')
    if abs(chg_pad[0]-17.141428)>0.001 or abs(chg_pad[1]-29.574501)>0.001: raise SystemExit(f'route1z C101.1 geometry gate failed: {chg_pad}')
    if not has_target_gnd_via(board): raise SystemExit('route1z source target gate failed: accepted GND via (16.85,30.49) not found on GND')
    net=board.FindNet('GND')
    if net is None: raise SystemExit('route1z GND net reacquire failed')
    added=0
    added+=add_track(board,net,gnd_pad,BEND1)
    added+=add_track(board,net,BEND1,BEND2)
    added+=add_track(board,net,BEND2,GND_VIA)
    if added!=3: raise SystemExit('route1z routing scope gate failed')
    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1z SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])
if __name__=='__main__': main()
