#!/usr/bin/env python3
"""Materialize route-1bk: C305.1/VSYS_HAPTIC -> C304.1/VSYS_HAPTIC."""
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
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bj"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1bj-r13.kicad_pcb"
SRC_PRO = SRC_DIR / "AegisBioWatch-MainBoard-Route1bj-r13.kicad_pro"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1bj.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bk"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bk-r13.kicad_pcb"
OUT_PRO = OUT_DIR / "AegisBioWatch-MainBoard-Route1bk-r13.kicad_pro"
REPORT_HELPER = ROOT / "tools/write-pcb-r13-route1bk-report.py"

POINTS = [(6.805, 22.335), (6.805, 21.65), (16.005, 21.65), (16.005, 23.725)]
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
    ap.add_argument("--route1bj-drc-json", required=True)
    ap.add_argument("--route1bj-pin-net-audit", required=True)
    ap.add_argument("--exact-probe-json", required=True)
    args = ap.parse_args()

    source_report = load_json(SRC_REPORT)
    source_sha = sha256(SRC_PCB)
    if source_report.get("output_sha256") != source_sha:
        raise SystemExit("route1bk source report/PCB SHA mismatch")

    drc = load_json(Path(args.route1bj_drc_json))
    audit = load_json(Path(args.route1bj_pin_net_audit))
    probe = load_json(Path(args.exact_probe_json))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 114:
        raise SystemExit("route1bk source DRC gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bk source audit gate failed")
    if probe.get("source_route1bj_sha256") != source_sha or probe.get("board_modified") is not False:
        raise SystemExit("route1bk exact-probe provenance gate failed")
    if probe.get("path", {}).get("points_mm") != [list(p) for p in POINTS]:
        raise SystemExit("route1bk exact-probe path gate failed")
    if float(probe.get("path", {}).get("minimum_conservative_clearance_mm", -1)) < 0.125 - 1e-6:
        raise SystemExit("route1bk exact-probe clearance gate failed")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    c305, c304, u4, r305 = fps.get("C305"), fps.get("C304"), fps.get("U4"), fps.get("R305")
    if None in (c305, c304, u4, r305):
        raise SystemExit("route1bk missing C305/C304/U4/R305")
    if c305.GetValue() != "1uF" or c304.GetValue() != "100nF":
        raise SystemExit("route1bk capacitor identity gate failed")
    if u4.GetValue() != "DRV2605LDGSR" or r305.GetValue() != "0R / FB OPTION":
        raise SystemExit("route1bk haptic supply identity gate failed")

    c305p1, c305p2 = get_pad(c305, "1"), get_pad(c305, "2")
    c304p1, c304p2 = get_pad(c304, "1"), get_pad(c304, "2")
    u4p10 = get_pad(u4, "10")
    r305p2 = get_pad(r305, "2")
    if (
        (c305p1.GetNetname(), pos(c305p1)) != ("VSYS_HAPTIC", POINTS[0])
        or (c305p2.GetNetname(), pos(c305p2)) != ("GND", (7.765, 22.335))
        or (c304p1.GetNetname(), pos(c304p1)) != ("VSYS_HAPTIC", POINTS[-1])
        or (c304p2.GetNetname(), pos(c304p2)) != ("GND", (16.645, 23.725))
        or (u4p10.GetNetname(), pos(u4p10)) != ("VSYS_HAPTIC", (23.005, 13.4))
        or (r305p2.GetNetname(), pos(r305p2)) != ("VSYS_HAPTIC", (31.315, 18.595))
    ):
        raise SystemExit("route1bk component pad/net/coordinate gate failed")

    net = board.FindNet("VSYS_HAPTIC")
    if net is None:
        raise SystemExit("route1bk VSYS_HAPTIC net reacquire failed")

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
        raise SystemExit("route1bk zone refill failed")
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit("route1bk SaveBoard failed")
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)

    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == "__main__":
    main()
