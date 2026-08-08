#!/usr/bin/env python3
"""Package executed KiCad r13 evidence into deterministic Git payload files.

This script never invents validation results. It requires an actual KiCad DRC
JSON file produced by the workflow and records violations and unconnected items
separately.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import os
import tarfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R13 = ROOT / "hardware/main-board/pcb/placement-r13"
PCB = R13 / "AegisBioWatch-MainBoard-Placement-r13.kicad_pcb"
PRO = R13 / "AegisBioWatch-MainBoard-Placement-r13.kicad_pro"
REPORT = R13 / "placement-implementation-r13.json"
DRC = Path(os.environ.get("R13_DRC_JSON", "/tmp/drc-r13.json"))
OUT = ROOT / "hardware/main-board/pcb/placement-r13-payload"
RESULT = ROOT / "docs/pcb-placement-implementation-r13-kicad-result.json"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def violation_type(v):
    if isinstance(v, dict):
        for key in ("type", "name", "category", "severity"):
            value = v.get(key)
            if value:
                return str(value)
    return "unknown"


def main():
    for p in (PCB, PRO, REPORT, DRC):
        if not p.exists():
            raise SystemExit(f"required executed evidence missing: {p}")

    drc_raw = DRC.read_bytes()
    drc = json.loads(drc_raw)
    violations = drc.get("violations", [])
    unconnected = drc.get("unconnected_items", [])
    if not isinstance(violations, list) or not isinstance(unconnected, list):
        raise SystemExit("unexpected KiCad DRC JSON schema")

    kicad_version = os.environ.get("KICAD_VERSION", "unknown")
    source_head = os.environ.get("GITHUB_SHA", "unknown")
    implementation = json.loads(REPORT.read_text(encoding="utf-8"))

    result = {
        "revision": "r13-npm1300-reference-placement-implementation",
        "evidence": "EXECUTED_KICAD_CLI",
        "kicad_cli": kicad_version,
        "source_git_sha": source_head,
        "rule_violations": len(violations),
        "unconnected_items": len(unconnected),
        "violation_types": dict(sorted(Counter(violation_type(v) for v in violations).items())),
        "routing_status": "PLACEMENT_ONLY_UNROUTED",
        "complete_pcb_drc_pass": len(violations) == 0 and len(unconnected) == 0,
        "placement_rule_clean": len(violations) == 0,
        "expected_unconnected_items_for_placement_only_r13": 186,
        "output_pcb_sha256": digest(PCB.read_bytes()),
        "drc_json_sha256": digest(drc_raw),
        "materializer_report_sha256": digest(REPORT.read_bytes()),
        "release_status": "NOT_FOR_GERBER",
        "note": "Rule violations and unconnected items are intentionally reported separately.",
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    files = {
        PCB.name: PCB.read_bytes(),
        PRO.name: PRO.read_bytes(),
        REPORT.name: REPORT.read_bytes(),
        "drc-r13.json": drc_raw,
        RESULT.name: RESULT.read_bytes(),
    }

    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as tf:
        for name in sorted(files):
            raw = files[name]
            ti = tarfile.TarInfo(name=name)
            ti.size = len(raw)
            ti.mtime = 0
            ti.uid = ti.gid = 0
            ti.uname = ti.gname = ""
            ti.mode = 0o644
            tf.addfile(ti, io.BytesIO(raw))

    gz_buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=gz_buffer, mode="wb", filename="", mtime=0, compresslevel=9) as gz:
        gz.write(tar_buffer.getvalue())
    archive = gz_buffer.getvalue()

    OUT.mkdir(parents=True, exist_ok=True)
    archive_path = OUT / "r13-placement-kicad-evidence.tar.gz.b64"
    encoded = base64.b64encode(archive).decode("ascii")
    archive_path.write_text("\n".join(encoded[i:i+120] for i in range(0, len(encoded), 120)) + "\n", encoding="ascii")

    manifest = {
        "revision": "r13-npm1300-reference-placement-implementation",
        "archive": str(archive_path.relative_to(ROOT)),
        "archive_bytes": len(archive),
        "archive_sha256": digest(archive),
        "files": {name: {"bytes": len(raw), "sha256": digest(raw)} for name, raw in sorted(files.items())},
        "kicad_result": result,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
