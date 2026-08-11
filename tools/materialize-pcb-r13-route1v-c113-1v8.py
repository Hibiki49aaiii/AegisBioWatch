#!/usr/bin/env python3
"""r13 route-1v: connect U2.12/+1V8 directly to C113.1/+1V8.

Source: executed-KiCad-clean route-1u (0 violations / 154 unconnected /
268-node physical audit PASS).

The executed route-1u ratsnest names U2.12 and C113.1 as the local +1V8 pair.
This increment adds one 0.20 mm F.Cu segment only; no via or placement change.
"""
from __future__ import annotations

import argparse
import faulthandler
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

import pcbnew  # type: ignore
faulthandler.enable()

ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1u'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1u-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1u-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1u.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1v'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1v-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1v-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1v-report.py'
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
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1v zone refill failed')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1u-drc-json',required=True); ap.add_argument('--route1u-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1u report/PCB SHA mismatch')
    d=loadj(args.route1u_drc_json); a=loadj(args.route1u_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=154: raise SystemExit('route1u DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1u pin/net gate failed')
    board=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in board.GetFootprints()}
    u2=fps.get('U2'); c113=fps.get('C113')
    if u2 is None or c113 is None: raise SystemExit('route1v missing U2/C113')
    gates={'U2.12':pads(u2,'12')[0].GetNetname(),'C113.1':pads(c113,'1')[0].GetNetname(),'C113.value':c113.GetValue()}
    if gates!={'U2.12':'+1V8','C113.1':'+1V8','C113.value':'100nF X5R'}: raise SystemExit(f'route1v net/value gate failed: {gates}')
    p1=point(u2,'12'); p2=point(c113,'1')
    if abs(p1[0]-11.1875)>0.001 or abs(p1[1]-30.95)>0.001: raise SystemExit(f'route1v U2.12 geometry gate failed: {p1}')
    if abs(p2[0]-12.245188)>0.001 or abs(p2[1]-32.399818)>0.001: raise SystemExit(f'route1v C113.1 geometry gate failed: {p2}')
    net=board.FindNet('+1V8')
    if net is None: raise SystemExit('route1v +1V8 net reacquire failed')
    if add_track(board,net,p1,p2)!=1: raise SystemExit('route1v scope gate failed')
    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1v SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])
if __name__=='__main__': main()
