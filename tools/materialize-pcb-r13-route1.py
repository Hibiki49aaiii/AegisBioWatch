#!/usr/bin/env python3
"""Create the r13 route-1 PMIC critical-loop routing seed.

Route-1 is deliberately narrow in scope:
  * SW1 / SW2 package-to-inductor connections
  * BUCK VOUT1 / VOUT2 local output nodes and first output capacitors
  * VSYS local input-cap distribution at U2
  * PVSS1/PVSS2 local return trees to their explicit NetTies
  * short GND escape from each NetTie to a provisional through-via

The script refuses to route unless the freshly materialized r13 placement is
byte-for-byte the PCB that an executed KiCad 9.0.9 placement DRC validated.
It does not touch U1 RF/crystal routing or unresolved supplier interfaces.

Track/via syntax follows KiCad's board S-expression format. Widths and via
geometry here are routing-seed values, not manufacturing authority. KiCad DRC
must be run again on the generated route-1 board.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACEMENT_SCRIPT = ROOT / "tools/materialize-pcb-r13.py"
PLACEMENT_DIR = ROOT / "hardware/main-board/pcb/placement-r13"
PLACEMENT_PCB = PLACEMENT_DIR / "AegisBioWatch-MainBoard-Placement-r13.kicad_pcb"
PLACEMENT_PRO = PLACEMENT_DIR / "AegisBioWatch-MainBoard-Placement-r13.kicad_pro"
PLACEMENT_REPORT = PLACEMENT_DIR / "placement-implementation-r13.json"
PLACEMENT_RESULT = ROOT / "docs/pcb-placement-implementation-r13-kicad-result.json"
DRC_JSON = Path(os.environ.get("R13_PLACEMENT_DRC_JSON", "/tmp/drc-r13.json"))
OUT_DIR = ROOT / "hardware/main-board/pcb/route-r13-1"
OUT_PCB = OUT_DIR / "AegisBioWatch-MainBoard-Route1-r13.kicad_pcb"
OUT_PRO = OUT_DIR / "AegisBioWatch-MainBoard-Route1-r13.kicad_pro"
OUT_REPORT = OUT_DIR / "routing-seed-r13-1.json"

UUID_NAMESPACE = uuid.UUID("3359a474-2c66-4e1d-af80-f4307c7a9393")

# Routing-seed geometry only. Final geometry remains gated by fab/current/
# thermal/DFM closure.
WIDTH_SW_MM = 0.25
WIDTH_VSYS_MM = 0.30
WIDTH_PVSS_MM = 0.35
WIDTH_VOUT_MM = 0.35
WIDTH_GND_ESCAPE_MM = 0.30
VIA_SIZE_MM = 0.60
VIA_DRILL_MM = 0.30
VIA_ESCAPE_MM = 0.55


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_placement_module():
    spec = importlib.util.spec_from_file_location("aegis_r13_placement", PLACEMENT_SCRIPT)
    if spec is None or spec.loader is None:
        raise SystemExit("unable to load r13 placement materializer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_exact_validated_placement() -> dict:
    """Bind route-1 to the exact PCB and DRC JSON recorded by the packager."""
    for path in (PLACEMENT_PCB, PLACEMENT_REPORT, PLACEMENT_RESULT, DRC_JSON):
        if not path.exists():
            raise SystemExit(f"required executed placement evidence missing: {path}")

    raw_drc = DRC_JSON.read_bytes()
    drc = json.loads(raw_drc)
    violations = drc.get("violations")
    unconnected = drc.get("unconnected_items")
    if not isinstance(violations, list) or not isinstance(unconnected, list):
        raise SystemExit("unexpected KiCad placement DRC JSON schema")
    if violations:
        raise SystemExit(f"placement DRC has {len(violations)} rule violations; route-1 blocked")
    if len(unconnected) != 186:
        raise SystemExit(
            f"placement-only unconnected baseline changed: expected 186, got {len(unconnected)}; route-1 blocked"
        )

    result = json.loads(PLACEMENT_RESULT.read_text(encoding="utf-8"))
    if result.get("evidence") != "EXECUTED_KICAD_CLI":
        raise SystemExit("placement result is not executed KiCad CLI evidence")
    if result.get("rule_violations") != 0 or result.get("unconnected_items") != 186:
        raise SystemExit("packaged placement result does not match required 0/186 gate")
    if "9.0.9" not in str(result.get("kicad_cli", "")):
        raise SystemExit(f"placement evidence is not KiCad 9.0.9: {result.get('kicad_cli')!r}")

    actual_pcb_sha = sha256(PLACEMENT_PCB)
    actual_drc_sha = hashlib.sha256(raw_drc).hexdigest()
    if result.get("output_pcb_sha256") != actual_pcb_sha:
        raise SystemExit(
            "stale placement evidence: validated PCB SHA does not match freshly materialized r13 placement"
        )
    if result.get("drc_json_sha256") != actual_drc_sha:
        raise SystemExit("stale/tampered placement evidence: DRC JSON SHA mismatch")

    return result


def balanced_blocks(text: str, token: str):
    needle = f"({token}"
    start = 0
    while True:
        i = text.find(needle, start)
        if i < 0:
            return
        depth = 0
        in_string = False
        escaped = False
        for j in range(i, len(text)):
            ch = text[j]
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    yield text[i:j + 1]
                    start = j + 1
                    break
        else:
            raise RuntimeError(f"unterminated {token} block at offset {i}")


def reference(block: str) -> str | None:
    for pat in (
        r'\(property\s+"Reference"\s+"([^"]+)"',
        r'\(fp_text\s+reference\s+"?([^"\s\)]+)"?',
    ):
        m = re.search(pat, block)
        if m:
            return m.group(1)
    return None


def footprint_at(block: str) -> tuple[float, float, float]:
    m = re.search(r"\n\s*\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)(?:\s+(-?[0-9.]+))?\)", block)
    if not m:
        raise ValueError("footprint has no top-level at")
    return float(m.group(1)), float(m.group(2)), float(m.group(3) or 0.0)


def rotate(v: tuple[float, float], deg: float) -> tuple[float, float]:
    r = math.radians(deg)
    return (
        v[0] * math.cos(r) - v[1] * math.sin(r),
        v[0] * math.sin(r) + v[1] * math.cos(r),
    )


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def mul(a, k):
    return a[0] * k, a[1] * k


def norm(v):
    d = math.hypot(v[0], v[1])
    if d < 1e-9:
        raise ValueError("zero-length vector")
    return v[0] / d, v[1] / d


def pad_records(block: str) -> list[dict]:
    fx, fy, fa = footprint_at(block)
    result = []
    for pad in balanced_blocks(block, "pad"):
        pm = re.match(r'\(pad\s+"?([^"\s]+)"?', pad)
        if not pm:
            continue
        am = re.search(r"\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)(?:\s+(-?[0-9.]+))?\)", pad)
        if not am:
            continue
        local = (float(am.group(1)), float(am.group(2)))
        nm = re.search(r'\(net\s+([0-9]+)\s+"([^"]*)"\)', pad)
        result.append(
            {
                "pad": pm.group(1),
                "net_id": int(nm.group(1)) if nm else None,
                "net": nm.group(2) if nm else None,
                "abs": add((fx, fy), rotate(local, fa)),
            }
        )
    return result


def build_index(text: str) -> dict[str, str]:
    out = {}
    for block in balanced_blocks(text, "footprint"):
        ref = reference(block)
        if ref:
            out[ref] = block
    return out


def pad_by_number(index: dict[str, str], ref: str, pad: str) -> dict:
    matches = [p for p in pad_records(index[ref]) if p["pad"] == pad]
    if len(matches) != 1:
        raise ValueError(f"{ref} pad {pad}: expected one match, got {len(matches)}")
    return matches[0]


def pad_by_net(index: dict[str, str], ref: str, net: str) -> dict:
    matches = [p for p in pad_records(index[ref]) if p["net"] == net]
    if len(matches) != 1:
        raise ValueError(f"{ref} net {net}: expected one pad, got {len(matches)}")
    return matches[0]


def same_net(*pads: dict) -> tuple[int, str]:
    ids = {p["net_id"] for p in pads}
    names = {p["net"] for p in pads}
    if len(ids) != 1 or len(names) != 1 or None in ids:
        raise ValueError(f"net disagreement: {pads}")
    return pads[0]["net_id"], pads[0]["net"]


def deterministic_id(kind: str, label: str) -> str:
    return str(uuid.uuid5(UUID_NAMESPACE, f"{kind}:{label}"))


def segment(a, b, width: float, net_id: int, label: str) -> str:
    if math.hypot(b[0] - a[0], b[1] - a[1]) < 0.01:
        raise ValueError(f"degenerate segment {label}")
    return (
        "  (segment\n"
        f"    (start {a[0]:.4f} {a[1]:.4f})\n"
        f"    (end {b[0]:.4f} {b[1]:.4f})\n"
        f"    (width {width:.3f})\n"
        '    (layer "F.Cu")\n'
        f"    (net {net_id})\n"
        f"    (tstamp {deterministic_id('segment', label)})\n"
        "  )\n"
    )


def via(at, net_id: int, label: str) -> str:
    return (
        "  (via\n"
        f"    (at {at[0]:.4f} {at[1]:.4f})\n"
        f"    (size {VIA_SIZE_MM:.3f})\n"
        f"    (drill {VIA_DRILL_MM:.3f})\n"
        '    (layers "F.Cu" "B.Cu")\n'
        f"    (net {net_id})\n"
        f"    (tstamp {deterministic_id('via', label)})\n"
        "  )\n"
    )


def mst_edges(named_points: list[tuple[str, tuple[float, float]]]):
    """Euclidean MST for a tiny same-net local-return set."""
    if len(named_points) < 2:
        return []
    used = {0}
    edges = []
    while len(used) < len(named_points):
        best = None
        for i in used:
            for j in range(len(named_points)):
                if j in used:
                    continue
                pi = named_points[i][1]
                pj = named_points[j][1]
                d = math.hypot(pi[0] - pj[0], pi[1] - pj[1])
                candidate = (d, i, j)
                if best is None or candidate < best:
                    best = candidate
        assert best is not None
        _, i, j = best
        used.add(j)
        edges.append((named_points[i], named_points[j]))
    return edges


def append_tracks(board_text: str, objects: list[str]) -> str:
    pos = board_text.rfind(")")
    if pos < 0:
        raise ValueError("invalid board: no final close parenthesis")
    return board_text[:pos] + "\n" + "".join(objects) + board_text[pos:]


def main():
    # Generate the placement first, then prove that the executed KiCad evidence
    # belongs to exactly this generated PCB before adding any copper.
    placement = load_placement_module()
    placement.main()
    if not PLACEMENT_PCB.exists() or not PLACEMENT_REPORT.exists():
        raise SystemExit("r13 placement materializer did not produce expected files")
    placement_evidence = require_exact_validated_placement()

    text = PLACEMENT_PCB.read_text(encoding="utf-8")
    index = build_index(text)
    required = {"U2", "L101", "L102", "C103", "C104", "C107", "C108", "C114", "NT101", "NT102"}
    missing = sorted(required - set(index))
    if missing:
        raise SystemExit(f"route-1 missing required footprints: {missing}")

    objects: list[str] = []
    routed: list[dict] = []
    segment_count = 0

    def connect(a: dict, b: dict, width: float, label: str):
        nonlocal segment_count
        net_id, net_name = same_net(a, b)
        objects.append(segment(a["abs"], b["abs"], width, net_id, label))
        segment_count += 1
        routed.append({"label": label, "net": net_name, "width_mm": width})

    # Highest-di/dt switch nodes: one direct seed segment each.
    connect(pad_by_number(index, "U2", "3"), pad_by_net(index, "L101", "PMIC_SW1"), WIDTH_SW_MM, "SW1_U2_L101")
    connect(pad_by_number(index, "U2", "5"), pad_by_net(index, "L102", "PMIC_SW2"), WIDTH_SW_MM, "SW2_U2_L102")

    # Complete each regulated output node locally: inductor -> output cap ->
    # nPM1300 VOUT pin. VOUT1 is pin 1; VOUT2 is pin 32 in QFN32.
    c107_vout = pad_by_net(index, "C107", "+1V8")
    c108_vout = pad_by_net(index, "C108", "+3V0")
    connect(pad_by_net(index, "L101", "+1V8"), c107_vout, WIDTH_VOUT_MM, "BUCK1_L101_C107")
    connect(c107_vout, pad_by_number(index, "U2", "1"), WIDTH_VOUT_MM, "BUCK1_C107_U2_VOUT1")
    connect(pad_by_net(index, "L102", "+3V0"), c108_vout, WIDTH_VOUT_MM, "BUCK2_L102_C108")
    connect(c108_vout, pad_by_number(index, "U2", "32"), WIDTH_VOUT_MM, "BUCK2_C108_U2_VOUT2")

    # Local VSYS/PVDD input network.
    u2_vsys = pad_by_number(index, "U2", "4")
    for ref in ("C103", "C104", "C114"):
        connect(u2_vsys, pad_by_net(index, ref, "VSYS"), WIDTH_VSYS_MM, f"VSYS_U2_{ref}")

    # Compact local switching-return tree for each BUCK.
    for suffix, pin, refs in (
        ("PVSS1_LOCAL", "2", ("C103", "C107", "NT101")),
        ("PVSS2_LOCAL", "6", ("C104", "C108", "NT102")),
    ):
        pads = [(f"U2.{pin}", pad_by_number(index, "U2", pin))]
        pads.extend((ref, pad_by_net(index, ref, suffix)) for ref in refs)
        same_net(*(p for _, p in pads))
        net_id = pads[0][1]["net_id"]
        for (name_a, a), (name_b, b) in mst_edges([(name, p["abs"]) for name, p in pads]):
            label = f"{suffix}_{name_a}_{name_b}"
            objects.append(segment(a, b, WIDTH_PVSS_MM, net_id, label))
            segment_count += 1
            routed.append({"label": label, "net": suffix, "width_mm": WIDTH_PVSS_MM})

    # NetTie GND-side escape to a provisional through-via. In1.Cu remains the
    # one continuous GND plane; these vias do not define a star/split plane.
    u2_center = footprint_at(index["U2"])[0:2]
    vias = []
    for nt in ("NT101", "NT102"):
        g = pad_by_net(index, nt, "GND")
        outward = norm(sub(g["abs"], u2_center))
        via_at = add(g["abs"], mul(outward, VIA_ESCAPE_MM))
        label = f"{nt}_GND_escape"
        objects.append(segment(g["abs"], via_at, WIDTH_GND_ESCAPE_MM, g["net_id"], label))
        segment_count += 1
        objects.append(via(via_at, g["net_id"], f"{nt}_GND_via"))
        routed.append({"label": label, "net": "GND", "width_mm": WIDTH_GND_ESCAPE_MM})
        vias.append(
            {
                "label": f"{nt}_GND_via",
                "at_mm": [round(via_at[0], 4), round(via_at[1], 4)],
                "size_mm": VIA_SIZE_MM,
                "drill_mm": VIA_DRILL_MM,
            }
        )

    out_text = append_tracks(text, objects)
    if out_text.count("(") != out_text.count(")"):
        raise SystemExit("route-1 PCB parenthesis balance failed")

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    OUT_PCB.write_text(out_text, encoding="utf-8")
    shutil.copy2(PLACEMENT_PRO, OUT_PRO)

    report = {
        "revision": "r13-route1-npm1300-critical-loops",
        "source_placement": str(PLACEMENT_PCB.relative_to(ROOT)),
        "source_placement_sha256": sha256(PLACEMENT_PCB),
        "validated_placement_result": str(PLACEMENT_RESULT.relative_to(ROOT)),
        "validated_placement_drc_sha256": placement_evidence["drc_json_sha256"],
        "placement_gate": {"rule_violations": 0, "unconnected_items": 186, "kicad_cli": placement_evidence["kicad_cli"]},
        "output": str(OUT_PCB.relative_to(ROOT)),
        "output_sha256": sha256(OUT_PCB),
        "track_segments_added": segment_count,
        "vias_added": len(vias),
        "routed_objects": routed,
        "vias": vias,
        "rf_routing_touched": False,
        "supplier_gated_interfaces_touched": False,
        "geometry_status": "ROUTING_SEED_NOT_MANUFACTURING_AUTHORITY",
        "validation_authority": "Run KiCad 9.0.9 pcb drc on this output and report rule violations/unconnected separately.",
        "release_status": "NOT_FOR_GERBER",
    }
    OUT_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
