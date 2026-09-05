#!/usr/bin/env python3
"""Print the small pcbnew API surface needed to rebuild r11 in CI."""
from __future__ import annotations

import json

try:
    import pcbnew  # type: ignore
except Exception as exc:
    print(json.dumps({"pcbnew_import": False, "error": repr(exc)}, indent=2))
    raise

names = dir(pcbnew)
interesting = [
    name for name in names
    if any(token.lower() in name.lower() for token in (
        "LoadBoard", "SaveBoard", "FootprintLoad", "BOARD", "NETINFO",
        "VECTOR2I", "FromMM", "ToMM", "PCB_IO", "GetBoard",
    ))
]
board_methods = []
try:
    board_methods = [
        name for name in dir(pcbnew.BOARD())
        if any(token.lower() in name.lower() for token in (
            "Add", "Net", "Footprint", "Design", "Connectivity", "BBox", "Bounding",
        ))
    ]
except Exception as exc:
    board_methods = [f"BOARD() probe failed: {exc!r}"]

print(json.dumps({
    "pcbnew_import": True,
    "version": getattr(pcbnew, "GetBuildVersion", lambda: "unknown")(),
    "module_symbols": sorted(interesting),
    "board_methods": sorted(board_methods),
}, indent=2))
