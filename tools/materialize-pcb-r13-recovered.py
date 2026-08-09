#!/usr/bin/env python3
"""Materialize r13 from the executed, validated recovered-r11 seed.

The historical r11 archive is irrecoverably truncated, so r13 must not invoke
or trust the old payload materializer. This wrapper binds the existing r13
nPM1300 placement algorithm to a freshly rebuilt r11 whose exact PCB SHA is
covered by executed KiCad 9.0.9 DRC evidence and a 268-node physical-pad audit.

The underlying r13 placement algorithm is unchanged: it derives its coordinate
frame from AegisBioWatch U2 pad geometry and places the PMIC support network by
functional pin/net relationship. No third-party absolute coordinates are used.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tools/materialize-pcb-r13.py"
DEFAULT_R11_DIR = ROOT / "hardware/main-board/pcb/placement-r11-rebuilt"
DEFAULT_R11_PCB = DEFAULT_R11_DIR / "AegisBioWatch-MainBoard-PlacementSeed-r11-rebuilt.kicad_pcb"
DEFAULT_R11_PRO = DEFAULT_R11_DIR / "AegisBioWatch-MainBoard-PlacementSeed-r11-rebuilt.kicad_pro"
DEFAULT_R11_MANIFEST = DEFAULT_R11_DIR / "placement-seed-manifest-r11-rebuilt.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing required evidence: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-pcb", type=Path, default=DEFAULT_R11_PCB)
    ap.add_argument("--source-pro", type=Path, default=DEFAULT_R11_PRO)
    ap.add_argument("--source-manifest", type=Path, default=DEFAULT_R11_MANIFEST)
    ap.add_argument("--drc-summary", type=Path, required=True)
    ap.add_argument("--pin-net-audit", type=Path, required=True)
    args = ap.parse_args()

    for path in (args.source_pcb, args.source_pro, args.source_manifest):
        if not path.is_file():
            raise SystemExit(f"missing recovered r11 source: {path}")

    source_sha = sha256(args.source_pcb)
    manifest = load_json(args.source_manifest)
    if manifest.get("output_pcb_sha256") != source_sha:
        raise SystemExit(
            "recovered r11 manifest/PCB SHA mismatch: "
            f"manifest={manifest.get('output_pcb_sha256')} actual={source_sha}"
        )
    if manifest.get("components_r8") != 79 or manifest.get("footprints_imported") != 76:
        raise SystemExit("recovered r11 component/footprint invariant mismatch")
    if manifest.get("nets_r8") != 86 or manifest.get("net_nodes_r8") != 268:
        raise SystemExit("recovered r11 net/node invariant mismatch")

    drc = load_json(args.drc_summary)
    if drc.get("rule_violations") != 0 or drc.get("unconnected_items") != 186:
        raise SystemExit(
            "r13 source rejected by executed r11 DRC gate: "
            f"violations={drc.get('rule_violations')} unconnected={drc.get('unconnected_items')}"
        )

    audit = load_json(args.pin_net_audit)
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit(
            "r13 source rejected by recovered r11 pin/net gate: "
            f"result={audit.get('result')} nodes={audit.get('audited_present_source_nodes')}"
        )

    spec = importlib.util.spec_from_file_location("aegis_r13_base", BASE)
    if spec is None or spec.loader is None:
        raise SystemExit(f"unable to import r13 base materializer: {BASE}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Rebind the base algorithm to the freshly validated recovered source. The
    # base main() normally runs the broken historical r11 payload materializer;
    # that call is deliberately suppressed only after all evidence above passes.
    mod.R11_SCRIPT = ROOT / "tools/rebuild-pcb-r11-recovered.py"
    mod.R11_DIR = args.source_pcb.parent
    mod.R11_PCB = args.source_pcb
    mod.R11_PRO = args.source_pro
    mod.EXPECTED_R11_PCB_SHA256 = source_sha
    mod.runpy.run_path = lambda *a, **k: None

    mod.main()

    report = load_json(mod.R13_REPORT)
    if report.get("source_sha256") != source_sha:
        raise SystemExit("r13 report source SHA did not bind to validated recovered r11")
    if report.get("output_sha256") != sha256(mod.R13_PCB):
        raise SystemExit("r13 output/report SHA mismatch")

    report["source_lineage"] = "recovered_r8_topology_plus_r10_floorplan__kicad_9_0_9_validated_r11"
    report["source_manifest_sha256"] = sha256(args.source_manifest)
    report["source_drc_summary_sha256"] = sha256(args.drc_summary)
    report["source_pin_net_audit_sha256"] = sha256(args.pin_net_audit)
    report["source_gate"] = {
        "rule_violations": 0,
        "unconnected_items": 186,
        "pin_net_nodes": 268,
        "pin_net_result": "PASS",
    }
    report["authority_notice"] = (
        "Nordic nPM1300 reference layout/current-loop guidance remains physical authority; "
        "this transformation uses AegisBioWatch U2 pad geometry and functional adjacency only."
    )
    mod.R13_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("r13 recovered-source binding PASS")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
