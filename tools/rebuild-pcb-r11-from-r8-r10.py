#!/usr/bin/env python3
"""Rebuild the r11 real-net placement seed from authoritative r8 + r10.

The historical compressed r11 payload in Git is truncated and cannot be
recovered byte-for-byte. This tool therefore does NOT attempt to recreate the
lost PCB coordinates. It constructs a new deterministic real-net seed from:

  * recovered r8-equivalent PCB topology XML (from retained capture evidence)
  * r10 KiCad floorplan board (mechanical/keep-out authority)
  * installed KiCad 9.0.9 footprint libraries

J3/J5/J6 remain intentionally absent. KiCad's own PCB DRC plus explicit
pin/net audit remain validation authority; this script is only the reconstruction
mechanism.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
R10_PCB = ROOT / "hardware/main-board/pcb/AegisBioWatch-MainBoard-Floorplan-r10.kicad_pcb"
R10_PRO = ROOT / "hardware/main-board/pcb/AegisBioWatch-MainBoard-Floorplan-r10.kicad_pro"
OUT_DIR = ROOT / "hardware/main-board/pcb/placement-r11-rebuilt"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-PlacementSeed-r11-rebuilt.kicad_pcb"
OUT_PRO = OUT_DIR / "AegisBioWatch-MainBoard-PlacementSeed-r11-rebuilt.kicad_pro"
OUT_REPORT = OUT_DIR / "placement-seed-manifest-r11-rebuilt.json"
EXCLUDED = {"J3", "J5", "J6"}
FP_ROOTS = [Path("/usr/share/kicad/footprints"), Path("/usr/local/share/kicad/footprints")]

ZONES = {
    "MCU_RF": (116.25, 72.25, 128.75, 85.75),
    "PMIC": (104.75, 87.25, 116.75, 97.75),
    "FLASH": (104.20, 99.15, 113.75, 103.75),
    "HAPTIC": (113.25, 99.15, 121.75, 103.75),
    "BIO": (100.25, 74.25, 112.75, 82.75),
    "DEBUG": (100.25, 83.20, 106.75, 87.75),
    "DISPLAY": (121.25, 94.25, 135.75, 101.75),
    "DOCK": (100.25, 88.25, 106.75, 93.75),
    "MISC_A": (107.25, 83.25, 115.75, 86.75),
    "MISC_B": (117.25, 87.25, 128.75, 93.50),
}

FIXED_ANCHORS = {
    "U1": (122.40, 79.00),
    "U2": (110.75, 92.50),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def natural_key(ref: str):
    return [int(s) if s.isdigit() else s for s in re.split(r"(\d+)", ref)]


def fp_path(identifier: str) -> tuple[Path, str]:
    if ":" not in identifier:
        raise ValueError(f"invalid footprint identifier: {identifier!r}")
    lib, name = identifier.split(":", 1)
    for root in FP_ROOTS:
        pretty = root / f"{lib}.pretty"
        if (pretty / f"{name}.kicad_mod").exists():
            return pretty, name
    raise FileNotFoundError(f"footprint not installed: {identifier}")


def mm(iu: int) -> float:
    return float(pcbnew.ToMM(iu))


def iu(value_mm: float) -> int:
    return int(pcbnew.FromMM(value_mm))


def load_fp(identifier: str):
    pretty, name = fp_path(identifier)
    fp = pcbnew.FootprintLoad(str(pretty), name)
    if fp is None:
        raise RuntimeError(f"pcbnew.FootprintLoad failed: {identifier}")
    return fp


def component_zone(comp: dict) -> str:
    sheet = comp["sheet"].upper()
    value = comp["value"].upper()
    ref = comp["ref"]
    text = f"{sheet} {value}"
    if "MCU_RF" in text or "CLOCK" in text or ref == "U1":
        return "MCU_RF"
    if "PMIC" in text or "CHARG" in text or ref == "U2":
        return "PMIC"
    if "FLASH" in text or "W25Q" in text:
        return "FLASH"
    if "HAPTIC" in text or "DRV2605" in text or "C10-100" in text:
        return "HAPTIC"
    if "BIO" in text:
        return "BIO"
    if "DEBUG" in text or "SWD" in text or "TC2030" in text:
        return "DEBUG"
    if "DISPLAY" in text or "TOUCH" in text or "AMOLED" in text:
        return "DISPLAY"
    if "POWER_INPUT" in text or "DOCK" in text or "PMEG" in text or "PESD" in text:
        return "DOCK"
    return "MISC_A"


def parse_netlist(path: Path):
    root = ET.parse(path).getroot()
    comps = []
    for c in root.findall("./components/comp"):
        sp = c.find("sheetpath")
        comps.append({
            "ref": c.attrib["ref"],
            "value": (c.findtext("value") or "").strip(),
            "footprint": (c.findtext("footprint") or "").strip(),
            "sheet": (sp.attrib.get("names", "") if sp is not None else ""),
        })
    nets = []
    for n in root.findall("./nets/net"):
        name = n.attrib.get("name", "")
        nodes = [{"ref": x.attrib["ref"], "pin": x.attrib["pin"]} for x in n.findall("node")]
        nets.append({"code": int(n.attrib["code"]), "name": name, "nodes": nodes})
    return comps, nets


def bbox_local_mm(fp):
    fp.SetPosition(pcbnew.VECTOR2I(0, 0))
    box = fp.GetBoundingBox()
    return (mm(box.GetX()), mm(box.GetY()), mm(box.GetWidth()), mm(box.GetHeight()))


def rect_for_fp_at_bbox_min(fp, bbox_min_x: float, bbox_min_y: float, margin: float = 0.25):
    lx, ly, w, h = bbox_local_mm(fp)
    origin_x = bbox_min_x - lx
    origin_y = bbox_min_y - ly
    fp.SetPosition(pcbnew.VECTOR2I(iu(origin_x), iu(origin_y)))
    return (bbox_min_x - margin, bbox_min_y - margin,
            bbox_min_x + w + margin, bbox_min_y + h + margin)


def overlaps(a, b, gap: float = 0.0):
    return not (a[2] + gap <= b[0] or b[2] + gap <= a[0] or
                a[3] + gap <= b[1] or b[3] + gap <= a[1])


def place_anchor(fp, center_x: float, center_y: float, margin: float = 0.35):
    lx, ly, w, h = bbox_local_mm(fp)
    bbox_min_x = center_x - w / 2
    bbox_min_y = center_y - h / 2
    return rect_for_fp_at_bbox_min(fp, bbox_min_x, bbox_min_y, margin)


def scan_place(fp, zone, occupied, margin: float = 0.25):
    x1, y1, x2, y2 = zone
    lx, ly, w, h = bbox_local_mm(fp)
    step = 0.20
    max_x = x2 - w
    max_y = y2 - h
    y = y1
    while y <= max_y + 1e-9:
        x = x1
        while x <= max_x + 1e-9:
            candidate = (x - margin, y - margin, x + w + margin, y + h + margin)
            if all(not overlaps(candidate, r, 0.10) for r in occupied):
                rect_for_fp_at_bbox_min(fp, x, y, margin)
                return candidate
            x += step
        y += step
    return None


def board_add_net(board, name: str):
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    return net


def find_pad(fp, number: str):
    for pad in fp.Pads():
        if str(pad.GetNumber()) == str(number):
            return pad
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--netlist", required=True)
    args = ap.parse_args()
    netlist = Path(args.netlist)

    comps, nets = parse_netlist(netlist)
    if len(comps) != 79:
        raise SystemExit(f"r8 component count changed: expected 79, got {len(comps)}")
    node_count = sum(len(n["nodes"]) for n in nets)
    if len(nets) != 86 or node_count != 268:
        raise SystemExit(f"r8 topology changed: nets={len(nets)} nodes={node_count}, expected 86/268")

    included = [c for c in comps if c["ref"] not in EXCLUDED]
    if len(included) != 76:
        raise SystemExit(f"expected 76 non-J3/J5/J6 components, got {len(included)}")
    missing_fp = [c["ref"] for c in included if not c["footprint"]]
    if missing_fp:
        raise SystemExit(f"nonexcluded components without footprint assignment: {missing_fp}")

    board = pcbnew.LoadBoard(str(R10_PCB))
    if board is None:
        raise SystemExit(f"failed to load r10 floorplan: {R10_PCB}")
    existing_footprints = list(board.GetFootprints())
    if existing_footprints:
        raise SystemExit(f"r10 floorplan unexpectedly contains {len(existing_footprints)} footprints")

    netinfo = {n["name"]: board_add_net(board, n["name"]) for n in nets}

    fps = {}
    component_meta = {}
    for c in included:
        fp = load_fp(c["footprint"])
        fp.SetReference(c["ref"])
        fp.SetValue(c["value"])
        board.Add(fp)
        fps[c["ref"]] = fp
        component_meta[c["ref"]] = c

    assigned_nodes = 0
    missing_pads = []
    for n in nets:
        target_net = netinfo[n["name"]]
        for node in n["nodes"]:
            ref = node["ref"]
            if ref in EXCLUDED:
                continue
            fp = fps.get(ref)
            if fp is None:
                raise SystemExit(f"netlist node refers to absent included footprint {ref}")
            pad = find_pad(fp, node["pin"])
            if pad is None:
                missing_pads.append({"ref": ref, "pin": node["pin"], "net": n["name"]})
                continue
            pad.SetNet(target_net)
            assigned_nodes += 1
    if missing_pads:
        raise SystemExit(f"footprint pin mismatch: {missing_pads}")

    expected_included_nodes = node_count - sum(
        1 for n in nets for node in n["nodes"] if node["ref"] in EXCLUDED
    )
    if assigned_nodes != expected_included_nodes:
        raise SystemExit(f"assigned nodes {assigned_nodes} != expected included nodes {expected_included_nodes}")

    occupied_by_zone = {name: [] for name in ZONES}
    placement = {}
    for ref in ("U1", "U2"):
        if ref in fps:
            zone_name = component_zone(component_meta[ref])
            rect = place_anchor(fps[ref], *FIXED_ANCHORS[ref])
            occupied_by_zone[zone_name].append(rect)
            p = fps[ref].GetPosition()
            placement[ref] = {"zone": zone_name, "x_mm": mm(p.x), "y_mm": mm(p.y), "fixed": True}

    rest = []
    for ref, fp in fps.items():
        if ref in FIXED_ANCHORS:
            continue
        _, _, w, h = bbox_local_mm(fp)
        rest.append((-(w * h), natural_key(ref), ref, w, h))
    rest.sort()

    spill_order = ["MISC_A", "MISC_B", "DISPLAY", "BIO", "DEBUG"]
    for _, _, ref, _, _ in rest:
        fp = fps[ref]
        preferred = component_zone(component_meta[ref])
        candidates = [preferred]
        if preferred.startswith("MISC"):
            candidates = ["MISC_A", "MISC_B"]
        candidates += [z for z in spill_order if z not in candidates]
        rect = None
        used_zone = None
        for zone_name in candidates:
            rect = scan_place(fp, ZONES[zone_name], occupied_by_zone[zone_name])
            if rect is not None:
                used_zone = zone_name
                occupied_by_zone[zone_name].append(rect)
                break
        if rect is None or used_zone is None:
            raise SystemExit(f"unable to pack footprint {ref} ({component_meta[ref]['footprint']})")
        p = fp.GetPosition()
        placement[ref] = {"zone": used_zone, "x_mm": mm(p.x), "y_mm": mm(p.y), "fixed": False}

    board.SynchronizeNetsAndNetClasses(True)
    board.BuildConnectivity()

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    if not pcbnew.SaveBoard(str(OUT_PCB), board):
        raise SystemExit("pcbnew.SaveBoard returned false")
    shutil.copy2(R10_PRO, OUT_PRO)

    report = {
        "revision": "r11-rebuilt-from-r8-r10",
        "reason": "historical r11 compressed payload was truncated and exact source files were not recoverable from Git objects",
        "authority": {
            "electrical": "recovered r8-equivalent PCB topology XML; validate with pin/net audit",
            "mechanical": str(R10_PCB.relative_to(ROOT)),
            "footprints": "KiCad 9.0.9 installed libraries using r8 footprint assignments",
        },
        "components_r8": len(comps),
        "footprints_imported": len(fps),
        "intentionally_absent": sorted(EXCLUDED),
        "nets_r8": len(nets),
        "net_nodes_r8": node_count,
        "net_nodes_assigned_to_present_footprints": assigned_nodes,
        "missing_footprint_pins": 0,
        "placement": placement,
        "output_pcb": str(OUT_PCB.relative_to(ROOT)),
        "output_pcb_sha256": sha(OUT_PCB),
        "source_r10_sha256": sha(R10_PCB),
        "kicad_build": pcbnew.GetBuildVersion(),
        "routing_status": "UNROUTED_REAL_NET_PLACEMENT_SEED",
        "validation_status": "PENDING_KICAD_PCB_DRC",
        "release_status": "NOT_FOR_GERBER",
    }
    OUT_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
