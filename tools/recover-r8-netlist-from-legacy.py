#!/usr/bin/env python3
"""Recover the Phase-1 r8 PCB electrical topology from retained legacy capture.

This is a deterministic recovery bridge for the historical native-r7/r8 payload
that was truncated in Git. It does not claim byte-for-byte recovery of the lost
native KiCad files. It reconstructs the PCB-stage component/pin/net topology from:

* the five retained legacy Eeschema sheets;
* the retained project legacy symbol library (for exact custom pin geometry);
* the retained r8 BOM (component values/footprints);
* the documented r8 J8/J9 interface freeze;
* the documented U1 pin-9 spelling normalization used by the design pin map.

The script fails closed unless the independently retained invariants recover
exactly: 79 BOM components, 86 PCB nets, 268 pin/net nodes, and all known r8
interface checks. J3/J5/J6 remain components in the BOM but intentionally have
no PCB-stage pin/net nodes because their physical interfaces were not frozen.

KiCad PCB DRC remains mandatory after this recovered XML is used to rebuild r11.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / "hardware/main-board/kicad/capture"
BOM = ROOT / "hardware/main-board/kicad/generated/BOM-r8.csv"
DEFAULT_OUT = ROOT / "hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml"
DEFAULT_REPORT = ROOT / "docs/r8-topology-recovery-validation.json"
LEGACY_SHEETS = [
    "MCU_RF_CLOCK",
    "PMIC_CHARGER",
    "STORAGE_HAPTIC",
    "DISPLAY_TOUCH",
    "BIO_INTERFACE",
]
PHYSICAL_GATES = {"J3", "J5", "J6"}

SYNTHETIC_COMPONENT_SHEETS = {"J8": "DEBUG_POWER", "J9": "DEBUG_POWER"}
SYNTHETIC_NODES = [
    ("J8", "1", "+1V8"),
    ("J8", "2", "SWDIO"),
    ("J8", "3", "NRF_RESET_N"),
    ("J8", "4", "SWDCLK"),
    ("J8", "5", "GND"),
    ("J8", "6", "SWO"),
    ("J9", "1", "GND"),
    ("J9", "2", "SIDE_BUTTON"),
]

NET_NORMALIZATION = {"GPIO_SPARE_CLK": "SPARE_CLK_GPIO"}

U1_CRITICAL = {
    "1": "NRF_XL1", "2": "NRF_XL2", "4": "DISP_PWR_EN",
    "10": "+1V8", "11": "DISP_QSPI_D3", "12": "DISP_QSPI_SCK",
    "13": "DISP_QSPI_D0", "14": "DISP_QSPI_D2", "15": "DISP_QSPI_D1",
    "16": "DISP_QSPI_CS_N", "17": "AUX_SPI_SCK", "18": "SWO",
    "19": "AUX_SPI_MOSI", "20": "AUX_SPI_MISO", "21": "FLASH_CS_N",
    "23": "SYS_I2C_SDA", "24": "SYS_I2C_SCL", "25": "SWDIO",
    "26": "SWDCLK", "27": "DISP_RST_N", "28": "DISP_TE",
    "29": "TOUCH_RST_N", "30": "NRF_RESET_RAW", "31": "RF_MCU",
    "32": "GND", "33": "NRF_DECA_RF", "34": "NRF_XC1",
    "35": "NRF_XC2", "37": "TOUCH_INT_N", "38": "IMU_INT2",
    "39": "IMU_INT1", "40": "PPG_INT_N", "41": "EDA_INT_N",
    "42": "BIO_SPI_CS_N", "43": "NRF_DECA_RF", "44": "GND",
    "45": "NRF_DECD", "46": "NRF_DCC", "49": "GND",
}
U2_CRITICAL = {
    "1": "+1V8", "2": "PVSS1_LOCAL", "3": "PMIC_SW1", "4": "VSYS",
    "5": "PMIC_SW2", "6": "PVSS2_LOCAL", "12": "+1V8",
    "13": "SYS_I2C_SDA", "14": "SYS_I2C_SCL", "15": "SHIP_HOLD",
    "16": "PMIC_VSET2", "17": "PMIC_VSET1", "18": "BAT_NTC",
    "19": "VBAT", "20": "VSYS", "21": "CHG_5V",
    "22": "VBUSOUT_SENSE", "28": "LDO1_IN", "29": "DISP_SW",
    "30": "LDO2_IN", "31": "BIO_SW", "32": "+3V0", "33": "GND",
}


class DSU:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.parent[b] = a


def parse_legacy_library(path: Path):
    symbols = {}
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DEF "):
            current = line.split()[1]
            symbols[current] = []
        elif current and line.startswith("X "):
            p = line.split()
            symbols[current].append((p[2], int(p[3]), int(p[4]), p[1]))
        elif line == "ENDDEF":
            current = None
    return symbols


def parse_sheet(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    components, labels, wires = [], [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line == "$Comp":
            block = []
            i += 1
            while i < len(lines) and lines[i] != "$EndComp":
                block.append(lines[i])
                i += 1
            sym = ref = value = footprint = None
            pos = matrix = None
            for b in block:
                if b.startswith("L "):
                    p = b.split(); sym, ref = p[1], p[2]
                elif b.startswith("P "):
                    p = b.split(); pos = (int(p[1]), int(p[2]))
                elif b.startswith('F 1 "'):
                    m = re.match(r'F 1 "(.*)"', b); value = m.group(1) if m else None
                elif b.startswith('F 2 "'):
                    m = re.match(r'F 2 "(.*)"', b); footprint = m.group(1) if m else None
                elif re.fullmatch(r"\s*-?\d+\s+-?\d+\s+-?\d+\s+-?\d+\s*", b):
                    matrix = tuple(int(v) for v in b.split())
            if sym is None or ref is None or pos is None or matrix is None:
                raise ValueError(f"incomplete component block in {path}: {block}")
            components.append({
                "sheet": path.stem, "symbol": sym, "ref": ref,
                "legacy_value": value or "", "legacy_footprint": footprint or "",
                "pos": pos, "matrix": matrix,
            })
        elif line.startswith("Text Label "):
            p = line.split()
            labels.append((int(p[2]), int(p[3]), lines[i + 1].strip()))
            i += 1
        elif line == "Wire Wire Line":
            p = [int(v) for v in lines[i + 1].split()]
            if len(p) != 4:
                raise ValueError(f"bad wire in {path}: {lines[i + 1]}")
            wires.append(tuple(p)); i += 1
        i += 1
    return components, labels, wires


def standard_local_pins(symbol: str):
    if symbol in {
        "Device:C_Small", "Device:R_Small", "Device:L_Small",
        "Device:FerriteBead_Small", "Device:Net-Tie_2",
    }:
        return [("1", 0, 100, "1"), ("2", 0, -100, "2")]
    if symbol == "Device:Crystal_Small":
        return [("1", -100, 0, "1"), ("2", 100, 0, "2")]
    if symbol.startswith("Connector_Generic:Conn_01x"):
        n = int(re.search(r"01x(\d+)", symbol).group(1))
        start = math.floor((n - 1) / 2) * 100
        return [(str(i), -200, start - (i - 1) * 100, str(i)) for i in range(1, n + 1)]
    if symbol == "Connector_Generic:Conn_02x10_Odd_Even":
        result = []
        for row in range(10):
            y = 400 - row * 100
            result.append((str(2 * row + 1), -200, y, str(2 * row + 1)))
            result.append((str(2 * row + 2), 300, y, str(2 * row + 2)))
        return result
    if symbol == "Transistor_FET:2N7002":
        return [("1", -200, 0, "G"), ("2", 100, -200, "S"), ("3", 100, 200, "D")]
    raise KeyError(symbol)


def component_local_pins(component, custom_symbols):
    symbol = component["symbol"]
    if symbol.startswith("AegisBioWatch:"):
        name = symbol.split(":", 1)[1]
        if name not in custom_symbols:
            raise KeyError(f"missing custom symbol {name}")
        return custom_symbols[name]
    return standard_local_pins(symbol)


def absolute_pins(component, custom_symbols):
    px, py = component["pos"]
    a, b, c, d = component["matrix"]
    return [
        (number, px + a * x + b * y, py + c * x + d * y, name)
        for number, x, y, name in component_local_pins(component, custom_symbols)
    ]


def point_on_segment(point, segment):
    x, y = point; x1, y1, x2, y2 = segment
    return ((x1 == x2 == x and min(y1, y2) <= y <= max(y1, y2)) or
            (y1 == y2 == y and min(x1, x2) <= x <= max(x1, x2)))


def recover_sheet_nodes(sheet_name, parsed, custom_symbols):
    components, labels, wires = parsed
    points = {(x, y) for x, y, _ in labels}
    pins_by_ref = {}
    for component in components:
        pins = absolute_pins(component, custom_symbols)
        pins_by_ref[component["ref"]] = pins
        points.update((x, y) for _, x, y, _ in pins)
    for x1, y1, x2, y2 in wires:
        points.add((x1, y1)); points.add((x2, y2))
    dsu = DSU()
    for segment in wires:
        on_wire = [point for point in points if point_on_segment(point, segment)]
        if on_wire:
            anchor = on_wire[0]
            for point in on_wire[1:]:
                dsu.union(anchor, point)
    labels_by_root = defaultdict(set)
    for x, y, net in labels:
        labels_by_root[dsu.find((x, y))].add(net)
    nodes = []
    for component in components:
        for pin, x, y, pin_name in pins_by_ref[component["ref"]]:
            found = labels_by_root.get(dsu.find((x, y)), set())
            if len(found) != 1:
                raise ValueError(
                    f"{sheet_name}:{component['ref']}.{pin} {pin_name} at {(x, y)} "
                    f"resolved to {sorted(found)}; expected exactly one net label"
                )
            nodes.append((component["ref"], str(pin), next(iter(found))))
    return nodes


def read_bom(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {row["Reference"]: row for row in rows}


def natural_ref(ref: str):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", ref)]


def validate_pin_map(node_lookup, ref, expected):
    failures = []
    for pin, net in expected.items():
        actual = node_lookup.get((ref, pin))
        if actual != net:
            failures.append({"ref": ref, "pin": pin, "expected": net, "actual": actual})
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = ap.parse_args()

    custom_symbols = parse_legacy_library(CAP / "AegisBioWatch.lib")
    parsed_sheets = {name: parse_sheet(CAP / f"{name}.sch") for name in LEGACY_SHEETS}
    legacy_components = [c for name in LEGACY_SHEETS for c in parsed_sheets[name][0]]
    if len(legacy_components) != 77:
        raise SystemExit(f"legacy component count changed: expected 77, got {len(legacy_components)}")
    legacy_refs = [c["ref"] for c in legacy_components]
    if len(set(legacy_refs)) != len(legacy_refs):
        raise SystemExit("duplicate legacy component reference")

    legacy_nodes = []
    for name in LEGACY_SHEETS:
        legacy_nodes.extend((name, ref, pin, net) for ref, pin, net in recover_sheet_nodes(name, parsed_sheets[name], custom_symbols))
    if len(legacy_nodes) != 278:
        raise SystemExit(f"legacy pin-node count changed: expected 278, got {len(legacy_nodes)}")
    legacy_net_count = len({net for _, _, _, net in legacy_nodes})
    if legacy_net_count != 87:
        raise SystemExit(f"legacy flat label count changed: expected 87, got {legacy_net_count}")

    gated_nodes = [n for n in legacy_nodes if n[1] in PHYSICAL_GATES]
    if len(gated_nodes) != 18:
        raise SystemExit(f"J3/J5/J6 node count changed: expected 18, got {len(gated_nodes)}")

    final_nodes = []
    for sheet, ref, pin, net in legacy_nodes:
        if ref in PHYSICAL_GATES:
            continue
        final_nodes.append((sheet, ref, pin, NET_NORMALIZATION.get(net, net)))
    final_nodes.extend(("DEBUG_POWER", ref, pin, net) for ref, pin, net in SYNTHETIC_NODES)

    bom = read_bom(BOM)
    if len(bom) != 79:
        raise SystemExit(f"r8 BOM count changed: expected 79, got {len(bom)}")
    component_sheet = {c["ref"]: c["sheet"] for c in legacy_components}
    component_sheet.update(SYNTHETIC_COMPONENT_SHEETS)
    if set(component_sheet) != set(bom):
        raise SystemExit(
            f"component/BOM refs differ: missing={sorted(set(bom)-set(component_sheet))}, "
            f"extra={sorted(set(component_sheet)-set(bom))}"
        )
    if len(final_nodes) != 268:
        raise SystemExit(f"recovered node count mismatch: expected 268, got {len(final_nodes)}")
    final_nets = sorted({net for _, _, _, net in final_nodes})
    if len(final_nets) != 86:
        raise SystemExit(f"recovered net count mismatch: expected 86, got {len(final_nets)}")

    node_lookup = {(ref, pin): net for _, ref, pin, net in final_nodes}
    if len(node_lookup) != len(final_nodes):
        raise SystemExit("duplicate ref/pin nodes in recovered topology")

    failures = validate_pin_map(node_lookup, "U1", U1_CRITICAL)
    failures += validate_pin_map(node_lookup, "U2", U2_CRITICAL)
    r8_interfaces = {
        ("J8", "1"): "+1V8", ("J8", "2"): "SWDIO", ("J8", "3"): "NRF_RESET_N",
        ("J8", "4"): "SWDCLK", ("J8", "5"): "GND", ("J8", "6"): "SWO",
        ("J9", "1"): "GND", ("J9", "2"): "SIDE_BUTTON",
        ("J101", "1"): "SHIP_HOLD", ("J101", "2"): "GND",
        ("J4", "1"): "HAPTIC_OUT_P", ("J4", "2"): "HAPTIC_OUT_N",
    }
    for key, expected in r8_interfaces.items():
        actual = node_lookup.get(key)
        if actual != expected:
            failures.append({"ref": key[0], "pin": key[1], "expected": expected, "actual": actual})
    if failures:
        raise SystemExit("critical recovered pin/net mismatches: " + json.dumps(failures, indent=2))

    export = ET.Element("export", version="E")
    design = ET.SubElement(export, "design")
    ET.SubElement(design, "source").text = "AegisBioWatch retained legacy capture -> recovered r8 PCB topology"
    ET.SubElement(design, "date").text = "recovered-deterministically"
    ET.SubElement(design, "tool").text = "AegisBioWatch recover-r8-netlist-from-legacy.py"
    comps_el = ET.SubElement(export, "components")
    for ref in sorted(bom, key=natural_ref):
        row = bom[ref]
        comp = ET.SubElement(comps_el, "comp", ref=ref)
        ET.SubElement(comp, "value").text = row["Value"]
        ET.SubElement(comp, "footprint").text = row["Footprint"]
        ET.SubElement(comp, "sheetpath", names=f"/{component_sheet[ref]}/", tstamps=f"/{component_sheet[ref]}/{ref}")

    nodes_by_net = defaultdict(list)
    for sheet, ref, pin, net in final_nodes:
        nodes_by_net[net].append((ref, pin, sheet))
    nets_el = ET.SubElement(export, "nets")
    for code, net in enumerate(sorted(nodes_by_net), 1):
        net_el = ET.SubElement(nets_el, "net", code=str(code), name=net)
        for ref, pin, _sheet in sorted(nodes_by_net[net], key=lambda x: (natural_ref(x[0]), int(x[1]) if x[1].isdigit() else x[1])):
            ET.SubElement(net_el, "node", ref=ref, pin=pin)

    ET.indent(export, space="  ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(export).write(args.output, encoding="utf-8", xml_declaration=True)

    report = {
        "revision": "r8-topology-recovered-from-retained-legacy-capture",
        "status": "RECOVERED_TOPOLOGY_NOT_BYTE_IDENTICAL_NATIVE_R8",
        "source": {
            "legacy_sheets": LEGACY_SHEETS,
            "project_symbol_library": "hardware/main-board/kicad/capture/AegisBioWatch.lib",
            "bom": "hardware/main-board/kicad/generated/BOM-r8.csv",
        },
        "invariants": {
            "legacy_components": len(legacy_components),
            "legacy_flat_label_nets": legacy_net_count,
            "legacy_pin_nodes": len(legacy_nodes),
            "physical_gate_nodes_removed_J3_J5_J6": len(gated_nodes),
            "r8_components": len(bom),
            "r8_nets": len(final_nets),
            "r8_pin_nodes": len(final_nodes),
            "expected_r11_components": 79,
            "expected_r11_nets": 86,
            "expected_r11_pin_nodes": 268,
        },
        "transformations": {
            "J3_J5_J6": "components retained; pin/net nodes deliberately omitted until physical interface freeze",
            "J8": "TC2030 six-pin SWD mapping restored from r8 interface-freeze evidence",
            "J9": "side-button two-pin mapping restored from r8 interface-freeze evidence",
            "GPIO_SPARE_CLK": "normalized to SPARE_CLK_GPIO to match retained phase1 pin map and J7.20",
        },
        "validation": {
            "all_legacy_symbol_pins_resolved_to_exactly_one_label": True,
            "u1_critical_checks": len(U1_CRITICAL),
            "u2_critical_checks": len(U2_CRITICAL),
            "r8_interface_checks": len(r8_interfaces),
            "critical_failures": failures,
            "result": "PASS_TOPOLOGY_RECOVERY",
        },
        "output": str(args.output.relative_to(ROOT)),
        "release_status": "NOT_FOR_GERBER",
        "next_authority": "KiCad 9.0.9 PCB DRC and pin/net audit on rebuilt r11/r13 artifacts",
        "privacy_boundary": "engineering_abstractions_only",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
