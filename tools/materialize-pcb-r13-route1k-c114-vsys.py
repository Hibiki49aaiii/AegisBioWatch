#!/usr/bin/env python3
"""r13 route-1k: close the C114 VSYS high-frequency decoupling loop.

Source: executed-KiCad-clean route-1j (0 violations / 170 unconnected /
268-node physical audit PASS).

This increment is intentionally limited to C114. VSYS crosses under SW1 on
B.Cu between two deliberate vias; C114 GND uses one short F.Cu stub and a
through-via into the continuous In1.Cu GND reference. C102 bulk VSYS,
VBAT/charger, RF and supplier-gated interfaces remain deferred.
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
VSYS_CAP_VIA=(6.15,27.05); VSYS_SPINE_VIA=(7.35,29.40); C114_GND_VIA=(6.60,25.90)

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
def add_track(b,net,a,c,w,layer):
    t=pcbnew.PCB_TRACK(b); t.SetLayer(layer); t.SetNet(net); t.SetWidth(iu(w)); t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(c[0]),iu(c[1]))); b.Add(t); return 1
def add_via(b,net,p):
    v=pcbnew.PCB_VIA(b); v.SetNet(net); v.SetPosition(pcbnew.VECTOR2I(iu(p[0]),iu(p[1]))); v.SetWidth(iu(VIA_SIZE)); v.SetDrill(iu(VIA_DRILL)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); b.Add(v); return 1
def refill(b):
    zs=pcbnew.ZONES()
    for z in b.Zones(): zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(b).Fill(zs): raise SystemExit('route1k zone refill failed')
def has_vsys_spine(b):
    for i in b.GetTracks():
        if isinstance(i,pcbnew.PCB_VIA) or i.GetNetname()!='VSYS' or i.GetLayer()!=pcbnew.F_Cu: continue
        s=(mm(i.GetStart().x),mm(i.GetStart().y)); e=(mm(i.GetEnd().x),mm(i.GetEnd().y))
        if abs(s[0]-7.35)<.01 and abs(e[0]-7.35)<.01 and {round(s[1],6),round(e[1],6)}=={28.25,29.815584}: return True
    return False

def main():
    stage('start'); ap=argparse.ArgumentParser(); ap.add_argument('--route1j-drc-json',required=True); ap.add_argument('--route1j-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1j report/PCB SHA mismatch')
    d=loadj(args.route1j_drc_json); a=loadj(args.route1j_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=170: raise SystemExit('route1j DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1j audit gate failed')
    b=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in b.GetFootprints()}; c=fps['C114']
    if {'1':pads(c,'1')[0].GetNetname(),'2':pads(c,'2')[0].GetNetname()}!={'1':'VSYS','2':'GND'}: raise SystemExit('route1k C114 net gate failed')
    p1=point(c,'1'); p2=point(c,'2')
    if max(abs(p1[0]-6.892232),abs(p1[1]-27.030566),abs(p2[0]-6.892232),abs(p2[1]-26.390566))>.001: raise SystemExit(f'route1k C114 geometry gate failed: {p1} {p2}')
    if not has_vsys_spine(b): raise SystemExit('route1k accepted VSYS spine gate failed')
    vsys=b.FindNet('VSYS'); gnd=b.FindNet('GND'); added=vias=0
    added+=add_track(b,vsys,p1,VSYS_CAP_VIA,VSYS_WIDTH,pcbnew.F_Cu); vias+=add_via(b,vsys,VSYS_CAP_VIA)
    added+=add_track(b,vsys,VSYS_CAP_VIA,VSYS_SPINE_VIA,VSYS_WIDTH,pcbnew.B_Cu); vias+=add_via(b,vsys,VSYS_SPINE_VIA)
    added+=add_track(b,gnd,p2,C114_GND_VIA,GND_WIDTH,pcbnew.F_Cu); vias+=add_via(b,gnd,C114_GND_VIA)
    if added!=3 or vias!=3: raise SystemExit(f'route1k scope failed {added=} {vias=}')
    refill(b); b.SynchronizeNetsAndNetClasses(True); b.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),b): raise SystemExit('route1k SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    stage('board saved'); os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])
if __name__=='__main__': main()
