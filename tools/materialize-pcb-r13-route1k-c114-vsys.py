#!/usr/bin/env python3
"""r13 route-1k: close the C114 VSYS high-frequency decoupling loop.

Source: executed-KiCad-clean route-1j (0 violations / 170 unconnected /
268-node physical audit PASS).

This increment is intentionally limited to C114:
- C114.1/VSYS -> existing route1j VSYS spine on F.Cu
- C114.2/GND -> one short F.Cu stub + through-via into continuous In1.Cu GND

C102 bulk VSYS, VBAT/charger, RF and supplier-gated interfaces remain deferred.
Planning/evidence artifact only; not fabrication authority.
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

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1j'
SRC_PCB = SRC_DIR / 'AegisBioWatch-MainBoard-Route1j-r13.kicad_pcb'
SRC_PRO = SRC_DIR / 'AegisBioWatch-MainBoard-Route1j-r13.kicad_pro'
SRC_REPORT = SRC_DIR / 'routing-seed-r13-1j.json'
OUT_DIR = ROOT / 'hardware/main-board/pcb/route-r13-1k'
OUT_PCB = OUT_DIR / 'AegisBioWatch-MainBoard-Route1k-r13.kicad_pcb'
OUT_PRO = OUT_DIR / 'AegisBioWatch-MainBoard-Route1k-r13.kicad_pro'
REPORT_HELPER = ROOT / 'tools/write-pcb-r13-route1k-report.py'

VSYS_WIDTH = 0.30
GND_WIDTH = 0.30
VIA_SIZE = 0.60
VIA_DRILL = 0.30
VSYS_SPINE_X = 7.35
VSYS_SPINE_JOIN_Y = 28.25
C114_GND_VIA = (7.35, 26.39)


def stage(name: str) -> None:
    print(f'[route1k] {name}', flush=True)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def loadj(path: str | Path):
    return json.loads(Path(path).read_text())


def mm(v) -> float:
    return float(pcbnew.ToMM(v))


def iu(v: float) -> int:
    return int(pcbnew.FromMM(v))


def pads(fp, number: str):
    return [p for p in fp.Pads() if str(p.GetNumber()) == str(number)]


def point(fp, number: str):
    ps = pads(fp, number)
    if not ps:
        raise SystemExit(f'{fp.GetReference()} missing pad {number}')
    return (
        sum(mm(p.GetPosition().x) for p in ps) / len(ps),
        sum(mm(p.GetPosition().y) for p in ps) / len(ps),
    )


def add_track(board, net, a, b, width):
    t = pcbnew.PCB_TRACK(board)
    t.SetLayer(pcbnew.F_Cu)
    t.SetNet(net)
    t.SetWidth(iu(width))
    t.SetStart(pcbnew.VECTOR2I(iu(a[0]), iu(a[1])))
    t.SetEnd(pcbnew.VECTOR2I(iu(b[0]), iu(b[1])))
    board.Add(t)
    return 1


def add_via(board, net, p):
    v = pcbnew.PCB_VIA(board)
    v.SetNet(net)
    v.SetPosition(pcbnew.VECTOR2I(iu(p[0]), iu(p[1])))
    v.SetWidth(iu(VIA_SIZE))
    v.SetDrill(iu(VIA_DRILL))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    board.Add(v)
    return 1


def refill_all_zones(board):
    zs = pcbnew.ZONES()
    for z in board.Zones():
        zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs):
        raise SystemExit('route1k zone refill failed')


def has_segment(board, netname: str, a: tuple[float,float], b: tuple[float,float], tol: float=0.01) -> bool:
    def near(p, q):
        return abs(p[0]-q[0]) <= tol and abs(p[1]-q[1]) <= tol
    for item in board.GetTracks():
        if isinstance(item, pcbnew.PCB_VIA) or item.GetNetname() != netname or item.GetLayer() != pcbnew.F_Cu:
            continue
        s=(mm(item.GetStart().x), mm(item.GetStart().y)); e=(mm(item.GetEnd().x), mm(item.GetEnd().y))
        if (near(s,a) and near(e,b)) or (near(s,b) and near(e,a)):
            return True
    return False


def main():
    stage('start')
    ap=argparse.ArgumentParser()
    ap.add_argument('--route1j-drc-json', required=True)
    ap.add_argument('--route1j-pin-net-audit', required=True)
    args=ap.parse_args()

    rep=loadj(SRC_REPORT)
    srcsha=sha(SRC_PCB)
    if rep.get('output_sha256') != srcsha:
        raise SystemExit('route1j report/PCB SHA mismatch')
    d=loadj(args.route1j_drc_json); a=loadj(args.route1j_pin_net_audit)
    if len(d.get('violations',[])) != 0 or len(d.get('unconnected_items',[])) != 170:
        raise SystemExit('route1j DRC gate failed')
    if a.get('result') != 'PASS' or a.get('audited_present_source_nodes') != 268:
        raise SystemExit('route1j pin/net gate failed')
    stage('source gates passed')

    b=pcbnew.LoadBoard(str(SRC_PCB))
    fps={f.GetReference():f for f in b.GetFootprints()}
    if 'C114' not in fps:
        raise SystemExit('route1k missing C114')
    c114=fps['C114']
    gates={'C114.1':pads(c114,'1')[0].GetNetname(), 'C114.2':pads(c114,'2')[0].GetNetname()}
    if gates != {'C114.1':'VSYS','C114.2':'GND'}:
        raise SystemExit(f'route1k C114 net gate failed: {gates}')

    p1=point(c114,'1'); p2=point(c114,'2')
    expected_p1=(6.892232,27.030566); expected_p2=(6.892232,26.390566)
    for actual, expected, name in ((p1,expected_p1,'C114.1'),(p2,expected_p2,'C114.2')):
        if abs(actual[0]-expected[0])>0.001 or abs(actual[1]-expected[1])>0.001:
            raise SystemExit(f'route1k {name} geometry gate failed: {actual}')

    # Fail closed unless the accepted VSYS spine is still exactly present.
    if not has_segment(b,'VSYS',(VSYS_SPINE_X,VSYS_SPINE_JOIN_Y),(VSYS_SPINE_X,29.815584)):
        raise SystemExit('route1k accepted VSYS spine gate failed')

    vsys=b.FindNet('VSYS'); gnd=b.FindNet('GND')
    if vsys is None or gnd is None:
        raise SystemExit('route1k net reacquire failed')

    added=0; vias=0
    # Join C114.1 horizontally to x=7.35, then vertically into the accepted spine.
    join=(VSYS_SPINE_X,p1[1])
    added += add_track(b,vsys,p1,join,VSYS_WIDTH)
    added += add_track(b,vsys,join,(VSYS_SPINE_X,VSYS_SPINE_JOIN_Y),VSYS_WIDTH)
    # C114.2 gets a short GND stub and a deliberate plane via.
    added += add_track(b,gnd,p2,C114_GND_VIA,GND_WIDTH)
    vias += add_via(b,gnd,C114_GND_VIA)
    if added != 3 or vias != 1:
        raise SystemExit('route1k internal scope gate failed')

    refill_all_zones(b)
    b.SynchronizeNetsAndNetClasses(True)
    b.BuildConnectivity()

    if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB),b):
        raise SystemExit('route1k SaveBoard failed')
    if SRC_PRO.exists(): shutil.copy2(SRC_PRO,OUT_PRO)
    stage('board saved')

    if not REPORT_HELPER.is_file():
        raise SystemExit('route1k report helper missing')
    os.execv(sys.executable,[sys.executable,str(REPORT_HELPER)])


if __name__ == '__main__':
    main()
