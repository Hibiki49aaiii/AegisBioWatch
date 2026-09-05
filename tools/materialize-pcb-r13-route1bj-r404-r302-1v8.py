#!/usr/bin/env python3
"""Materialize route-1bj: R404.1/+1V8 -> R302.1/+1V8 using three F.Cu segments."""
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
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bi"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bi-r13.kicad_pcb"
SRC_PRO = SRC_DIR / "AegisBioWatch-MainBoard-Route1bi-r13.kicad_pro"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bi.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bj"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bj-r13.kicad_pcb"
OUT_PRO = OUT_DIR / "AegisBioWatch-MainBoard-Route1bj-r13.kicad_pro"
REPORT_HELPER = ROOT / "tools/write-pcb-r13-route1bj-report.py"

POINTS = [(15.755, 26.725), (15.755, 26.2), (20.255, 26.2), (20.255, 25.975)]
TRACK_WIDTH = 0.30


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mm(v: int) -> float:
    return float(pcbnew.ToMM(v))


def iu(v: float) -> int:
    return int(pcbnew.FromMM(v))


def get_pad(fp, number: str):
    pads = [p for p in fp.Pads() if str(p.GetNumber()) == str(number)]
    if len(pads) != 1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(pads)}")
    return pads[0]


def pos(pad) -> tuple[float, float]:
    p = pad.GetPosition()
    return (round(mm(p.x), 6), round(mm(p.y), 6))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--route1bi-drc-json", required=True)
    ap.add_argument("--route1bi-pin-net-audit", required=True)
    ap.add_argument("--exact-probe-json", required=True)
    args = ap.parse_args()

    source_report = load_json(SRC_REPORT)
    source_sha = sha256(SRC_PCB)
    if source_report.get("output_sha256") != source_sha:
        raise SystemExit("route1bj source report/PCB SHA mismatch")

    drc = load_json(Path(args.route1bi_drc_json))
    audit = load_json(Path(args.route1bi_pin_net_audit))
    probe = load_json(Path(args.exact_probe_json))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 115:
        raise SystemExit("route1bj source DRC gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bj source audit gate failed")
    if probe.get("source_route1bi_sha256") != source_sha or probe.get("board_modified") is not False:
        raise SystemExit("route1bj exact-probe provenance gate failed")
    if probe.get("path", {}).get("points_mm") != [list(p) for p in POINTS]:
        raise SystemExit("route1bj exact-probe path gate failed")
    if float(probe.get("path", {}).get("minimum_conservative_clearance_mm", -1)) < 0.175 - 1e-6:
        raise SystemExit("route1bj exact-probe clearance gate failed")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    r404, r302, r501 = fps.get("R404"), fps.get("R302"), fps.get("R501")
    if r404 is None or r302 is None or r501 is None:
        raise SystemExit("route1bj missing R404/R302/R501")
    if r404.GetValue() != "4.7k PU PROV" or r302.GetValue() != "47k PU" or r501.GetValue() != "100k":
        raise SystemExit("route1bj component identity gate failed")

    r404p1, r404p2 = get_pad(r404, "1"), get_pad(r404, "2")
    r302p1, r302p2 = get_pad(r302, "1"), get_pad(r302, "2")
    r501p1 = get_pad(r501, "1")
    if (
        (r404p1.GetNetname(), pos(r404p1)) != ("+1V8", POINTS[0])
        or (r404p2.GetNetname(), pos(r404p2)) != ("SYS_I2C_SCL", (16.395, 26.725))
        or (r302p1.GetNetname(), pos(r302p1)) != ("+1V8", POINTS[-1])
        or (r302p2.GetNetname(), pos(r302p2)) != ("FLASH_HOLD_N", (20.895, 25.975))
        or (r501p1.GetNetname(), pos(r501p1)) != ("CHG_5V", (18.005, 26.725))
    ):
        raise SystemExit("route1bj component pad/net/coordinate gate failed")

    net = board.FindNet("+1V8")
    if net is None:
        raise SystemExit("route1bj +1V8 net reacquire failed")

    for a, b in zip(POINTS, POINTS[1:]):
        track = pcbnew.PCB_TRACK(board)
        track.SetLayer(pcbnew.F_Cu)
        track.SetNet(net)
        track.SetWidth(iu(TRACK_WIDTH))
        track.SetStart(pcbnew.VECTOR2I(iu(a[0]), iu(a[1])))
        track.SetEnd(pcbnew.VECTOR2I(iu(b[0]), iu(b[1])))
        board.Add(track)

    zones = pcbnew.ZONES()
    for z in board.Zones():
        zones.append(z)
    if len(zones) and not pcbnew.ZONE_FILLER(board).Fill(zones):
        raise SystemExit("route1bj zone refill failed")
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit("route1bj SaveBoard failed")
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)

    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == "__main__":
    main()
