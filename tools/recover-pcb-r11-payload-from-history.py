#!/usr/bin/env python3
"""Recover the r11 placement payload from repository history without guessing bytes.

The current payload may be damaged by text truncation/placeholder insertion. This
utility searches historical blobs for this exact path and accepts a candidate
only if, after strict Base64 decoding, BOTH the compressed archive byte count
and SHA-256 match the current r11 manifest. No fuzzy repair is permitted.

With --restore, the exact certified historical blob is written back to the
working tree. The caller may then commit that byte-for-byte restoration.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_REL = Path("hardware/main-board/pcb/placement-r11-payload/r11-placement-seed.tar.gz.b64")
MANIFEST_REL = Path("hardware/main-board/pcb/placement-r11-payload/manifest.json")
PAYLOAD = ROOT / PAYLOAD_REL
MANIFEST = ROOT / MANIFEST_REL


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        list(args),
        cwd=ROOT,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def validate_blob(raw: bytes, expected_bytes: int, expected_sha: str) -> tuple[bool, str]:
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        return False, f"non-ASCII payload: {exc}"
    compact = "".join(text.split())
    if len(compact) % 4:
        return False, f"base64 length {len(compact)} is not divisible by 4"
    try:
        archive = base64.b64decode(compact, validate=True)
    except Exception as exc:
        return False, f"strict base64 decode failed: {exc}"
    if len(archive) != expected_bytes:
        return False, f"archive bytes {len(archive)} != expected {expected_bytes}"
    actual_sha = hashlib.sha256(archive).hexdigest()
    if actual_sha != expected_sha:
        return False, f"archive sha256 {actual_sha} != expected {expected_sha}"
    return True, "exact archive size+sha256 match"


def git_commits_for_path() -> list[str]:
    # The path has not been renamed; searching all refs gives us branch, base and
    # merge history without relying on GitHub API indexing. Full history is
    # supplied by actions/checkout fetch-depth: 0.
    cp = run("git", "log", "--all", "--format=%H", "--", PAYLOAD_REL.as_posix())
    commits = []
    seen = set()
    for line in cp.stdout.decode("ascii", errors="strict").splitlines():
        sha = line.strip()
        if sha and sha not in seen:
            seen.add(sha)
            commits.append(sha)
    return commits


def blob_at(commit: str) -> bytes | None:
    cp = run("git", "show", f"{commit}:{PAYLOAD_REL.as_posix()}", check=False)
    if cp.returncode != 0:
        return None
    return cp.stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--restore", action="store_true", help="write the certified historical blob to the working tree")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_bytes = int(manifest["archive_bytes"])
    expected_sha = str(manifest["archive_sha256"])

    current = PAYLOAD.read_bytes()
    current_ok, current_reason = validate_blob(current, expected_bytes, expected_sha)
    if current_ok:
        result = {
            "status": "CURRENT_PAYLOAD_ALREADY_VALID",
            "archive_bytes": expected_bytes,
            "archive_sha256": expected_sha,
            "payload_file_sha256": hashlib.sha256(current).hexdigest(),
            "restored": False,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    attempts = []
    good_commit = None
    good_blob = None
    for commit in git_commits_for_path():
        raw = blob_at(commit)
        if raw is None:
            continue
        ok, reason = validate_blob(raw, expected_bytes, expected_sha)
        attempts.append({"commit": commit, "valid": ok, "reason": reason})
        if ok:
            good_commit = commit
            good_blob = raw
            break

    if good_commit is None or good_blob is None:
        report = {
            "status": "NO_CERTIFIED_HISTORICAL_PAYLOAD_FOUND",
            "current_failure": current_reason,
            "expected_archive_bytes": expected_bytes,
            "expected_archive_sha256": expected_sha,
            "historical_candidates_checked": len(attempts),
            "attempts": attempts[:30],
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        raise SystemExit("No historical r11 payload matched the manifest exactly; refusing heuristic repair")

    restored = False
    if args.restore:
        PAYLOAD.write_bytes(good_blob)
        verify_ok, verify_reason = validate_blob(PAYLOAD.read_bytes(), expected_bytes, expected_sha)
        if not verify_ok:
            raise SystemExit(f"post-restore verification failed: {verify_reason}")
        restored = current != good_blob

    result = {
        "status": "CERTIFIED_HISTORICAL_PAYLOAD_FOUND",
        "current_failure": current_reason,
        "source_commit": good_commit,
        "archive_bytes": expected_bytes,
        "archive_sha256": expected_sha,
        "historical_payload_file_sha256": hashlib.sha256(good_blob).hexdigest(),
        "restored": restored,
        "candidates_checked_until_match": len(attempts),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
