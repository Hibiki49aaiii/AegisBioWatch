#!/usr/bin/env python3
"""Read-only 0.05 mm local refine for Issue #20 route-1bn +1V8 source track -> R403.1."""
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
DEFAULT_PCB = ROOT / "hardware/main-board/pcb/route-r13-1bm/AegisBioWatch-MainBoard-Route1bm-r13.kicad_pcb"
DEFAULT_REPORT = ROOT / "hardware/main-board/pcb/route-r13-1bm/routing-seed-r13-1bm.json"
ENGINE = ROOT / "tools/probe-pcb-r13-route1bm-max4-coarse.py"

TARGET_NET = "+1V8"
SOURCE_ENDPOINT = (41.005, 14.975)
SOURCE_TRACK_LENGTH_MM = 4.6628
R403_PAD1 = (40.255, 25.975)
R403_PAD2 = (40.895, 25.975)
COARSE_POINTS = [
    [41.005, 14.975],
    [41.005, 15.75],
    [39.5, 15.75],
    [39.5, 25.975],
    [40.255, 25.975],
]
GRID = 0.05
X_RANGE = (39.0, 40.0)
Y_RANGE = (15.25, 16.25)
EPS = 1e-9


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
        raise SystemExit("route1bn R403 refine source report/PCB SHA gate failed")

    drc = load_json(Path(args.drc_json))
    audit = load_json(Path(args.pin_net_audit))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 111:
        raise SystemExit("route1bn R403 refine DRC source gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bn R403 refine audit source gate failed")
    if audit.get("mismatches", []) != [] or audit.get("unexpected_pad_nets", []) != []:
        raise SystemExit("route1bn R403 refine audit mismatch gate failed")

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
            x.get("description", "") == "Pad 1 [+1V8] of R403 on Top_layer"
            and near(item_pos(x), R403_PAD1)
            for x in items
        )
        if has_source and has_target:
            matches.append(idx)
    if len(matches) != 1:
        raise SystemExit(f"route1bn R403 refine exact ratsnest identity gate failed: {matches}")
    drc_index = matches[0]

    board = pcbnew.LoadBoard(str(source_pcb))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    r403 = fps.get("R403")
    if r403 is None:
        raise SystemExit("route1bn R403 refine missing R403")
    p1 = get_pad(r403, "1")
    p2 = get_pad(r403, "2")
    if (p1.GetNetname(), xy(p1.GetPosition())) != (TARGET_NET, R403_PAD1):
        raise SystemExit("route1bn R403.1 identity/net/position gate failed")
    if (p2.GetNetname(), xy(p2.GetPosition())) != ("SYS_I2C_SDA", R403_PAD2):
        raise SystemExit("route1bn R403.2 identity/net/position gate failed")

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
        raise SystemExit(f"route1bn R403 refine exact source-track gate failed: {source_tracks}")

    engine_output = Path(args.engine_output)
    cmd = [
        sys.executable,
        str(ENGINE),
        "--drc-json", args.drc_json,
        "--pin-net-audit", args.pin_net_audit,
        "--source-pcb", str(source_pcb),
        "--source-report", str(source_report),
        "--expected-unconnected", "111",
        "--grid-mm", str(GRID),
        "--only-drc-index", str(drc_index),
        "--only-path-family", "VHVH",
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
        "unconnected_items": 111,
        "pin_net_audit": "PASS",
        "audited_nodes": 268,
    }
    if engine.get("source_gate") != expected_gate or engine.get("board_modified") is not False:
        raise SystemExit("route1bn R403 refine engine source/board gate failed")
    candidates = engine.get("passing_candidates", [])
    if len(candidates) != 1:
        raise SystemExit(f"route1bn R403 refine candidate cardinality gate failed: {len(candidates)}")
    candidate = candidates[0]
    if candidate.get("net") != TARGET_NET or candidate.get("drc_index") != drc_index:
        raise SystemExit("route1bn R403 refine engine candidate identity gate failed")
    if candidate.get("a", {}).get("pos") != list(SOURCE_ENDPOINT):
        raise SystemExit("route1bn R403 refine engine source endpoint moved")
    if candidate.get("b", {}).get("ref") != "R403" or candidate.get("b", {}).get("pad") != "1":
        raise SystemExit("route1bn R403 refine engine target endpoint changed")
    if candidate.get("b", {}).get("pos") != list(R403_PAD1):
        raise SystemExit("route1bn R403 refine engine target position moved")
    if candidate.get("passing_path_count", 0) < 1:
        raise SystemExit("route1bn R403 refine found no legal local VHVH path")

    best = candidate.get("best_passing_path")
    if best is None or best.get("path_family") != "VHVH":
        raise SystemExit("route1bn R403 refine best-path gate failed")
    if best.get("minimum_conservative_clearance_mm", -1) + 1e-9 < 0.1:
        raise SystemExit("route1bn R403 refine clearance gate failed")

    out = {
        "revision": "r13-route1bn-r403-1v8-local-refine",
        "issue": 20,
        "source_route1bm_sha256": source_sha,
        "source_gate": expected_gate,
        "board_modified": False,
        "semantic_selection": {
            "selected_family": "+1V8 source track -> R403.1/+1V8 VHVH",
            "selection_reason": "Current route-1bm full screen has only J8 and R403 numerical passes; J8 remains held for unresolved blank-pad context. R403 is an ordinary +1V8 closure and this four-segment family is distinct from the rejected 0.099999 mm three-segment route.",
            "coarse_anchor_points_mm": COARSE_POINTS,
            "coarse_minimum_conservative_clearance_mm": 0.26,
            "alternate_j8_status": "HOLD_NOT_SELECTED",
        },
        "exact_identity": {
            "actual_drc_index": drc_index,
            "source_track_endpoint_mm": list(SOURCE_ENDPOINT),
            "source_track_expected_length_mm": SOURCE_TRACK_LENGTH_MM,
            "source_track": source_tracks[0],
            "R403_value": r403.GetValue(),
            "R403_pad1": {"net": p1.GetNetname(), "position_mm": list(xy(p1.GetPosition()))},
            "R403_pad2": {"net": p2.GetNetname(), "position_mm": list(xy(p2.GetPosition()))},
        },
        "refine": {
            "track_width_mm": engine.get("track_width_mm"),
            "rule_clearance_mm": engine.get("rule_clearance_mm"),
            "grid_mm": engine.get("grid_mm"),
            "lane_x_range_mm": engine.get("lane_x_range_mm"),
            "lane_y_range_mm": engine.get("lane_y_range_mm"),
            "path_family": "VHVH",
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
            "next_action": "Review the refined winner; only then create an exact Phase B probe/materializer for one documented path.",
        },
        "release_status": "NOT_FOR_GERBER",
    }
    Path(args.output).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
