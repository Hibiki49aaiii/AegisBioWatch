#!/usr/bin/env python3
"""r13 route-1bf: connect R301.1/+1V8 to R503.1/+1V8 with one F.Cu segment."""
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
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1be"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1be-r13.kicad_pcb"
SRC_PRO = SRC_DIR / "AegisBioWatch-MainBoard-Route1be-r13.kicad_pro"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1be.json"
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1bf"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1bf-r13.kicad_pcb"
OUT_PRO = OUT_DIR / "AegisBioWatch-MainBoard-Route1bf-r13.kicad_pro"
REPORT_HELPER = ROOT / "tools/write-pcb-r13-route1bf-report.py"

START = (3.005, 25.975)
END = (3.005, 27.475)
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
    ps = [p for p in fp.Pads() if str(p.GetNumber()) == number]
    if len(ps) != 1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(ps)}")
    return ps[0]


def pos(p) -> tuple[float, float]:
    return (round(mm(p.GetPosition().x), 6), round(mm(p.GetPosition().y), 6))


def add_track(board, net, start, end) -> None:
    t = pcbnew.PCB_TRACK(board)
    t.SetLayer(pcbnew.F_Cu)
    t.SetNet(net)
    t.SetWidth(iu(TRACK_WIDTH))
    t.SetStart(pcbnew.VECTOR2I(iu(start[0]), iu(start[1])))
    t.SetEnd(pcbnew.VECTOR2I(iu(end[0]), iu(end[1])))
    board.Add(t)


def refill(board) -> None:
    zones = pcbnew.ZONES()
    for z in board.Zones():
        zones.append(z)
    if len(zones) and not pcbnew.ZONE_FILLER(board).Fill(zones):
        raise SystemExit("route1bf zone refill failed")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--route1be-drc-json", required=True)
    ap.add_argument("--route1be-pin-net-audit", required=True)
    args = ap.parse_args()

    report = load_json(SRC_REPORT)
    source_sha = sha256(SRC_PCB)
    if report.get("output_sha256") != source_sha:
        raise SystemExit("route1be report/PCB SHA mismatch")

    drc = load_json(Path(args.route1be_drc_json))
    audit = load_json(Path(args.route1be_pin_net_audit))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 118:
        raise SystemExit("route1be DRC gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1be pin/net gate failed")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    r301, r503 = fps.get("R301"), fps.get("R503")
    if r301 is None or r503 is None:
        raise SystemExit("route1bf missing R301/R503")
    if r301.GetValue() != "47k PU" or r503.GetValue() != "47k PU":
        raise SystemExit(f"route1bf value gate failed: R301={r301.GetValue()!r} R503={r503.GetValue()!r}")

    p301_1, p301_2 = pad(r301, "1"), pad(r301, "2")
    p503_1, p503_2 = pad(r503, "1"), pad(r503, "2")

    if (p301_1.GetNetname(), p301_2.GetNetname(), p503_1.GetNetname(), p503_2.GetNetname()) != (
        "+1V8", "FLASH_WP_N", "+1V8", "CHG_PRESENT_N"
    ):
        raise SystemExit("route1bf pad-net gate failed")
    if pos(p301_1) != START or pos(p503_1) != END:
        raise SystemExit(f"route1bf endpoint gate failed: R301.1={pos(p301_1)} R503.1={pos(p503_1)}")
    if pos(p301_2) != (3.645, 25.975) or pos(p503_2) != (3.645, 27.475):
        raise SystemExit(f"route1bf signal-pad coordinate gate failed: R301.2={pos(p301_2)} R503.2={pos(p503_2)}")

    net = board.FindNet("+1V8")
    if net is None:
        raise SystemExit("route1bf +1V8 net reacquire failed")

    add_track(board, net, START, END)
    refill(board)
    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit("route1bf SaveBoard failed")
    if SRC_PRO.exists():
        shutil.copy2(SRC_PRO, OUT_PRO)

    os.execv(sys.executable, [sys.executable, str(REPORT_HELPER)])


if __name__ == "__main__":
    main()
