#!/usr/bin/env python3
"""r13 route-1bh: connect C301.1/+1V8 to R404.1/+1V8."""
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
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bh"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bh-r13.kicad_pcb"
OUT_PRO = OUT_DIR / "AegisBioWatch-MainBoard-Route1bh-r13.kicad_pro"
REPORT_HELPER = ROOT / "tools/write-pcb-r13-route1bh-report.py"

START = (13.755, 23.725)
END = (15.755, 26.725)
TRACK_WIDTH = 0.30


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mm(value: int) -> float:
    return float(pcbnew.ToMM(value))


def iu(value: float) -> int:
    return int(pcbnew.FromMM(value))


def pad(fp, number: str):
    ps = [p for p in fp.Pads() if str(p.GetNumber()) == str(number)]
    if len(ps) != 1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(ps)}")
    return ps[0]


def pos(p) -> tuple[float, float]:
    return (round(mm(p.GetPosition().x), 6), round(mm(p.GetPosition().y), 6))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--route1bg-drc-json", required=True)
    ap.add_argument("--route1bg-pin-net-audit", required=True)
    args = ap.parse_args()

    report = load_json(SRC_REPORT)
    source_sha = sha256(SRC_PCB)
    if report.get("output_sha256") != source_sha:
        raise SystemExit("route1bg report/PCB SHA mismatch")

    drc = load_json(Path(args.route1bg_drc_json))
    audit = load_json(Path(args.route1bg_pin_net_audit))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 116:
        raise SystemExit("route1bg DRC gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bg pin/net gate failed")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    c301, r404 = fps.get("C301"), fps.get("R404")
    if c301 is None or r404 is None:
        raise SystemExit("route1bh missing C301/R404")
    if c301.GetValue() != "100nF" or r404.GetValue() != "4.7k PU PROV":
        raise SystemExit(f"route1bh value gate failed C301={c301.GetValue()!r} R404={r404.GetValue()!r}")

    c1, c2, r1, r2 = pad(c301, "1"), pad(c301, "2"), pad(r404, "1"), pad(r404, "2")
    if (c1.GetNetname(), c2.GetNetname(), r1.GetNetname(), r2.GetNetname()) != (
        "+1V8", "GND", "+1V8", "SYS_I2C_SCL"
    ):
        raise SystemExit("route1bh pad-net gate failed")
    if pos(c1) != START or pos(c2) != (14.395, 23.725) or pos(r1) != END or pos(r2) != (16.395, 26.725):
        raise SystemExit(
            f"route1bh coordinate gate failed C301.1={pos(c1)} C301.2={pos(c2)} "
            f"R404.1={pos(r1)} R404.2={pos(r2)}"
        )

    net = board.FindNet("+1V8")
    if net is None:
        raise SystemExit("route1bh +1V8 net reacquire failed")

    t = pcbnew.PCB_TRACK(board)
    t.SetLayer(pcbnew.F_Cu)
    t.SetNet(net)
    t.SetWidth(iu(TRACK_WIDTH))
    t.SetStart(pcbnew.VECTOR2I(iu(START[0]), iu(START[1])))
    t.SetEnd(pcbnew.VECTOR2I(iu(END[0]), iu(END[1])))
    board.Add(t)

    zones = pcbnew.ZONES()
    for z in board.Zones():
        zones.append(z)
    if len(zones) and not pcbnew.ZONE_FILLER(board).Fill(zones):
        raise SystemExit("route1bh zone refill failed")
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit("route1bh SaveBoard failed")
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)

    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == "__main__":
    main()
