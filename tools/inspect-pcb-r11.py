#!/usr/bin/env python3
"""Inspect critical r11 PCB footprint and pad geometry without replacing KiCad DRC.

This tool is diagnostic only. KiCad's own DRC remains the validation authority.
It reports both critical PMIC and nRF54L15 reference-placement source geometry.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / "hardware/main-board/pcb/placement-r11/AegisBioWatch-MainBoard-PlacementSeed-r11.kicad_pcb"

PMIC_TARGETS = [
    "U2", "L101", "L102",
    "C101", "C102", "C103", "C104", "C105", "C106", "C107", "C108", "C109", "C110", "C111", "C112", "C113", "C114",
    "NT101", "NT102", "R101", "R102", "R103", "R104", "R105", "R106",
]
NRF_TARGETS = [
    "U1", "Y1", "Y2", "L1", "L2", "L3", "L4", "FB1", "R1",
    "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13",
]
TARGETS = PMIC_TARGETS + NRF_TARGETS

U1_CRITICAL_NETS = {
    "1": "NRF_XL1",
    "2": "NRF_XL2",
    "10": "+1V8",
    "22": "+1V8",
    "25": "SWDIO",
    "26": "SWDCLK",
    "30": "NRF_RESET_RAW",
    "31": "RF_MCU",
    "32": "GND",
    "33": "NRF_DECA_RF",
    "34": "NRF_XC1",
    "35": "NRF_XC2",
    "36": "+1V8",
    "43": "NRF_DECA_RF",
    "44": "GND",
    "45": "NRF_DECD",
    "46": "NRF_DCC",
    "47": "+1V8",
    "48": "+1V8",
    "49": "GND",
}


def balanced_blocks(text: str, token: str):
    start = 0
    needle = f"({token}"
    while True:
        i = text.find(needle, start)
        if i < 0:
            return
        depth = 0
        in_string = False
        escaped = False
        for j in range(i, len(text)):
            ch = text[j]
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    yield text[i:j + 1]
                    start = j + 1
                    break
        else:
            raise RuntimeError(f"unterminated {token} block at offset {i}")


def parse_at(block: str):
    m = re.search(r"\n\s*\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)(?:\s+(-?[0-9.]+))?\)", block)
    if not m:
        return None
    return float(m.group(1)), float(m.group(2)), float(m.group(3) or 0.0)


def reference(block: str):
    for pat in [
        r'\(property\s+"Reference"\s+"([^"]+)"',
        r'\(fp_text\s+reference\s+"?([^"\s\)]+)"?',
    ]:
        m = re.search(pat, block)
        if m:
            return m.group(1)
    return None


def pad_info(block: str, footprint_at):
    fx, fy, fa = footprint_at
    out = []
    for pad in balanced_blocks(block, "pad"):
        pm = re.match(r'\(pad\s+"?([^"\s]+)"?', pad)
        if not pm:
            continue
        num = pm.group(1)
        am = re.search(r"\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)(?:\s+(-?[0-9.]+))?\)", pad)
        dx = float(am.group(1)) if am else 0.0
        dy = float(am.group(2)) if am else 0.0
        pa = float(am.group(3) or 0.0) if am else 0.0
        rad = math.radians(fa)
        ax = fx + dx * math.cos(rad) - dy * math.sin(rad)
        ay = fy + dx * math.sin(rad) + dy * math.cos(rad)
        nm = re.search(r'\(net\s+([0-9]+)\s+"([^"]*)"\)', pad)
        out.append({
            "pad": num,
            "at_local_mm": [round(dx, 4), round(dy, 4), round(pa, 3)],
            "at_abs_mm": [round(ax, 4), round(ay, 4)],
            "net_id": int(nm.group(1)) if nm else None,
            "net": nm.group(2) if nm else None,
        })
    return out


def main():
    if not PCB.exists():
        raise SystemExit(f"materialized r11 PCB not found: {PCB}")
    text = PCB.read_text(encoding="utf-8")
    found = {}
    for block in balanced_blocks(text, "footprint"):
        ref = reference(block)
        if ref not in TARGETS:
            continue
        at = parse_at(block)
        if at is None:
            raise SystemExit(f"missing footprint at for {ref}")
        found[ref] = {
            "at_mm": [round(at[0], 4), round(at[1], 4), round(at[2], 3)],
            "pads": pad_info(block, at),
        }

    missing = [r for r in TARGETS if r not in found]
    if missing:
        raise SystemExit(f"critical footprints not found: {missing}")

    u1_nets = {p["pad"]: p["net"] for p in found["U1"]["pads"]}
    mismatches = []
    for pin, expected in U1_CRITICAL_NETS.items():
        actual = u1_nets.get(pin)
        if actual != expected:
            mismatches.append({"pin": pin, "expected": expected, "actual": actual})
    if mismatches:
        raise SystemExit(f"U1 critical pad/net mismatch: {mismatches}")

    report = {
        "pcb": str(PCB.relative_to(ROOT)),
        "groups": {
            "npm1300": PMIC_TARGETS,
            "nrf54l15_qfaa": NRF_TARGETS,
        },
        "u1_critical_pin_net_audit": {
            "checked": len(U1_CRITICAL_NETS),
            "mismatches": 0,
        },
        "footprints": found,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
