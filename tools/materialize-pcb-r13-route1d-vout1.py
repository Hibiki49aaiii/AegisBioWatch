#!/usr/bin/env python3
"""r13 route-1d: add the local BUCK1 VOUT1 / +1V8 path only.

Source is route-1c with the continuous In1.Cu GND plane already filled. This
stage connects U2 pin 1 (+1V8 feedback/output node) to L101 pad 2 and then to
C107 pad 1. No other +1V8 distribution, PVSS return, vias, RF, or supplier-
gated interfaces are touched.

Planning/evidence artifact only; not fabrication authority.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path
import pcbnew  # type: ignore

ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1c'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1c-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1c-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1c.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1d'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1d-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1d-r13.kicad_pro'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1d.json'
WIDTH=0.35

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pads(fp,num): return [p for p in fp.Pads() if str(p.GetNumber())==str(num)]
def point(fp,num):
    ps=pads(fp,num)
    if not ps: raise SystemExit(f'{fp.GetReference()} missing pad {num}')
    return (sum(mm(p.GetPosition().x) for p in ps)/len(ps), sum(mm(p.GetPosition().y) for p in ps)/len(ps))
def add_track(board,net,a,b,width=WIDTH):
    t=pcbnew.PCB_TRACK(board); t.SetLayer(pcbnew.F_Cu); t.SetNet(net); t.SetWidth(iu(width))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1]))); board.Add(t); return 1

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1c-drc-json',required=True); ap.add_argument('--route1c-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1c report/PCB SHA mismatch')
    d=loadj(args.route1c_drc_json); a=loadj(args.route1c_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=184: raise SystemExit('route1c DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1c pin/net gate failed')

    b=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in b.GetFootprints()}
    u2,l101,c107=fps['U2'],fps['L101'],fps['C107']
    pu=point(u2,'1'); pl=point(l101,'2'); pc=point(c107,'1')
    nu=pads(u2,'1')[0].GetNet(); nl=pads(l101,'2')[0].GetNet(); nc=pads(c107,'1')[0].GetNet()
    names={nu.GetNetname(),nl.GetNetname(),nc.GetNetname()}
    if names!={'+1V8'}: raise SystemExit(f'VOUT1 net gate failed: {names}')

    # U2.1 is the uppermost left-edge QFN pad, so a direct run toward L101.2
    # moves away from the adjacent QFN pad row. The second segment terminates at
    # the local BUCK1 output capacitor and stays above NT101/PVSS1 routing space.
    segs=add_track(b,nu,pu,pl)+add_track(b,nu,pl,pc)
    b.SynchronizeNetsAndNetClasses(True); b.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),b): raise SystemExit('SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    out={'revision':'r13-route1d-vout1-local','source_route1c_sha256':srcsha,'output_sha256':sha(OUT_PCB),'track_width_mm':WIDTH,'track_segments_added':segs,'vias_added':0,'routed_nets_added':['+1V8'],'vout1_points_mm':[pu,pl,pc],'scope':'U2.1 -> L101.2 -> C107.1 only','gnd_plane_preserved':True,'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,'routing_status':'VOUT1_LOCAL_ADDED','validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
