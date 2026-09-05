#!/usr/bin/env python3
"""Inspect r8 KiCad XML netlist and resolve assigned footprints in CI."""
from __future__ import annotations
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path

NETLIST = Path(os.environ.get("R8_NETLIST", "/tmp/aegis-r8.xml"))
FOOTPRINT_ROOTS = [Path("/usr/share/kicad/footprints"), Path("/usr/local/share/kicad/footprints")]
EXCLUDED = {"J3", "J5", "J6"}

def resolve(fid: str):
    if not fid or ":" not in fid:
        return None
    lib, name = fid.split(":", 1)
    for root in FOOTPRINT_ROOTS:
        p = root / f"{lib}.pretty" / f"{name}.kicad_mod"
        if p.exists():
            return str(p)
    return None

def main():
    root = ET.parse(NETLIST).getroot()
    comps = []
    for c in root.findall("./components/comp"):
        ref = c.attrib["ref"]
        value = (c.findtext("value") or "").strip()
        fp = (c.findtext("footprint") or "").strip()
        comps.append({"ref": ref, "value": value, "footprint": fp, "resolved": resolve(fp), "excluded": ref in EXCLUDED})
    nets = root.findall("./nets/net")
    nodes = sum(len(n.findall("node")) for n in nets)
    missing_fp = [c for c in comps if not c["footprint"]]
    unresolved = [c for c in comps if c["footprint"] and not c["resolved"] and not c["excluded"]]
    report = {
        "components": len(comps),
        "nets": len(nets),
        "net_nodes": nodes,
        "excluded_refs": sorted(EXCLUDED),
        "assigned_nonexcluded": sum(1 for c in comps if c["footprint"] and not c["excluded"]),
        "missing_footprint": missing_fp,
        "unresolved_nonexcluded": unresolved,
        "components_detail": comps,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if unresolved:
        raise SystemExit(f"{len(unresolved)} assigned nonexcluded footprints could not be resolved")

if __name__ == "__main__":
    main()
