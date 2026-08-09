#!/usr/bin/env python3
"""r13 route-1g: refine SW/VSYS escapes to open top-copper PVSS corridors.

This stage does not add new logical connectivity. It replaces the accepted
route-1b SW1/SW2 doglegs and route-1f VSYS dogleg with shorter, diverging
routes. The objective is to make the Nordic-critical PVSS1/PVSS2 local returns
routable on F.Cu without via-in-pad or cutting the continuous In1.Cu GND plane.

Source gate: route-1f must be executed-KiCad-clean at 0 violations / 178
unconnected with the 268-node physical pad/net audit PASS.

Planning/evidence artifact only; not fabrication authority.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path
import pcbnew  # type: ignore

ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1f'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1f-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1f-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1f.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1g'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1g-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1g-r13.kicad_pro'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1g.json'
SW_WIDTH=0.20
VSYS_WIDTH=0.30
SW_ESCAPE_X=8.70
VSYS_ESCAPE_X=8.50

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pads(fp,num): return [p for p in fp.Pads() if str(p.GetNumber())==str(num)]
def point(fp,num):
    ps=pads(fp,num)
    if not ps: raise SystemExit(f'{fp.GetReference()} missing pad {num}')
    return (sum(mm(p.GetPosition().x) for p in ps)/len(ps),sum(mm(p.GetPosition().y) for p in ps)/len(ps))
def add_track(board,net,a,b,width):
    t=pcbnew.PCB_TRACK(board); t.SetLayer(pcbnew.F_Cu); t.SetNet(net); t.SetWidth(iu(width))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1]))); board.Add(t); return 1

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1f-drc-json',required=True); ap.add_argument('--route1f-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1f report/PCB SHA mismatch')
    d=loadj(args.route1f_drc_json); a=loadj(args.route1f_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=178: raise SystemExit('route1f DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1f pin/net gate failed')

    b=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in b.GetFootprints()}
    u2,l101,l102,c103,c104=fps['U2'],fps['L101'],fps['L102'],fps['C103'],fps['C104']

    # Resolve every footprint/pad-derived datum before mutating the board.
    # KiCad 9 SWIG wrappers for unrelated board items can become stale after
    # BOARD.Remove(), so no cached FOOTPRINT/PAD wrapper is reused afterwards.
    sw1_name=pads(u2,'3')[0].GetNetname(); sw2_name=pads(u2,'5')[0].GetNetname(); vsys_name=pads(u2,'4')[0].GetNetname()
    if {sw1_name,sw2_name,vsys_name}!={'PMIC_SW1','PMIC_SW2','VSYS'}: raise SystemExit('critical net gate failed')
    if pads(l101,'1')[0].GetNetname()!='PMIC_SW1' or pads(l102,'1')[0].GetNetname()!='PMIC_SW2': raise SystemExit('inductor SW pad gate failed')
    if pads(c103,'1')[0].GetNetname()!='VSYS' or pads(c104,'1')[0].GetNetname()!='VSYS': raise SystemExit('VSYS cap gate failed')
    u3=point(u2,'3'); u5=point(u2,'5'); u4=point(u2,'4')
    l1=point(l101,'1'); l2=point(l102,'1'); p103=point(c103,'1'); p104=point(c104,'1')
    e1=(SW_ESCAPE_X,u3[1]); e2=(SW_ESCAPE_X,u5[1]); ev=(VSYS_ESCAPE_X,u4[1])

    # Remove only F.Cu track segments on the three locally controlled nets.
    removed=[]
    for item in list(b.GetTracks()):
        if not isinstance(item,pcbnew.PCB_TRACK) or isinstance(item,pcbnew.PCB_VIA): continue
        if item.GetLayer()!=pcbnew.F_Cu: continue
        nn=item.GetNetname()
        if nn in {'PMIC_SW1','PMIC_SW2','VSYS'}:
            removed.append(nn); b.Remove(item)
    if removed.count('PMIC_SW1')!=3 or removed.count('PMIC_SW2')!=4 or removed.count('VSYS')!=4:
        raise SystemExit(f'unexpected controlled-track counts removed: {removed}')

    # Reacquire nets from the mutated board; do not reuse stale PAD-derived
    # NETINFO_ITEM wrappers across Remove() calls.
    n_sw1=b.FindNet(sw1_name); n_sw2=b.FindNet(sw2_name); n_vsys=b.FindNet(vsys_name)
    if n_sw1 is None or n_sw2 is None or n_vsys is None: raise SystemExit('controlled net reacquire failed')

    # Short pad-row escape, then diverge away from PVSS pins instead of forming
    # vertical copper walls beside the QFN.
    added=0
    added+=add_track(b,n_sw1,u3,e1,SW_WIDTH); added+=add_track(b,n_sw1,e1,l1,SW_WIDTH)
    added+=add_track(b,n_sw2,u5,e2,SW_WIDTH); added+=add_track(b,n_sw2,e2,l2,SW_WIDTH)
    # With SW2 now diverging down-left, VSYS can leave U2.4 above it and head
    # directly toward the two input capacitors without the previous x=7.75 wall.
    added+=add_track(b,n_vsys,u4,ev,VSYS_WIDTH); added+=add_track(b,n_vsys,ev,p103,VSYS_WIDTH); added+=add_track(b,n_vsys,p103,p104,VSYS_WIDTH)

    b.SynchronizeNetsAndNetClasses(True); b.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),b): raise SystemExit('SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    out={
      'revision':'r13-route1g-pvss-corridor-refinement',
      'source_route1f_sha256':srcsha,
      'output_sha256':sha(OUT_PCB),
      'removed_track_segments':len(removed),
      'removed_by_net':{n:removed.count(n) for n in sorted(set(removed))},
      'added_track_segments':added,
      'vias_added':0,
      'sw_track_width_mm':SW_WIDTH,
      'vsys_track_width_mm':VSYS_WIDTH,
      'sw_escape_x_mm':SW_ESCAPE_X,
      'vsys_escape_x_mm':VSYS_ESCAPE_X,
      'sw1_points_mm':[u3,e1,l1],
      'sw2_points_mm':[u5,e2,l2],
      'vsys_points_mm':[u4,ev,p103,p104],
      'logical_connectivity_added':False,
      'target':'open F.Cu approach corridors for PVSS1/PVSS2 local returns',
      'in1_gnd_plane_preserved':True,
      'rf_routing_touched':False,
      'supplier_gated_interfaces_touched':False,
      'validation_status':'PENDING_EXECUTED_KICAD_DRC',
      'release_status':'NOT_FOR_GERBER'
    }
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
