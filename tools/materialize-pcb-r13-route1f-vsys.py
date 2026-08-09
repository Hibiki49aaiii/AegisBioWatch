#!/usr/bin/env python3
"""r13 route-1f: add the local VSYS/PVDD input decoupling spine.

Source is the executed-KiCad-clean route-1e board. This stage connects only:

    U2.4 VSYS -> C103.1 -> C104.1

C114 is deliberately deferred because its rotated pad-2 GND sits between the
main VSYS corridor and C114.1; forcing a direct branch would cross foreign
copper. No PVSS return, GND stitching, charger, RF, or supplier-gated interface
routing is added here.

Planning/evidence artifact only; not fabrication authority.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path
import pcbnew  # type: ignore

ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1e'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1e-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1e-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1e.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1f'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1f-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1f-r13.kicad_pro'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1f.json'
WIDTH=0.30

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pads(fp,num): return [p for p in fp.Pads() if str(p.GetNumber())==str(num)]
def point(fp,num):
    ps=pads(fp,num)
    if not ps: raise SystemExit(f'{fp.GetReference()} missing pad {num}')
    return (sum(mm(p.GetPosition().x) for p in ps)/len(ps),sum(mm(p.GetPosition().y) for p in ps)/len(ps))
def add_track(board,net,a,b):
    t=pcbnew.PCB_TRACK(board); t.SetLayer(pcbnew.F_Cu); t.SetNet(net); t.SetWidth(iu(WIDTH))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1]))); board.Add(t); return 1

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1e-drc-json',required=True); ap.add_argument('--route1e-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1e report/PCB SHA mismatch')
    d=loadj(args.route1e_drc_json); a=loadj(args.route1e_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=180: raise SystemExit('route1e DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1e pin/net gate failed')

    b=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in b.GetFootprints()}
    u2,c103,c104=fps['U2'],fps['C103'],fps['C104']
    pu=point(u2,'4'); p103=point(c103,'1'); p104=point(c104,'1')
    net=pads(u2,'4')[0].GetNet()
    names={net.GetNetname(),pads(c103,'1')[0].GetNetname(),pads(c104,'1')[0].GetNetname()}
    if names!={'VSYS'}: raise SystemExit(f'VSYS net gate failed: {names}')

    # U2.4 lies midway between the already-routed SW1/SW2 left-edge escapes.
    # The 0.30 mm VSYS spine keeps >0.10 mm planning clearance to both 0.20 mm
    # switching tracks, then continues across the two same-net input caps.
    segs=add_track(b,net,pu,p103)+add_track(b,net,p103,p104)
    b.SynchronizeNetsAndNetClasses(True); b.BuildConnectivity()

    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),b): raise SystemExit('SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    out={
      'revision':'r13-route1f-vsys-local-input',
      'source_route1e_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'track_width_mm':WIDTH,
      'track_segments_added':segs,
      'vias_added':0,
      'routed_nets_added':['VSYS'],
      'vsys_points_mm':[pu,p103,p104],
      'scope':'U2.4 -> C103.1 -> C104.1 only',
      'c114_deferred':True,
      'gnd_plane_preserved':True,
      'rf_routing_touched':False,
      'supplier_gated_interfaces_touched':False,
      'routing_status':'VSYS_LOCAL_INPUT_SPINE_ADDED',
      'validation_status':'PENDING_EXECUTED_KICAD_DRC',
      'release_status':'NOT_FOR_GERBER'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
