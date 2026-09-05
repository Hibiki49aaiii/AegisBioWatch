#!/usr/bin/env python3
"""Move the route-1h PVSS1 cap-side via away from C104.2.

The first DRC-cleanup attempt left the PVSS1_LOCAL through-via at
(5.55, 28.265584), which is electrically too close to C104.2/PVSS2_LOCAL.
This focused postprocessor moves only that via and the two attached
PVSS1_LOCAL track endpoints to (5.55, 27.55), then refills zones and saves.

It intentionally exits with os._exit() after SaveBoard to avoid KiCad 9
Python/SWIG teardown instability already observed in this route stage.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pcbnew  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / 'hardware/main-board/pcb/route-r13-1h/AegisBioWatch-MainBoard-Route1h-r13.kicad_pcb'
OLD = (5.55, 28.265584)
NEW = (5.55, 27.55)
TOL = 0.001


def mm(v):
    return float(pcbnew.ToMM(v))


def iu(v):
    return int(pcbnew.FromMM(v))


def pos_tuple(p):
    return (mm(p.x), mm(p.y))


def close(a, b):
    return abs(a[0] - b[0]) <= TOL and abs(a[1] - b[1]) <= TOL


def refill(board):
    zs = pcbnew.ZONES()
    for z in board.Zones():
        zs.append(z)
    if len(zs) and not pcbnew.ZONE_FILLER(board).Fill(zs):
        raise SystemExit('route1h postprocess zone refill failed')


def main():
    if not PCB.is_file():
        raise SystemExit('route1h PCB missing')

    board = pcbnew.LoadBoard(str(PCB))
    moved_vias = 0
    adjusted_endpoints = 0

    for item in list(board.GetTracks()):
        if item.GetNetname() != 'PVSS1_LOCAL':
            continue

        if isinstance(item, pcbnew.PCB_VIA):
            if close(pos_tuple(item.GetPosition()), OLD):
                item.SetPosition(pcbnew.VECTOR2I(iu(NEW[0]), iu(NEW[1])))
                moved_vias += 1
            continue

        if not isinstance(item, pcbnew.PCB_TRACK):
            continue

        s = pos_tuple(item.GetStart())
        e = pos_tuple(item.GetEnd())
        if close(s, OLD):
            item.SetStart(pcbnew.VECTOR2I(iu(NEW[0]), iu(NEW[1])))
            adjusted_endpoints += 1
        if close(e, OLD):
            item.SetEnd(pcbnew.VECTOR2I(iu(NEW[0]), iu(NEW[1])))
            adjusted_endpoints += 1

    if moved_vias != 1 or adjusted_endpoints != 2:
        raise SystemExit(
            f'route1h PVSS1-via scope gate failed: vias={moved_vias} endpoints={adjusted_endpoints}'
        )

    refill(board)
    if not pcbnew.SaveBoard(str(PCB), board):
        raise SystemExit('route1h postprocess SaveBoard failed')

    print(
        f'route1h PVSS1 cap via moved {OLD} -> {NEW}; '
        f'adjusted track endpoints={adjusted_endpoints}',
        flush=True,
    )
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)


if __name__ == '__main__':
    main()
