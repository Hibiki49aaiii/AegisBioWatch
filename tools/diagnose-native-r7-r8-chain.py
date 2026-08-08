#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import string
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CASES = [
    {
        "name": "r7_archive",
        "manifest": ROOT / "hardware/main-board/kicad/native-r7-payload/manifest.json",
        "path_key": "archive",
        "bytes_key": "archive_bytes",
        "sha_key": "archive_sha256",
    },
    {
        "name": "r8_patch",
        "manifest": ROOT / "hardware/main-board/kicad/native-r8-patch/manifest.json",
        "path_key": "patch",
        "bytes_key": "patch_bytes",
        "sha_key": "patch_sha256",
    },
]

ALLOWED = set(string.ascii_letters + string.digits + "+/=")


def diagnose(case: dict) -> dict:
    m = json.loads(case["manifest"].read_text(encoding="utf-8"))
    path = ROOT / m[case["path_key"]]
    raw = path.read_bytes()
    result = {
        "name": case["name"],
        "path": str(path.relative_to(ROOT)),
        "manifest": str(case["manifest"].relative_to(ROOT)),
        "payload_file_bytes": len(raw),
        "payload_file_sha256": hashlib.sha256(raw).hexdigest(),
        "expected_decoded_bytes": int(m[case["bytes_key"]]),
        "expected_decoded_sha256": str(m[case["sha_key"]]),
    }
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        result.update({"valid": False, "failure": "non_ascii", "detail": repr(exc)})
        return result

    bad = [(i, ch, ord(ch)) for i, ch in enumerate(text) if not ch.isspace() and ch not in ALLOWED]
    compact = "".join(text.split())
    result["compact_base64_chars"] = len(compact)
    result["base64_length_mod4"] = len(compact) % 4
    result["invalid_non_whitespace_chars"] = len(bad)
    result["first_invalid_chars"] = bad[:20]
    if bad:
        result.update({"valid": False, "failure": "invalid_base64_characters"})
        return result
    if len(compact) % 4:
        result.update({"valid": False, "failure": "base64_length_not_divisible_by_4"})
        return result
    try:
        decoded = base64.b64decode(compact, validate=True)
    except Exception as exc:
        result.update({"valid": False, "failure": "strict_base64_decode", "detail": repr(exc)})
        return result

    actual_sha = hashlib.sha256(decoded).hexdigest()
    result["decoded_bytes"] = len(decoded)
    result["decoded_sha256"] = actual_sha
    result["size_match"] = len(decoded) == result["expected_decoded_bytes"]
    result["sha_match"] = actual_sha == result["expected_decoded_sha256"]
    result["valid"] = bool(result["size_match"] and result["sha_match"])
    if not result["valid"]:
        result["failure"] = "manifest_identity_mismatch"
    return result


def main() -> None:
    results = [diagnose(c) for c in CASES]
    print(json.dumps({"results": results}, indent=2, sort_keys=True))
    if not all(r["valid"] for r in results):
        raise SystemExit("native r7/r8 payload integrity failure")


if __name__ == "__main__":
    main()
