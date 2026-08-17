#!/usr/bin/env python3
"""r13 route-1x: connect the R103/R104 +1V8 pull-up branch to route-1v +1V8.

Source: executed-KiCad-clean route-1w (0 violations / 152 unconnected /
268-node physical audit PASS).

Two F.Cu-only candidates were rejected by executed KiCad DRC because accepted
GND vias block the local corridor. This revision does not force another same-
layer escape. It places one +1V8 through via directly on the accepted R103-R104
pull-up branch, a second +1V8 through via directly on the accepted route-1v
+1V8 track, and joins them with one 0.20 mm In2.Cu segment. The local In2.Cu
window is unused by accepted routing. No I2C signal pad or component placement
is modified.
"""
from __future__ import annotations
import argparse,faulthandler,hashlib,json,os,shutil,sys
from pathlib import Path
import pcbnew  # type: ignore
faulthandler.enable()
ROOT=Path(__file__).resolve().parents[1]
SRC_DIR=ROOT/'hardware/main-board/pcb/route-r13-1w'
SRC_PCB=SRC_DIR/'AegisBioWatch-MainBoard-Route1w-r13.kicad_pcb'
SRC_PRO=SRC_DIR/'AegisBioWatch-MainBoard-Route1w-r13.kicad_pro'
SRC_REPORT=SRC_DIR/'routing-seed-r13-1w.json'
OUT_DIR=ROOT/'hardware/main-board/pcb/route-r13-1x'
OUT_PCB=OUT_DIR/'AegisBioWatch-MainBoard-Route1x-r13.kicad_pcb'
OUT_PRO=OUT_DIR/'AegisBioWatch-MainBoard-Route1x-r13.kicad_pro'
REPORT_HELPER=ROOT/'tools/write-pcb-r13-route1x-report.py'
TRACK_WIDTH=0.20
VIA_SIZE=0.60
VIA_DRILL=0.30
BRANCH_VIA=(12.684473,34.267766)
TRUNK_VIA=(11.45,31.685729)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def mm(v): return float(pcbnew.ToMM(v))
def iu(v): return int(pcbnew.FromMM(v))
def pads(fp,n): return [p for p in fp.Pads() if str(p.GetNumber())==str(n)]
def point(fp,n):
    ps=pads(fp,n)
    if not ps: raise SystemExit(f'{fp.GetReference()} missing pad {n}')
    return (sum(mm(p.GetPosition().x) for p in ps)/len(ps),sum(mm(p.GetPosition().y) for p in ps)/len(ps))
def add_track(board,net,a,b,layer):
    t=pcbnew.PCB_TRACK(board); t.SetLayer(layer); t.SetNet(net); t.SetWidth(iu(TRACK_WIDTH))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]),iu(a[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(b[0]),iu(b[1]))); board.Add(t); return 1
def add_via(board,net,p):
    v=pcbnew.PCB_VIA(board); v.SetNet(net); v.SetPosition(pcbnew.VECTOR2I(iu(p[0]),iu(p[1])))
    v.SetWidth(iu(VIA_SIZE)); v.SetDrill(iu(VIA_DRILL)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); board.Add(v); return 1
def refill(board):
    zs=pcbnew.ZONES()
    for z in board.Zones(): zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs): raise SystemExit('route1x zone refill failed')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--route1w-drc-json',required=True); ap.add_argument('--route1w-pin-net-audit',required=True); args=ap.parse_args()
    rep=loadj(SRC_REPORT); srcsha=sha(SRC_PCB)
    if rep.get('output_sha256')!=srcsha: raise SystemExit('route1w report/PCB SHA mismatch')
    d=loadj(args.route1w_drc_json); a=loadj(args.route1w_pin_net_audit)
    if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=152: raise SystemExit('route1w DRC gate failed')
    if a.get('result')!='PASS' or a.get('audited_present_source_nodes')!=268: raise SystemExit('route1w pin/net gate failed')
    board=pcbnew.LoadBoard(str(SRC_PCB)); fps={f.GetReference():f for f in board.GetFootprints()}
    r103=fps.get('R103'); r104=fps.get('R104'); c113=fps.get('C113')
    if r103 is None or r104 is None or c113 is None: raise SystemExit('route1x missing R103/R104/C113')
    gates={'R103.1':pads(r103,'1')[0].GetNetname(),'R103.2':pads(r103,'2')[0].GetNetname(),'R104.1':pads(r104,'1')[0].GetNetname(),'R104.2':pads(r104,'2')[0].GetNetname(),'C113.1':pads(c113,'1')[0].GetNetname(),'C113.2':pads(c113,'2')[0].GetNetname()}
    expected={'R103.1':'+1V8','R103.2':'SYS_I2C_SDA','R104.1':'+1V8','R104.2':'SYS_I2C_SCL','C113.1':'+1V8','C113.2':'GND'}
    if gates!=expected: raise SystemExit(f'route1x net gate failed: {gates}')
    p103=point(r103,'1'); p104=point(r104,'1'); target=point(c113,'1')
    if abs(p103[0]-12.214871)>0.001 or abs(p103[1]-34.223282)>0.001: raise SystemExit(f'route1x R103.1 geometry gate failed: {p103}')
    if abs(p104[0]-13.154075)>0.001 or abs(p104[1]-34.312249)>0.001: raise SystemExit(f'route1x R104.1 geometry gate failed: {p104}')
    if abs(target[0]-12.245188)>0.001 or abs(target[1]-32.399818)>0.001: raise SystemExit(f'route1x C113.1 geometry gate failed: {target}')
    # BRANCH_VIA is the midpoint of the accepted route-1w R103.1-R104.1 segment.
    if abs(BRANCH_VIA[0]-(p103[0]+p104[0])/2)>0.001 or abs(BRANCH_VIA[1]-(p103[1]+p104[1])/2)>0.001:
        raise SystemExit('route1x branch via is not on accepted pull-up segment')
    # TRUNK_VIA lies exactly on the accepted route-1v U2.12->C113.1 second segment.
    u2=fps.get('U2')
    if u2 is None: raise SystemExit('route1x missing U2')
    u2p=point(u2,'12'); route1v_bend=(11.1875,31.45)
    vx=target[0]-route1v_bend[0]; vy=target[1]-route1v_bend[1]
    tx=(TRUNK_VIA[0]-route1v_bend[0])/vx
    expected_y=route1v_bend[1]+tx*vy
    if not (0.0 < tx < 1.0) or abs(TRUNK_VIA[1]-expected_y)>0.001:
        raise SystemExit('route1x trunk via is not on accepted route-1v +1V8 segment')
    net=board.FindNet('+1V8')
    if net is None: raise SystemExit('route1x +1V8 net reacquire failed')
    vias=add_via(board,net,BRANCH_VIA)+add_via(board,net,TRUNK_VIA)
    added=add_track(board,net,BRANCH_VIA,TRUNK_VIA,pcbnew.In2_Cu)
    if added!=1 or vias!=2: raise SystemExit(f'route1x scope gate failed: segments={added} vias={vias}')
    refill(board); board.SynchronizeNetsAndNetClasses(True); board.BuildConnectivity()
    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),board): raise SystemExit('route1x SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])
if __name__=='__main__': main()
