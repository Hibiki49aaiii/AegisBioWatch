#!/usr/bin/env python3
"""Package a KiCad-validated rebuilt r11 into the canonical materialized payload.

The packager is intentionally strict. It only replaces the corrupted historical
payload when the reconstructed seed is backed by:
  * r8 ERC = 0 violations
  * r8 topology = 79 components / 86 nets / 268 nodes
  * 76 present footprints, J3/J5/J6 intentionally absent
  * KiCad 9.0.9 PCB DRC rule violations = 0
  * unconnected items = 186 (same electrical topology, still unrouted)

The archive container gets new hashes. The lost historical PCB SHA is not
pretended to have been recovered.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import os
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REBUILT = ROOT / "hardware/main-board/pcb/placement-r11-rebuilt"
PCB = REBUILT / "AegisBioWatch-MainBoard-PlacementSeed-r11-rebuilt.kicad_pcb"
PRO = REBUILT / "AegisBioWatch-MainBoard-PlacementSeed-r11-rebuilt.kicad_pro"
REPORT = REBUILT / "placement-seed-manifest-r11-rebuilt.json"
DRC = Path(os.environ.get("R11_REBUILT_DRC_JSON", "/tmp/drc-r11-rebuilt.json"))
ERC = Path(os.environ.get("R8_ERC_JSON", "/tmp/erc-r8.json"))
NETLIST = Path(os.environ.get("R8_NETLIST", "/tmp/aegis-r8.xml"))
PAY = ROOT / "hardware/main-board/pcb/placement-r11-payload"
VALIDATION = ROOT / "docs/pcb-placement-seed-validation-r11.json"
RECOVERY = ROOT / "docs/pcb-r11-reconstruction.json"

STD_PCB = "AegisBioWatch-MainBoard-PlacementSeed-r11.kicad_pcb"
STD_PRO = "AegisBioWatch-MainBoard-PlacementSeed-r11.kicad_pro"
STD_REPORT = "placement-seed-manifest-r11.json"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def deterministic_archive(files: dict[str, bytes]) -> bytes:
    tb = io.BytesIO()
    with tarfile.open(fileobj=tb, mode="w", format=tarfile.PAX_FORMAT) as tf:
        for name in sorted(files):
            raw = files[name]
            ti = tarfile.TarInfo(name=name)
            ti.size = len(raw)
            ti.mtime = 0
            ti.uid = ti.gid = 0
            ti.uname = ti.gname = ""
            ti.mode = 0o644
            tf.addfile(ti, io.BytesIO(raw))
    gb = io.BytesIO()
    with gzip.GzipFile(fileobj=gb, mode="wb", filename="", mtime=0, compresslevel=9) as gz:
        gz.write(tb.getvalue())
    return gb.getvalue()


def main() -> None:
    for p in (PCB, PRO, REPORT, DRC, ERC, NETLIST):
        if not p.exists():
            raise SystemExit(f"required rebuilt-r11 evidence missing: {p}")

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    drc_raw = DRC.read_bytes()
    drc = json.loads(drc_raw)
    erc_raw = ERC.read_bytes()
    erc = json.loads(erc_raw)

    erc_v = erc.get("violations", [])
    violations = drc.get("violations", [])
    unconnected = drc.get("unconnected_items", [])
    if len(erc_v) != 0:
        raise SystemExit(f"r8 ERC is not clean: {len(erc_v)} violations")
    if len(violations) != 0:
        raise SystemExit(f"rebuilt r11 has {len(violations)} PCB rule violations")
    if len(unconnected) != 186:
        raise SystemExit(f"rebuilt r11 unconnected count is {len(unconnected)}, expected 186")

    invariants = {
        "components_r8": 79,
        "footprints_imported": 76,
        "nets_r8": 86,
        "net_nodes_r8": 268,
        "missing_footprint_pins": 0,
    }
    for key, expected in invariants.items():
        if report.get(key) != expected:
            raise SystemExit(f"rebuilt r11 invariant {key}: {report.get(key)!r} != {expected!r}")

    rebuilt_pcb = PCB.read_bytes()
    rebuilt_pro = PRO.read_bytes()
    canonical_report = dict(report)
    canonical_report.update({
        "revision": "r11-reconstructed-authority",
        "output_pcb": f"hardware/main-board/pcb/placement-r11/{STD_PCB}",
        "output_pcb_sha256": digest(rebuilt_pcb),
        "validation_status": "KICAD_9_0_9_RULE_VIOLATIONS_0_UNCONNECTED_186",
        "historical_pcb_sha256_status": "LOST_CORRUPTED_PAYLOAD_NOT_RECOVERED",
    })
    report_raw = (json.dumps(canonical_report, indent=2, sort_keys=True) + "\n").encode()
    readme_raw = (
        "# AegisBioWatch Main Board r11 reconstructed placement seed\n\n"
        "The historical compressed r11 payload was truncated in Git and its original PCB bytes were not recoverable.\n"
        "This payload is a new deterministic real-net placement seed reconstructed from r8 electrical authority and r10 floorplan authority.\n"
        "J3/J5/J6 remain intentionally absent. The board is unrouted.\n\n"
        "Validation: KiCad 9.0.9 PCB rule violations = 0; unconnected items = 186.\n"
        "Do not describe this as a complete PCB DRC pass and do not use it for Gerber release.\n"
    ).encode()

    files = {
        STD_PCB: rebuilt_pcb,
        STD_PRO: rebuilt_pro,
        STD_REPORT: report_raw,
        "README.md": readme_raw,
        "drc-r11.json": drc_raw,
        "erc-r8.json": erc_raw,
        "r8-netlist.xml": NETLIST.read_bytes(),
    }
    archive = deterministic_archive(files)
    PAY.mkdir(parents=True, exist_ok=True)
    archive_path = PAY / "r11-placement-seed.tar.gz.b64"
    enc = base64.b64encode(archive).decode("ascii")
    archive_path.write_text("\n".join(enc[i:i+120] for i in range(0, len(enc), 120)) + "\n", encoding="ascii")

    outer = {
        "revision": "r11-reconstructed-authority",
        "archive": str(archive_path.relative_to(ROOT)),
        "archive_bytes": len(archive),
        "archive_sha256": digest(archive),
        "files": {name: {"bytes": len(raw), "sha256": digest(raw)} for name, raw in sorted(files.items())},
        "provenance": {
            "electrical": "r8 native KiCad authority",
            "mechanical": "r10 floorplan authority",
            "reconstruction_reason": "historical Base64 payload truncated and exact original r11 PCB not recoverable from Git history/object database",
        },
    }
    (PAY / "manifest.json").write_text(json.dumps(outer, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    validation = {
        "revision": "r11-reconstructed-authority",
        "kicad": "9.0.9",
        "schematic_components": 79,
        "footprints": 76,
        "intentionally_absent": ["J3", "J5", "J6"],
        "nets": 86,
        "pin_net_nodes": 268,
        "missing_footprint_pins": 0,
        "rule_violations": 0,
        "unconnected_items": 186,
        "pcb_sha256": digest(rebuilt_pcb),
        "drc_json_sha256": digest(drc_raw),
        "erc_json_sha256": digest(erc_raw),
        "r8_netlist_sha256": digest(NETLIST.read_bytes()),
        "historical_r11": {
            "original_board_recovered": False,
            "reason": "corrupted compressed payload was the only retained container; exact constituent PCB blob was absent from Git objects",
        },
        "release_status": "NOT_FOR_GERBER",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RECOVERY.write_text(json.dumps({
        "status": "RECONSTRUCTED_FROM_AUTHORITIES",
        "new_r11_pcb_sha256": digest(rebuilt_pcb),
        "payload_archive_sha256": digest(archive),
        "source_r10_sha256": report.get("source_r10_sha256"),
        "r8_netlist_sha256": validation["r8_netlist_sha256"],
        "old_original_pcb_sha256": "f31211be596c4435faa7bdf116bc16239b70e668b6e9377ef26f0909ebce19e2",
        "old_original_pcb_recovered": False,
        "rule_violations": 0,
        "unconnected_items": 186,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "PACKAGED_REBUILT_R11",
        "pcb_sha256": digest(rebuilt_pcb),
        "archive_sha256": digest(archive),
        "files": len(files),
        "rule_violations": 0,
        "unconnected_items": 186,
    }, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
