#!/usr/bin/env python3
"""Read-only 0.05 mm local refine for Issue #21 route-1bo +1V8 source track -> J8.1."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PCB = ROOT / "hardware/main-board/pcb/route-r13-1bn/AegisBioWatch-MainBoard-Route1bn-r13.kicad_pcb"
DEFAULT_REPORT = ROOT / "hardware/main-board/pcb/route-r13-1bn/routing-seed-r13-1bn.json"
ENGINE = ROOT / "tools/probe-pcb-r13-route1bm-max4-coarse.py"

TARGET_NET = "+1V8"
SOURCE_ENDPOINT = (10.305, 4.72)
SOURCE_TRACK_LENGTH_MM = 6.3650
J8_PAD1 = (12.105, 15.26)
COARSE_POINTS = [
    [10.305, 4.72],
    [9.75, 4.72],
    [9.75, 15.75],
    [12.105, 15.75],
    [12.105, 15.26],
]
GRID = 0.05
X_RANGE = (9.25, 10.25)
Y_RANGE = (15.25, 16.25)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mm(value) -> float:
    return float(pcbnew.ToMM(value))


def xy(v) -> tuple[float, float]:
    return (round(mm(v.x), 6), round(mm(v.y), 6))


def near(a: tuple[float, float], b: tuple[float, float], tol: float = 0.002) -> bool:
    return math.dist(a, b) <= tol


def item_pos(item: dict) -> tuple[float, float]:
    p = item.get("pos", {})
    return (float(p.get("x", 1e9)), float(p.get("y", 1e9)))


def get_pad(fp, number: str):
    pads = [p for p in fp.Pads() if str(p.GetNumber()) == str(number)]
    if len(pads) != 1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(pads)}")
    return pads[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--drc-json", required=True)
    ap.add_argument("--pin-net-audit", required=True)
    ap.add_argument("--source-pcb", default=str(DEFAULT_PCB))
    ap.add_argument("--source-report", default=str(DEFAULT_REPORT))
    ap.add_argument("--engine-output", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    source_pcb = Path(args.source_pcb)
    source_report = Path(args.source_report)
    report = load_json(source_report)
    source_sha = sha256(source_pcb)
    if report.get("output_sha256") != source_sha:
        raise SystemExit("route1bo J8 refine source report/PCB SHA gate failed")

    drc = load_json(Path(args.drc_json))
    audit = load_json(Path(args.pin_net_audit))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 110:
        raise SystemExit("route1bo J8 refine DRC source gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bo J8 refine audit source gate failed")
    if audit.get("mismatches", []) != [] or audit.get("unexpected_pad_nets", []) != []:
        raise SystemExit("route1bo J8 refine audit mismatch gate failed")

    matches = []
    for idx, u in enumerate(drc.get("unconnected_items", [])):
        items = u.get("items", [])
        if len(items) != 2:
            continue
        has_source = any(
            x.get("description", "").startswith("Track [+1V8] on Top_layer")
            and near(item_pos(x), SOURCE_ENDPOINT)
            for x in items
        )
        has_target = any(
            x.get("description", "") == "Pad 1 [+1V8] of J8 on Top_layer"
            and near(item_pos(x), J8_PAD1)
            for x in items
        )
        if has_source and has_target:
            matches.append(idx)
    if len(matches) != 1:
        raise SystemExit(f"route1bo J8 refine exact ratsnest identity gate failed: {matches}")
    drc_index = matches[0]

    board = pcbnew.LoadBoard(str(source_pcb))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    j8 = fps.get("J8")
    if j8 is None:
        raise SystemExit("route1bo J8 refine missing J8")
    p1 = get_pad(j8, "1")
    if (p1.GetNetname(), xy(p1.GetPosition())) != (TARGET_NET, J8_PAD1):
        raise SystemExit("route1bo J8.1 identity/net/position gate failed")

    blank_pads = []
    for p in j8.Pads():
        if str(p.GetNumber()) != "":
            continue
        drill = p.GetDrillSize()
        blank_pads.append({
            "number": "",
            "net": p.GetNetname(),
            "position_mm": list(xy(p.GetPosition())),
            "size_mm": [round(mm(p.GetSize().x), 6), round(mm(p.GetSize().y), 6)],
            "drill_mm": [round(mm(drill.x), 6), round(mm(drill.y), 6)],
            "attribute": str(p.GetAttribute()),
            "on_fcu": bool(p.IsOnLayer(pcbnew.F_Cu)),
        })
    if not blank_pads:
        raise SystemExit("route1bo J8 refine expected mechanical blank pads were not found")
    if any(p["net"] != "" for p in blank_pads):
        raise SystemExit(f"route1bo J8 blank-pad net gate failed: {blank_pads}")

    source_tracks = []
    for item in board.GetTracks():
        if isinstance(item, pcbnew.PCB_VIA) or item.GetLayer() != pcbnew.F_Cu:
            continue
        if item.GetNetname() != TARGET_NET:
            continue
        start, end = xy(item.GetStart()), xy(item.GetEnd())
        length = mm(item.GetLength())
        if (near(start, SOURCE_ENDPOINT) or near(end, SOURCE_ENDPOINT)) and abs(length - SOURCE_TRACK_LENGTH_MM) <= 0.002:
            source_tracks.append({
                "start_mm": list(start),
                "end_mm": list(end),
                "length_mm": round(length, 6),
                "width_mm": round(mm(item.GetWidth()), 6),
                "net": item.GetNetname(),
                "layer": "F.Cu",
            })
    if len(source_tracks) != 1:
        raise SystemExit(f"route1bo J8 refine exact source-track gate failed: {source_tracks}")

    engine_output = Path(args.engine_output)
    cmd = [
        sys.executable,
        str(ENGINE),
        "--drc-json", args.drc_json,
        "--pin-net-audit", args.pin_net_audit,
        "--source-pcb", str(source_pcb),
        "--source-report", str(source_report),
        "--expected-unconnected", "110",
        "--grid-mm", str(GRID),
        "--only-drc-index", str(drc_index),
        "--only-path-family", "HVHV",
        "--lane-x-min", str(X_RANGE[0]),
        "--lane-x-max", str(X_RANGE[1]),
        "--lane-y-min", str(Y_RANGE[0]),
        "--lane-y-max", str(Y_RANGE[1]),
        "--output", str(engine_output),
    ]
    subprocess.run(cmd, check=True)

    engine = load_json(engine_output)
    expected_gate = {
        "rule_violations": 0,
        "unconnected_items": 110,
        "pin_net_audit": "PASS",
        "audited_nodes": 268,
    }
    if engine.get("source_gate") != expected_gate or engine.get("board_modified") is not False:
        raise SystemExit("route1bo J8 refine engine source/board gate failed")
    candidates = engine.get("passing_candidates", [])
    if len(candidates) != 1:
        raise SystemExit(f"route1bo J8 refine candidate cardinality gate failed: {len(candidates)}")
    candidate = candidates[0]
    if candidate.get("net") != TARGET_NET or candidate.get("drc_index") != drc_index:
        raise SystemExit("route1bo J8 refine engine candidate identity gate failed")
    if candidate.get("a", {}).get("pos") != list(SOURCE_ENDPOINT):
        raise SystemExit("route1bo J8 refine engine source endpoint moved")
    if candidate.get("b", {}).get("ref") != "J8" or candidate.get("b", {}).get("pad") != "1":
        raise SystemExit("route1bo J8 refine engine target endpoint changed")
    if candidate.get("b", {}).get("pos") != list(J8_PAD1):
        raise SystemExit("route1bo J8 refine engine target position moved")
    if candidate.get("passing_path_count", 0) < 1:
        raise SystemExit("route1bo J8 refine found no legal local HVHV path")

    best = candidate.get("best_passing_path")
    if best is None or best.get("path_family") != "HVHV":
        raise SystemExit("route1bo J8 refine best-path gate failed")
    if best.get("minimum_conservative_clearance_mm", -1) + 1e-9 < 0.1:
        raise SystemExit("route1bo J8 refine clearance gate failed")

    nearest = best.get("nearest_unrelated_copper") or {}
    blank_pad_context = {
        "coarse_nearest_was_numberless_j8_pad": True,
        "j8_numberless_pads": blank_pads,
        "refined_nearest_unrelated_copper": nearest,
        "resolution": "Numberless J8 pads are explicitly enumerated from the reproduced route-1bn footprint; the refined route remains above the unchanged 0.100 mm conservative clearance gate.",
    }

    out = {
        "revision": "r13-route1bo-j8-1v8-local-refine",
        "issue": 21,
        "source_route1bn_sha256": source_sha,
        "source_gate": expected_gate,
        "board_modified": False,
        "semantic_selection": {
            "selected_family": "+1V8 source track -> J8.1/+1V8 HVHV",
            "selection_reason": "The route-1bo Phase A1 screen evaluated 110 current ratsnest items after frozen/deferred exclusions and produced exactly one passing ordinary candidate. This refine explicitly resolves the prior numberless-J8-pad context before any copper is materialized.",
            "coarse_anchor_points_mm": COARSE_POINTS,
            "coarse_minimum_conservative_clearance_mm": 0.4397,
        },
        "exact_identity": {
            "actual_drc_index": drc_index,
            "source_track_endpoint_mm": list(SOURCE_ENDPOINT),
            "source_track_expected_length_mm": SOURCE_TRACK_LENGTH_MM,
            "source_track": source_tracks[0],
            "J8_value": j8.GetValue(),
            "J8_pad1": {"net": p1.GetNetname(), "position_mm": list(xy(p1.GetPosition()))},
        },
        "blank_pad_context": blank_pad_context,
        "refine": {
            "track_width_mm": engine.get("track_width_mm"),
            "rule_clearance_mm": engine.get("rule_clearance_mm"),
            "grid_mm": engine.get("grid_mm"),
            "lane_x_range_mm": engine.get("lane_x_range_mm"),
            "lane_y_range_mm": engine.get("lane_y_range_mm"),
            "path_family": "HVHV",
            "candidate_path_count": candidate.get("path_count"),
            "passing_path_count": candidate.get("passing_path_count"),
            "best_passing_path": best,
            "top_passing_paths": candidate.get("top_passing_paths", []),
        },
        "decision_state": {
            "phase_a1_complete": True,
            "phase_a2_refine_complete": True,
            "candidate_selected_for_phase_b": False,
            "phase_b_started": False,
            "accepted_authority_changed": False,
            "next_action": "Review the refined winner and J8 numberless-pad evidence; only then create an exact Phase B probe/materializer for one documented path.",
        },
        "release_status": "NOT_FOR_GERBER",
    }
    Path(args.output).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
