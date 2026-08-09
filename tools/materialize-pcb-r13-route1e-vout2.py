#!/usr/bin/env python3
"""r13 route-1e: add BUCK2 +3V0 output copper and VOUT2 sense return.

The high-current local leg is L102.2 -> C108.1 on F.Cu. U2 pin 32 is a VOUT2
sense node at the QFN top edge; because the existing SW1/VOUT1 copper and BUCK1
passives block a short legal F.Cu return to the BUCK2 output node, the sense
trace escapes to In2.Cu through two provisional through-vias. The In1.Cu GND
zone is refilled after via insertion so antipads are current before DRC.

Via/track dimensions are routing-seed geometry only, not fabrication authority.
No RF or supplier-gated interfaces are touched.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path
import pcbnew  # type: ignore

ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1d'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1d-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1d-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1d.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1e'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1e-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1e-r13.kicad_pro'
OUT_REPORT=OUT_DIR/'routing-seed-r13-1e.json'
WIDTH_POWER=0.40
WIDTH_SENSE=0.20
VIA_SIZE=0.60
VIA_DRILL=0.30

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pads(fp,num): return [p for p in fp.Pads() if str(p.GetNumber())==str(num)]
def point(fp,num):
    ps=pads(fp,num)
    if not ps: raise SystemExit(f'{fp.GetReference()} missing pad {num}')
    return (sum(mm(p.GetPosition().x) for p in ps)/len(ps), sum(mm(p.GetPosition().y) for p in ps)/len(ps))
def add_track(board,net,a,b,width,layer):
    t=pcbnew.PCB_TRACK(board); t.SetLayer(layer); t.SetNet(net); t.SetWidth(iu(width))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1]))); board.Add(t); return 1
def add_via(board,net,p):
    v=pcbnew.PCB_VIA(board); v.SetNet(net); v.SetPosition(pcbnew.VECTOR2I(iu(p[0]),iu(p[1]))); v.SetWidth(iu(VIA_SIZE)); v.SetDrill(iu(VIA_DRILL)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); board.Add(v); return 1

def refill_all_zones(board):
    zs=pcbnew.ZONES()
    for z in board.Zones(): zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('zone refill failed')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1d-drc-json',required=True); ap.add_argument('--route1d-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1d report/PCB SHA mismatch')
    d=loadj(args.route1d_drc_json); a=loadj(args.route1d_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=182: raise SystemExit('route1d DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1d pin/net gate failed')

    b=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in b.GetFootprints()}
    u2,l102,c108=fps['U2'],fps['L102'],fps['C108']
    pu=point(u2,'32'); pl=point(l102,'2'); pc=point(c108,'1')
    net=pads(u2,'32')[0].GetNet()
    names={net.GetNetname(),pads(l102,'2')[0].GetNetname(),pads(c108,'1')[0].GetNetname()}
    if names!={'+3V0'}: raise SystemExit(f'VOUT2 net gate failed: {names}')

    # High-current local output leg.
    segs=add_track(b,net,pl,pc,WIDTH_POWER,pcbnew.F_Cu)

    # Kelvin/sense escape. Three executed DRC probes bounded the legal gap:
    # x=10.00 conflicts alternately with NT101.1/U2.31; x=9.50 clears those but
    # approaches the existing +1V8 track. At (9.62,25.30), conservative copper
    # edge gaps are about 0.126 mm to NT101.1, 0.143 mm to U2.31 and 0.170 mm
    # to the +1V8 track, all above the 0.10 mm planning rule.
    via_top=(9.62,25.30)
    via_out=(4.80,33.828194)
    segs+=add_track(b,net,pu,via_top,WIDTH_SENSE,pcbnew.F_Cu)
    vias=add_via(b,net,via_top)
    segs+=add_track(b,net,via_top,via_out,WIDTH_SENSE,pcbnew.In2_Cu)
    vias+=add_via(b,net,via_out)
    segs+=add_track(b,net,via_out,pc,WIDTH_SENSE,pcbnew.F_Cu)

    refill_all_zones(b)
    b.SynchronizeNetsAndNetClasses(True); b.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),b): raise SystemExit('SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    out={'revision':'r13-route1e-vout2-local-and-sense','source_route1d_sha256':srcsha,'output_sha256':sha(OUT_PCB),'power_track_width_mm':WIDTH_POWER,'sense_track_width_mm':WIDTH_SENSE,'via_size_mm':VIA_SIZE,'via_drill_mm':VIA_DRILL,'track_segments_added':segs,'vias_added':vias,'routed_nets_added':['+3V0'],'power_points_mm':[pl,pc],'sense_points_mm':[pu,via_top,via_out,pc],'sense_layer':'In2.Cu between vias','gnd_plane_refilled':True,'rf_routing_touched':False,'supplier_gated_interfaces_touched':False,'routing_status':'VOUT2_LOCAL_AND_SENSE_ADDED','validation_status':'PENDING_EXECUTED_KICAD_DRC','release_status':'NOT_FOR_GERBER'}
    OUT_REPORT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
