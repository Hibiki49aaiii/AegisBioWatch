#!/usr/bin/env python3
"""Create route-1 copper from the executed recovered-source r13 placement.

This adapter deliberately reuses the existing narrow route-1 copper algorithm
(SW1/SW2, local VOUT, VSYS input decoupling, PVSS local-return trees and
NetTie->GND escape vias) but replaces its obsolete historical-r11/r13 evidence
loader with the executed recovered-source placement gate.

The adapter refuses to run unless the exact current r13 placement has:
- KiCad 9.0.9 placement DRC: 0 rule violations / 186 unconnected items;
- physical-pad pin/net audit: 268 / 268 PASS;
- placement report SHA matching the PCB being routed.

No RF routing or supplier-gated J3/J5/J6 interfaces are touched. Track widths
and via geometry remain routing-seed values, not fabrication authority.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tools/materialize-pcb-r13-route1.py"
PLACEMENT_PCB = ROOT / "hardware/main-board/pcb/placement-r13/AegisBioWatch-MainBoard-Placement-r13.kicad_pcb"
PLACEMENT_PRO = ROOT / "hardware/main-board/pcb/placement-r13/AegisBioWatch-MainBoard-Placement-r13.kicad_pro"
PLACEMENT_REPORT = ROOT / "hardware/main-board/pcb/placement-r13/placement-implementation-r13.json"
ROUTE_REPORT = ROOT / "hardware/main-board/pcb/route-r13-1/routing-seed-r13-1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"required route-1 source evidence missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--placement-drc-json", type=Path, required=True)
    ap.add_argument("--placement-pin-net-audit", type=Path, required=True)
    ap.add_argument("--kicad-cli-version", default="9.0.9")
    args = ap.parse_args()

    for p in (PLACEMENT_PCB, PLACEMENT_PRO, PLACEMENT_REPORT):
        if not p.is_file():
            raise SystemExit(f"current r13 placement source missing: {p}")

    placement_sha = sha256(PLACEMENT_PCB)
    placement_report = load_json(PLACEMENT_REPORT)
    if placement_report.get("output_sha256") != placement_sha:
        raise SystemExit(
            "route-1 source rejected: placement report/PCB SHA mismatch: "
            f"report={placement_report.get('output_sha256')} actual={placement_sha}"
        )
    if placement_report.get("source_gate") != {
        "rule_violations": 0,
        "unconnected_items": 186,
        "pin_net_nodes": 268,
        "pin_net_result": "PASS",
    }:
        raise SystemExit(f"route-1 source rejected: unexpected placement source gate {placement_report.get('source_gate')}")
    if placement_report.get("moved_ref_count") != 24:
        raise SystemExit("route-1 source rejected: r13 PMIC placement completeness changed")
    if placement_report.get("non_pmic_seed_refs_moved") != []:
        raise SystemExit("route-1 source rejected: non-PMIC seed refs unexpectedly moved")

    raw_drc = args.placement_drc_json.read_bytes()
    drc = json.loads(raw_drc)
    violations = drc.get("violations")
    unconnected = drc.get("unconnected_items")
    if not isinstance(violations, list) or not isinstance(unconnected, list):
        raise SystemExit("route-1 source rejected: unexpected KiCad DRC JSON schema")
    if len(violations) != 0 or len(unconnected) != 186:
        raise SystemExit(
            f"route-1 source rejected by executed DRC: violations={len(violations)} unconnected={len(unconnected)}"
        )

    audit = load_json(args.placement_pin_net_audit)
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit(
            "route-1 source rejected by physical-pad audit: "
            f"result={audit.get('result')} nodes={audit.get('audited_present_source_nodes')}"
        )

    if "9.0.9" not in args.kicad_cli_version:
        raise SystemExit(f"route-1 requires KiCad 9.0.9 evidence, got {args.kicad_cli_version!r}")

    spec = importlib.util.spec_from_file_location("aegis_route1_base", BASE)
    if spec is None or spec.loader is None:
        raise SystemExit(f"unable to load route-1 base algorithm: {BASE}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # The current r13 placement is already materialized and executed-evidence
    # validated above. Prevent the historical route-1 helper from invoking the
    # obsolete placement materializer or requiring its old packaged-result file.
    mod.load_placement_module = lambda: SimpleNamespace(main=lambda: None)
    mod.PLACEMENT_RESULT = PLACEMENT_REPORT
    mod.require_exact_validated_placement = lambda: {
        "output_pcb_sha256": placement_sha,
        "drc_json_sha256": hashlib.sha256(raw_drc).hexdigest(),
        "rule_violations": 0,
        "unconnected_items": 186,
        "kicad_cli": args.kicad_cli_version,
        "evidence": "EXECUTED_KICAD_CLI_RECOVERED_R13",
    }

    mod.main()

    report = load_json(ROUTE_REPORT)
    if report.get("source_placement_sha256") != placement_sha:
        raise SystemExit("route-1 report is not bound to the validated r13 placement SHA")
    if report.get("rf_routing_touched") is not False or report.get("supplier_gated_interfaces_touched") is not False:
        raise SystemExit("route-1 scope guard failed")

    report["source_lineage"] = "recovered_r8+r10 -> KiCad-validated r11 -> collision-aware r13 placement"
    report["source_placement_report_sha256"] = sha256(PLACEMENT_REPORT)
    report["source_placement_drc_json_sha256"] = hashlib.sha256(raw_drc).hexdigest()
    report["source_placement_pin_net_audit_sha256"] = sha256(args.placement_pin_net_audit)
    report["source_placement_physical_pad_audit"] = {"result": "PASS", "nodes": 268}
    report["routing_stage"] = "STARTED_PMICS_ONLY"
    report["validation_status"] = "PENDING_EXECUTED_KICAD_ROUTE_DRC"
    report["privacy_boundary"] = "engineering_abstractions_only"
    ROUTE_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("route-1 recovered-source binding PASS")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
