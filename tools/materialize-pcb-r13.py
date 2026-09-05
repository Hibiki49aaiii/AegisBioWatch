#!/usr/bin/env python3
"""Materialize AegisBioWatch Main Board r13 from the hash-verified r11 seed.

r13 compacts the nPM1300-QEAA/QFN32 support network around U2 using the actual
U2 pad geometry plus Nordic current-loop/component-adjacency rules. Third-party
absolute coordinates are never imported. KiCad PCB DRC remains mandatory.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import runpy
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R11_SCRIPT = ROOT / "tools/materialize-pcb-r11.py"
R11_DIR = ROOT / "hardware/main-board/pcb/placement-r11"
R11_PCB = R11_DIR / "AegisBioWatch-MainBoard-PlacementSeed-r11.kicad_pcb"
R11_PRO = R11_DIR / "AegisBioWatch-MainBoard-PlacementSeed-r11.kicad_pro"
R13_DIR = ROOT / "hardware/main-board/pcb/placement-r13"
R13_PCB = R13_DIR / "AegisBioWatch-MainBoard-Placement-r13.kicad_pcb"
R13_PRO = R13_DIR / "AegisBioWatch-MainBoard-Placement-r13.kicad_pro"
R13_REPORT = R13_DIR / "placement-implementation-r13.json"

EXPECTED_R11_PCB_SHA256 = "f31211be596c4435faa7bdf116bc16239b70e668b6e9377ef26f0909ebce19e2"

U2_CRITICAL_NETS = {
    "1": "+1V8", "2": "PVSS1_LOCAL", "3": "PMIC_SW1", "4": "VSYS",
    "5": "PMIC_SW2", "6": "PVSS2_LOCAL", "12": "+1V8",
    "16": "PMIC_VSET2", "17": "PMIC_VSET1", "19": "VBAT",
    "20": "VSYS", "21": "CHG_5V", "22": "VBUSOUT_SENSE",
    "28": "LDO1_IN", "29": "DISP_SW", "30": "LDO2_IN",
    "31": "BIO_SW", "32": "+3V0",
}

PMIC_REFS = {
    "U2", "L101", "L102",
    *{f"C{i}" for i in range(101, 115)},
    "NT101", "NT102",
    *{f"R{i}" for i in range(101, 107)},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def balanced_blocks(text: str, token: str):
    needle = f"({token}"
    start = 0
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
                    yield i, j + 1, text[i:j + 1]
                    start = j + 1
                    break
        else:
            raise RuntimeError(f"unterminated {token} block at offset {i}")


def reference(block: str) -> str | None:
    for pat in (
        r'\(property\s+"Reference"\s+"([^"]+)"',
        r'\(fp_text\s+reference\s+"?([^"\s\)]+)"?',
    ):
        m = re.search(pat, block)
        if m:
            return m.group(1)
    return None


def footprint_at(block: str) -> tuple[float, float, float]:
    m = re.search(r"\n\s*\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)(?:\s+(-?[0-9.]+))?\)", block)
    if not m:
        raise ValueError("footprint has no top-level at")
    return float(m.group(1)), float(m.group(2)), float(m.group(3) or 0.0)


def replace_footprint_at(block: str, x: float, y: float, angle_deg: float) -> str:
    angle_deg = ((angle_deg + 180.0) % 360.0) - 180.0
    pat = re.compile(r"(\n\s*)\(at\s+-?[0-9.]+\s+-?[0-9.]+(?:\s+-?[0-9.]+)?\)")
    out, n = pat.subn(lambda m: f"{m.group(1)}(at {x:.4f} {y:.4f} {angle_deg:.3f})", block, count=1)
    if n != 1:
        raise ValueError("unable to replace footprint at")
    return out


def rotate(v: tuple[float, float], deg: float) -> tuple[float, float]:
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return v[0] * c - v[1] * s, v[0] * s + v[1] * c


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def mul(a, k):
    return a[0] * k, a[1] * k


def mean(points):
    return sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points)


def norm(v):
    d = math.hypot(v[0], v[1])
    if d < 1e-9:
        raise ValueError("zero-length vector")
    return v[0] / d, v[1] / d


def angle(v):
    return math.degrees(math.atan2(v[1], v[0]))


def pad_records(block: str):
    result = []
    for _, _, pad in balanced_blocks(block, "pad"):
        pm = re.match(r'\(pad\s+"?([^"\s]+)"?', pad)
        if not pm:
            continue
        am = re.search(r"\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)(?:\s+(-?[0-9.]+))?\)", pad)
        if not am:
            continue
        nm = re.search(r'\(net\s+([0-9]+)\s+"([^"]*)"\)', pad)
        result.append({
            "num": pm.group(1),
            "local": (float(am.group(1)), float(am.group(2))),
            "pad_angle": float(am.group(3) or 0.0),
            "net_id": int(nm.group(1)) if nm else None,
            "net": nm.group(2) if nm else None,
        })
    return result


def abs_pad_map(block: str):
    x, y, a = footprint_at(block)
    return {p["num"]: add((x, y), rotate(p["local"], a)) for p in pad_records(block)}


def pad_by_net(block: str, net: str):
    pads = [p for p in pad_records(block) if p["net"] == net]
    if len(pads) != 1:
        raise ValueError(f"expected one pad on net {net!r}, found {len(pads)}")
    return pads[0]


def place_2t(block: str, net_a: str, net_b: str, midpoint, axis_a_to_b):
    pa = pad_by_net(block, net_a)
    pb = pad_by_net(block, net_b)
    local_axis = sub(pb["local"], pa["local"])
    rot = angle(norm(axis_a_to_b)) - angle(local_axis)
    local_mid = mul(add(pa["local"], pb["local"]), 0.5)
    center = sub(midpoint, rotate(local_mid, rot))
    return replace_footprint_at(block, center[0], center[1], rot)


def place_2t_anchor(block: str, net_a: str, net_b: str, anchor_a, axis_a_to_b):
    """Place a 2-terminal part with its net_a pad exactly on anchor_a."""
    pa = pad_by_net(block, net_a)
    pb = pad_by_net(block, net_b)
    local_axis = sub(pb["local"], pa["local"])
    rot = angle(norm(axis_a_to_b)) - angle(local_axis)
    center = sub(anchor_a, rotate(pa["local"], rot))
    return replace_footprint_at(block, center[0], center[1], rot)


def passive_abs_pad(block: str, net: str):
    x, y, a = footprint_at(block)
    p = pad_by_net(block, net)
    return add((x, y), rotate(p["local"], a))


def build_index(text: str):
    idx = {}
    for start, end, block in balanced_blocks(text, "footprint"):
        ref = reference(block)
        if ref:
            idx[ref] = {"start": start, "end": end, "block": block}
    return idx


def replace_blocks(text: str, replacements: dict[str, str]) -> str:
    idx = build_index(text)
    spans = []
    for ref, new_block in replacements.items():
        if ref not in idx:
            raise ValueError(f"missing footprint {ref}")
        spans.append((idx[ref]["start"], idx[ref]["end"], new_block))
    for start, end, new_block in sorted(spans, reverse=True):
        text = text[:start] + new_block + text[end:]
    return text


def main():
    if not R11_SCRIPT.exists():
        raise SystemExit(f"missing r11 materializer: {R11_SCRIPT}")
    runpy.run_path(str(R11_SCRIPT), run_name="__main__")
    if sha256(R11_PCB) != EXPECTED_R11_PCB_SHA256:
        raise SystemExit("r11 PCB SHA-256 mismatch; refusing to transform unknown source")

    text = R11_PCB.read_text(encoding="utf-8")
    idx = build_index(text)
    missing = sorted(PMIC_REFS - set(idx))
    if missing:
        raise SystemExit(f"r13 critical footprint set incomplete: {missing}")

    u2 = idx["U2"]["block"]
    ux, uy, ua = footprint_at(u2)
    uc = (ux, uy)
    up = abs_pad_map(u2)
    u2_pad_nets = {p["num"]: p["net"] for p in pad_records(u2)}
    for pin, expected_net in U2_CRITICAL_NETS.items():
        actual = u2_pad_nets.get(pin)
        if actual != expected_net:
            raise SystemExit(f"U2 pin {pin}: expected {expected_net!r}, got {actual!r}")

    # Derive the physical BUCK-side frame from the complete QFN side (pins 1..8),
    # not from a subset of function pins. This keeps the normal insensitive to the
    # asymmetric positions of PVSS/SW/PVDD within that side.
    buck_side_point = mean([up[str(i)] for i in range(1, 9)])
    n = norm(sub(buck_side_point, uc))
    t = norm(sub(up["8"], up["1"]))
    if abs(n[0] * t[0] + n[1] * t[1]) > 0.05:
        raise SystemExit("unexpected U2 QFN geometry: BUCK-side frame is not orthogonal")

    repl = {"U2": u2}

    # Input capacitors bridge the PVDD neighborhood toward the corresponding
    # PVSS side while leaving the SW lanes free to escape diagonally. Their
    # exact board-level clearances are subsequently checked by KiCad DRC.
    cap_ring = 0.95
    c103_vs = add(add(up["4"], mul(n, cap_ring)), mul(t, -0.12))
    c104_vs = add(add(up["4"], mul(n, cap_ring)), mul(t, 0.12))
    c103_ret_target = add(up["2"], mul(n, cap_ring))
    c104_ret_target = add(up["6"], mul(n, cap_ring))
    repl["C103"] = place_2t_anchor(
        idx["C103"]["block"], "VSYS", "PVSS1_LOCAL", c103_vs, sub(c103_ret_target, c103_vs))
    repl["C104"] = place_2t_anchor(
        idx["C104"]["block"], "VSYS", "PVSS2_LOCAL", c104_vs, sub(c104_ret_target, c104_vs))

    # 0201 high-frequency PVDD application decoupler remains centered between
    # the two larger input capacitors with a very short VSYS escape.
    repl["C114"] = place_2t_anchor(
        idx["C114"]["block"], "VSYS", "GND", add(up["4"], mul(n, 0.48)), n)

    # SW inductors use pad anchoring: the SW pad itself is placed in a diagonal
    # escape lane from pin 3/5, instead of only positioning the component center.
    sw1_axis = norm(add(mul(n, 1.00), mul(t, -0.72)))
    sw2_axis = norm(add(mul(n, 1.00), mul(t, 0.72)))
    sw1_anchor = add(up["3"], mul(sw1_axis, 1.40))
    sw2_anchor = add(up["5"], mul(sw2_axis, 1.40))
    repl["L101"] = place_2t_anchor(
        idx["L101"]["block"], "PMIC_SW1", "+1V8", sw1_anchor, sw1_axis)
    repl["L102"] = place_2t_anchor(
        idx["L102"]["block"], "PMIC_SW2", "+3V0", sw2_anchor, sw2_axis)

    # Output capacitors start just beyond the inductor output pads and orient
    # their local-return pads back toward the centerline between both BUCKs.
    l101_out = passive_abs_pad(repl["L101"], "+1V8")
    l102_out = passive_abs_pad(repl["L102"], "+3V0")
    c107_out_anchor = add(l101_out, mul(n, 0.78))
    c108_out_anchor = add(l102_out, mul(n, 0.78))
    repl["C107"] = place_2t_anchor(
        idx["C107"]["block"], "+1V8", "PVSS1_LOCAL", c107_out_anchor, t)
    repl["C108"] = place_2t_anchor(
        idx["C108"]["block"], "+3V0", "PVSS2_LOCAL", c108_out_anchor, mul(t, -1.0))

    # Explicit local switching-return transition to continuous board GND.
    c107_ret = passive_abs_pad(repl["C107"], "PVSS1_LOCAL")
    c108_ret = passive_abs_pad(repl["C108"], "PVSS2_LOCAL")
    repl["NT101"] = place_2t_anchor(
        idx["NT101"]["block"], "PVSS1_LOCAL", "GND", add(c107_ret, mul(t, 0.32)), mul(n, -1.0))
    repl["NT102"] = place_2t_anchor(
        idx["NT102"]["block"], "PVSS2_LOCAL", "GND", add(c108_ret, mul(t, -0.32)), mul(n, -1.0))

    def pin_out(pin: str):
        return norm(sub(up[pin], uc))

    def pin_tangent(pin: str):
        o = pin_out(pin)
        return (-o[1], o[0])

    # Remaining PMIC-local passives are placed from the relevant package pins.
    # Distances are deliberately conservative until executed KiCad courtyard
    # evidence is available; electrical topology is unchanged.
    simple = {
        "C101": ("21", "CHG_5V", "GND", 1.28, -0.70),
        "C102": ("20", "VSYS", "GND", 1.28, 0.70),
        "C105": ("22", "VBUSOUT_SENSE", "GND", 1.28, 0.70),
        "C106": ("19", "VBAT", "GND", 1.28, -0.70),
        "C113": ("12", "+1V8", "GND", 0.92, 0.00),
        "R101": ("17", "PMIC_VSET1", "GND", 0.95, 0.48),
        "R102": ("16", "PMIC_VSET2", "GND", 0.95, -0.48),
    }
    for ref, (pin, net_a, net_b, dist, tang_off) in simple.items():
        o = pin_out(pin)
        q = pin_tangent(pin)
        midpoint = add(add(up[pin], mul(o, dist)), mul(q, tang_off))
        repl[ref] = place_2t(idx[ref]["block"], net_a, net_b, midpoint, q)

    for ref, pin, net, off in (
        ("C109", "29", "DISP_SW", -0.78), ("C110", "29", "DISP_SW", 0.78),
        ("C111", "31", "BIO_SW", -0.78), ("C112", "31", "BIO_SW", 0.78),
    ):
        o = pin_out(pin)
        q = pin_tangent(pin)
        midpoint = add(add(up[pin], mul(o, 1.38)), mul(q, off))
        repl[ref] = place_2t(idx[ref]["block"], net, "GND", midpoint, q)

    for ref, pin, net_b, off in (
        ("R105", "28", "LDO1_IN", -0.46),
        ("R106", "30", "LDO2_IN", 0.46),
    ):
        o = pin_out(pin)
        q = pin_tangent(pin)
        midpoint = add(add(up[pin], mul(o, 1.02)), mul(q, off))
        repl[ref] = place_2t(idx[ref]["block"], "VSYS", net_b, midpoint, q)

    for ref, pin, net in (("R103", "13", "SYS_I2C_SDA"), ("R104", "14", "SYS_I2C_SCL")):
        o = pin_out(pin)
        q = pin_tangent(pin)
        repl[ref] = place_2t(
            idx[ref]["block"], "+1V8", net, add(up[pin], mul(o, 1.00)), q)

    out_text = replace_blocks(text, repl)
    if out_text.count("(") != out_text.count(")"):
        raise SystemExit("r13 PCB parenthesis balance failed")

    out_idx = build_index(out_text)
    positions = {ref: footprint_at(out_idx[ref]["block"]) for ref in sorted(PMIC_REFS)}
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    bbox = {"width_mm": max(xs) - min(xs), "height_mm": max(ys) - min(ys)}
    if bbox["width_mm"] > 13.5 or bbox["height_mm"] > 13.5:
        raise SystemExit(f"r13 PMIC cluster escaped compact reserve sanity bound: {bbox}")

    if R13_DIR.exists():
        shutil.rmtree(R13_DIR)
    R13_DIR.mkdir(parents=True)
    R13_PCB.write_text(out_text, encoding="utf-8")
    shutil.copy2(R11_PRO, R13_PRO)
    report = {
        "revision": "r13-npm1300-reference-placement-implementation",
        "source": str(R11_PCB.relative_to(ROOT)),
        "source_sha256": EXPECTED_R11_PCB_SHA256,
        "output": str(R13_PCB.relative_to(ROOT)),
        "output_sha256": sha256(R13_PCB),
        "u2_center_mm": [ux, uy, ua],
        "pmic_cluster_bbox_mm": bbox,
        "moved_refs": sorted(PMIC_REFS - {"U2"}),
        "placement_method": "actual_U2_pad_geometry_plus_pad_anchored_power_passives",
        "routing_status": "NOT_STARTED_IN_MATERIALIZER__RUN_KICAD_DRC_BEFORE_POWER_ROUTING",
        "validation_authority": "kicad-cli pcb drc --severity-all",
        "release_status": "NOT_FOR_GERBER",
    }
    R13_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PCB r13 nPM1300 placement materialized at {R13_PCB}")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
