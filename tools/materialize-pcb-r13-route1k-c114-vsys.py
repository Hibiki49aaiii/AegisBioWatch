#!/usr/bin/env python3
"""r13 route-1k: relocate and connect C114 as the local VSYS HF decoupler.

Source: executed-KiCad-clean route-1j (0 violations / 170 unconnected /
268-node physical audit PASS).

Two fixed-position routing attempts from the old C114 location were rejected by
executed DRC because that location is trapped between SW1/PVSS/R502 copper.
This revision moves only C114 into the free corridor beside U2.20/VSYS and
connects it directly to U2.20 plus a short GND-plane via.

C102 bulk VSYS, VBAT/charger, RF and supplier-gated interfaces remain deferred.
"""
from __future__ import annotations
import argparse, faulthandler, hashlib, json, os, shutil, sys
from pathlib import Path
import pcbnew  # type: ignore
faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1j'; SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1j-r13.kicad_pcb'; SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1j-r13.kicad_pro'; SRC_REPORT=SRC_DIR/'routing-seed-r13-1j.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1k'; OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1k-r13.kicad_pcb'; OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1k-r13.kicad_pro'; REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1k-report.py'
VSYS_WIDTH=0.30; GND_WIDTH=0.30; VIA_SIZE=0.60; VIA_DRILL=0.30
C114_NEW=(15.05,27.25); VSYS_ESCAPE_X=14.65; C114_GND_VIA=(15.05,26.45)

def stage(n): print(f'[route1k] {n}',flush=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pads(fp,n): return [p for p in fp.Pads() if str(p.GetNumber())==str(n)]
def point(fp,n):
    ps=pads(fp,n)
    if not ps: raise SystemExit(f'{fp.GetReference()} missing pad {n}')
    return (sum(mm(p.GetPosition().x) for p in ps)/len(ps),sum(mm(p.GetPosition().y) for p in ps)/len(ps))
def add_track(b,net,a,c,w):
    t=pcbnew.PCB_TRACK(b); t.SetLayer(pcbnew.F_Cu); t.SetNet(net); t.SetWidth(iu(w)); t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(c[0]),iu(c[1]))); b.Add(t); return 1
def add_via(b,net,p):
    v=pcbnew.PCB_VIA(b); v.SetNet(net); v.SetPosition(pcbnew.VECTOR2I(iu(p[0]),iu(p[1]))); v.SetWidth(iu(VIA_SIZE)); v.SetDrill(iu(VIA_DRILL)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); b.Add(v); return 1
def refill(b):
    zs=pcbnew.ZONES()
    for z in b.Zones(): zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(b).Fill(zs): raise SystemExit('route1k zone refill failed')
def main():
    stage('start'); ap=argparse.ArgumentParser(); ap.add_argument('--route1j-drc-json',required=True); ap.add_argument('--route1j-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1j report/PCB SHA mismatch')
    d=loadj(args.route1j_drc_json); a=loadj(args.route1j_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=170: raise SystemExit('route1j DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1j audit gate failed')
    b=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in b.GetFootprints()}; c=fps['C114']; u2=fps['U2']
    if {'1':pads(c,'1')[0].GetNetname(),'2':pads(c,'2')[0].GetNetname(),'u2.20':pads(u2,'20')[0].GetNetname()}!={'1':'VSYS','2':'GND','u2.20':'VSYS'}: raise SystemExit('route1k net gate failed')
    old1=point(c,'1'); old2=point(c,'2')
    if max(abs(old1[0]-6.892232),abs(old1[1]-27.030566),abs(old2[0]-6.892232),abs(old2[1]-26.390566))>.001: raise SystemExit(f'route1k source C114 geometry gate failed {old1} {old2}')
    u20=point(u2,'20')
    if max(abs(u20[0]-13.8875),abs(u20[1]-28.75))>.001: raise SystemExit(f'route1k U2.20 geometry gate failed {u20}')
    c.SetPosition(pcbnew.VECTOR2I(iu(C114_NEW[0]),iu(C114_NEW[1]))); c.SetOrientationDegrees(90.0)
    p1=point(c,'1'); p2=point(c,'2')
    expected1=(15.05,27.57); expected2=(15.05,26.93)
    if max(abs(p1[0]-expected1[0]),abs(p1[1]-expected1[1]),abs(p2[0]-expected2[0]),abs(p2[1]-expected2[1]))>.001: raise SystemExit(f'route1k moved C114 geometry failed {p1} {p2}')
    vsys=b.FindNet('VSYS'); gnd=b.FindNet('GND'); added=vias=0
    a1=(VSYS_ESCAPE_X,u20[1]); a2=(VSYS_ESCAPE_X,p1[1])
    added+=add_track(b,vsys,u20,a1,VSYS_WIDTH); added+=add_track(b,vsys,a1,a2,VSYS_WIDTH); added+=add_track(b,vsys,a2,p1,VSYS_WIDTH)
    added+=add_track(b,gnd,p2,C114_GND_VIA,GND_WIDTH); vias+=add_via(b,gnd,C114_GND_VIA)
    if added!=4 or vias!=1: raise SystemExit(f'route1k scope failed {added=} {vias=}')
    refill(b); b.SynchronizeNetsAndNetClasses(True); b.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),b): raise SystemExit('route1k SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    stage('board saved'); os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])
if __name__=='__main__': main()
