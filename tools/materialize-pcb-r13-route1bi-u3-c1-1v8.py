#!/usr/bin/env python3
"""Materialize route-1bi: U3.8/+1V8 -> C1.1/+1V8 using two F.Cu segments."""
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
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bg"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bg-r13.kicad_pcb"
SRC_PRO = SRC_DIR / "AegisBioWatch-MainBoard-Route1bg-r13.kicad_pro"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bg.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bi"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bi-r13.kicad_pcb"
OUT_PRO = OUT_DIR / "AegisBioWatch-MainBoard-Route1bi-r13.kicad_pro"
REPORT_HELPER = ROOT / "tools/write-pcb-r13-route1bi-report.py"

POINTS = [(11.08, 4.72), (10.305, 4.72), (10.305, 11.085)]
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
    ap.add_argument("--route1bg-drc-json", required=True)
    ap.add_argument("--route1bg-pin-net-audit", required=True)
    ap.add_argument("--exact-probe-json", required=True)
    args = ap.parse_args()

    source_report = load_json(SRC_REPORT)
    source_sha = sha256(SRC_PCB)
    if source_report.get("output_sha256") != source_sha:
        raise SystemExit("route1bi source report/PCB SHA mismatch")

    drc = load_json(Path(args.route1bg_drc_json))
    audit = load_json(Path(args.route1bg_pin_net_audit))
    probe = load_json(Path(args.exact_probe_json))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 116:
        raise SystemExit("route1bi source DRC gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bi source audit gate failed")
    if probe.get("source_route1bg_sha256") != source_sha or probe.get("board_modified") is not False:
        raise SystemExit("route1bi exact-probe provenance gate failed")
    if probe.get("path", {}).get("points_mm") != [list(p) for p in POINTS]:
        raise SystemExit("route1bi exact-probe path gate failed")
    if float(probe.get("path", {}).get("minimum_conservative_clearance_mm", -1)) < 0.100:
        raise SystemExit("route1bi exact-probe clearance gate failed")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    u3, c1 = fps.get("U3"), fps.get("C1")
    if u3 is None or c1 is None:
        raise SystemExit("route1bi missing U3/C1")
    if u3.GetValue() != "W25Q256JWPIQ 256Mbit" or c1.GetValue() != "10uF":
        raise SystemExit("route1bi component identity gate failed")

    u8, u7, u5 = get_pad(u3, "8"), get_pad(u3, "7"), get_pad(u3, "5")
    c1p1, c1p2 = get_pad(c1, "1"), get_pad(c1, "2")
    if (
        (u8.GetNetname(), pos(u8)) != ("+1V8", POINTS[0])
        or (u7.GetNetname(), pos(u7)) != ("FLASH_HOLD_N", (11.08, 5.99))
        or (u5.GetNetname(), pos(u5)) != ("AUX_SPI_MOSI", (11.08, 8.53))
        or (c1p1.GetNetname(), pos(c1p1)) != ("+1V8", POINTS[-1])
        or (c1p2.GetNetname(), pos(c1p2)) != ("GND", (11.265, 11.085))
    ):
        raise SystemExit("route1bi component pad/net/coordinate gate failed")

    net = board.FindNet("+1V8")
    if net is None:
        raise SystemExit("route1bi +1V8 net reacquire failed")

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
        raise SystemExit("route1bi zone refill failed")
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit("route1bi SaveBoard failed")
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)

    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == "__main__":
    main()
