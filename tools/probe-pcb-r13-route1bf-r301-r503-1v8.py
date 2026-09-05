#!/usr/bin/env python3
"""Read-only route-1bf geometry probe for R301.1/+1V8 -> R503.1/+1V8."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "hardware/main-board/pcb/route-r13-1be"
SRC_PCB = SRC_DIR / "AegisBioWatch-MainBoard-Route1be-r13.kicad_pcb"
SRC_REPORT = SRC_DIR / "routing-seed-r13-1be.json"

START = (3.005, 25.975)
END = (3.005, 27.475)
TRACK_WIDTH = 0.30
RULE_CLEARANCE = 0.10
ENVELOPE = (
    START[0] - TRACK_WIDTH / 2 - RULE_CLEARANCE,
    START[1] - RULE_CLEARANCE,
    START[0] + TRACK_WIDTH / 2 + RULE_CLEARANCE,
    END[1] + RULE_CLEARANCE,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mm(value: int) -> float:
    return float(pcbnew.ToMM(value))


def pxy(v) -> tuple[float, float]:
    return (round(mm(v.x), 6), round(mm(v.y), 6))


def bbox(item) -> tuple[float, float, float, float]:
    b = item.GetBoundingBox()
    return (
        round(mm(b.GetX()), 6),
        round(mm(b.GetY()), 6),
        round(mm(b.GetRight()), 6),
        round(mm(b.GetBottom()), 6),
    )


def intersects(a, b) -> bool:
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def pad(fp, number: str):
    ps = [p for p in fp.Pads() if str(p.GetNumber()) == number]
    if len(ps) != 1:
        raise SystemExit(f"{fp.GetReference()}.{number} cardinality gate failed: {len(ps)}")
    return ps[0]


def track_bbox(item) -> tuple[float, float, float, float]:
    a = pxy(item.GetStart())
    b = pxy(item.GetEnd())
    half = mm(item.GetWidth()) / 2.0
    return (
        min(a[0], b[0]) - half,
        min(a[1], b[1]) - half,
        max(a[0], b[0]) + half,
        max(a[1], b[1]) + half,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--route1be-drc-json", required=True)
    ap.add_argument("--route1be-pin-net-audit", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    report = load_json(SRC_REPORT)
    source_sha = sha256(SRC_PCB)
    if report.get("output_sha256") != source_sha:
        raise SystemExit("route1bf probe route1be report/PCB SHA mismatch")

    drc = load_json(Path(args.route1be_drc_json))
    audit = load_json(Path(args.route1be_pin_net_audit))
    if len(drc.get("violations", [])) != 0 or len(drc.get("unconnected_items", [])) != 118:
        raise SystemExit("route1bf probe route1be DRC gate failed")
    if audit.get("result") != "PASS" or audit.get("audited_present_source_nodes") != 268:
        raise SystemExit("route1bf probe route1be pin/net gate failed")

    board = pcbnew.LoadBoard(str(SRC_PCB))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    r301 = fps.get("R301")
    r503 = fps.get("R503")
    if r301 is None or r503 is None:
        raise SystemExit("route1bf probe missing R301/R503")

    if r301.GetValue() != "47k PU" or r503.GetValue() != "47k PU":
        raise SystemExit(f"route1bf probe value gate failed: R301={r301.GetValue()!r} R503={r503.GetValue()!r}")

    p301_1, p301_2 = pad(r301, "1"), pad(r301, "2")
    p503_1, p503_2 = pad(r503, "1"), pad(r503, "2")

    observed = {
        "R301.1": {"net": p301_1.GetNetname(), "position_mm": list(pxy(p301_1.GetPosition())), "bbox_mm": list(bbox(p301_1))},
        "R301.2": {"net": p301_2.GetNetname(), "position_mm": list(pxy(p301_2.GetPosition())), "bbox_mm": list(bbox(p301_2))},
        "R503.1": {"net": p503_1.GetNetname(), "position_mm": list(pxy(p503_1.GetPosition())), "bbox_mm": list(bbox(p503_1))},
        "R503.2": {"net": p503_2.GetNetname(), "position_mm": list(pxy(p503_2.GetPosition())), "bbox_mm": list(bbox(p503_2))},
    }

    expected = {
        "R301.1": ("+1V8", [3.005, 25.975]),
        "R301.2": ("FLASH_WP_N", [3.645, 25.975]),
        "R503.1": ("+1V8", [3.005, 27.475]),
        "R503.2": ("CHG_PRESENT_N", [3.645, 27.475]),
    }
    for key, (net, pos) in expected.items():
        if observed[key]["net"] != net or observed[key]["position_mm"] != pos:
            raise SystemExit(f"route1bf probe endpoint/net gate failed for {key}: {observed[key]}")

    blockers = []
    targets = {("R301", "1"), ("R503", "1")}
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if not p.IsOnLayer(pcbnew.F_Cu):
                continue
            key = (fp.GetReference(), str(p.GetNumber()))
            if key in targets:
                continue
            pb = bbox(p)
            if intersects(pb, ENVELOPE):
                blockers.append({
                    "kind": "pad",
                    "reference": fp.GetReference(),
                    "pad": str(p.GetNumber()),
                    "net": p.GetNetname(),
                    "bbox_mm": list(pb),
                })

    for item in board.GetTracks():
        net = item.GetNetname() if hasattr(item, "GetNetname") else ""
        if isinstance(item, pcbnew.PCB_VIA):
            vb = bbox(item)
            if intersects(vb, ENVELOPE):
                blockers.append({
                    "kind": "via",
                    "net": net,
                    "position_mm": list(pxy(item.GetPosition())),
                    "bbox_mm": list(vb),
                })
        else:
            if item.GetLayer() != pcbnew.F_Cu:
                continue
            tb = track_bbox(item)
            if intersects(tb, ENVELOPE):
                blockers.append({
                    "kind": "track",
                    "net": net,
                    "start_mm": list(pxy(item.GetStart())),
                    "end_mm": list(pxy(item.GetEnd())),
                    "width_mm": round(mm(item.GetWidth()), 6),
                    "bbox_mm": [round(v, 6) for v in tb],
                })

    candidate_right = START[0] + TRACK_WIDTH / 2.0
    signal_left = min(observed["R301.2"]["bbox_mm"][0], observed["R503.2"]["bbox_mm"][0])
    lateral_gap = round(signal_left - candidate_right, 6)

    out = {
        "revision": "r13-route1bf-r301-r503-1v8-geometry-probe",
        "source_route1be_sha256": source_sha,
        "source_gate": {"rule_violations": 0, "unconnected_items": 118, "pin_net_audit": "PASS", "audited_nodes": 268},
        "board_modified": False,
        "R301_value": r301.GetValue(),
        "R503_value": r503.GetValue(),
        "pads": observed,
        "candidate": {
            "start_mm": list(START),
            "end_mm": list(END),
            "track_width_mm": TRACK_WIDTH,
            "length_mm": 1.5,
            "rule_clearance_mm": RULE_CLEARANCE,
            "envelope_mm": list(ENVELOPE),
            "lateral_gap_to_signal_pad_column_mm": lateral_gap,
        },
        "blockers": blockers,
        "blocker_count": len(blockers),
        "release_status": "NOT_FOR_GERBER",
    }

    if lateral_gap < RULE_CLEARANCE:
        raise SystemExit(f"route1bf probe lateral gap gate failed: {lateral_gap} < {RULE_CLEARANCE}")
    if blockers:
        raise SystemExit("route1bf probe direct corridor blocked: " + json.dumps(blockers, indent=2))

    Path(args.output).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
