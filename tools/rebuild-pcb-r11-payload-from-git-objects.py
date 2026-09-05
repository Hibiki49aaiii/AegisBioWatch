#!/usr/bin/env python3
"""Rebuild a corrupted r11 payload from exact Git object content hashes.

The outer r11 manifest contains byte length + SHA-256 for every file expected
inside the archive. This utility scans Git's object database for blobs that
match those exact file identities. Only if *all* expected files are recovered
byte-for-byte does it create a new deterministic tar.gz/base64 payload and
update the outer archive byte-count/SHA metadata.

No missing Base64 bytes are guessed and no PCB file is regenerated from a
similar board. The recovered PCB/project/support files must match the recorded
r11 file SHA-256 values exactly.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAY_DIR = ROOT / "hardware/main-board/pcb/placement-r11-payload"
PAYLOAD = PAY_DIR / "r11-placement-seed.tar.gz.b64"
MANIFEST = PAY_DIR / "manifest.json"
RECOVERY_REPORT = ROOT / "docs/pcb-r11-payload-recovery.json"


def run(*args: str, input_bytes: bytes | None = None, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        list(args),
        cwd=ROOT,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def all_blob_headers() -> list[tuple[str, int]]:
    cp = run(
        "git", "cat-file", "--batch-all-objects",
        "--batch-check=%(objectname) %(objecttype) %(objectsize)"
    )
    rows = []
    for line in cp.stdout.decode("ascii", errors="strict").splitlines():
        parts = line.split()
        if len(parts) != 3 or parts[1] != "blob":
            continue
        rows.append((parts[0], int(parts[2])))
    return rows


def object_paths() -> dict[str, list[str]]:
    cp = run("git", "rev-list", "--objects", "--all")
    result: dict[str, list[str]] = {}
    for raw_line in cp.stdout.decode("utf-8", errors="replace").splitlines():
        if not raw_line:
            continue
        oid, sep, path = raw_line.partition(" ")
        if sep:
            result.setdefault(oid, []).append(path)
    return result


def blob(oid: str) -> bytes:
    return run("git", "cat-file", "blob", oid).stdout


def deterministic_archive(files: dict[str, bytes]) -> bytes:
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as tf:
        for name in sorted(files):
            raw = files[name]
            ti = tarfile.TarInfo(name=name)
            ti.size = len(raw)
            ti.mtime = 0
            ti.uid = 0
            ti.gid = 0
            ti.uname = ""
            ti.gname = ""
            ti.mode = 0o644
            tf.addfile(ti, io.BytesIO(raw))
    gz_buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=gz_buffer, mode="wb", filename="", mtime=0, compresslevel=9) as gz:
        gz.write(tar_buffer.getvalue())
    return gz_buffer.getvalue()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--restore", action="store_true", help="write reconstructed payload and archive metadata")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    targets = manifest.get("files", {})
    if not isinstance(targets, dict) or not targets:
        raise SystemExit("r11 manifest has no file identities")

    by_size: dict[int, list[tuple[str, dict]]] = {}
    for name, meta in targets.items():
        by_size.setdefault(int(meta["bytes"]), []).append((name, meta))

    paths = object_paths()
    recovered: dict[str, bytes] = {}
    provenance: dict[str, dict] = {}
    candidate_blobs_checked = 0

    for oid, size in all_blob_headers():
        if size not in by_size:
            continue
        raw = blob(oid)
        candidate_blobs_checked += 1
        actual_sha = sha256(raw)
        for name, meta in by_size[size]:
            if name in recovered:
                continue
            if actual_sha == meta["sha256"]:
                recovered[name] = raw
                provenance[name] = {
                    "git_blob_oid": oid,
                    "historical_paths": sorted(set(paths.get(oid, []))),
                    "bytes": len(raw),
                    "sha256": actual_sha,
                }

    missing = sorted(set(targets) - set(recovered))
    if missing:
        report = {
            "revision": "r11-placement-seed",
            "status": "INCOMPLETE_GIT_OBJECT_RECOVERY",
            "candidate_blobs_checked": candidate_blobs_checked,
            "recovered": provenance,
            "missing": missing,
            "restore_performed": False,
        }
        RECOVERY_REPORT.parent.mkdir(parents=True, exist_ok=True)
        RECOVERY_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        raise SystemExit(f"Git object recovery incomplete; missing exact r11 files: {missing}")

    # Re-verify all recovered bytes before archive construction.
    for name, meta in targets.items():
        raw = recovered[name]
        if len(raw) != int(meta["bytes"]) or sha256(raw) != meta["sha256"]:
            raise SystemExit(f"internal exact-file verification failed: {name}")

    archive = deterministic_archive(recovered)
    old_archive_bytes = manifest.get("archive_bytes")
    old_archive_sha = manifest.get("archive_sha256")
    new_archive_bytes = len(archive)
    new_archive_sha = sha256(archive)

    report = {
        "revision": "r11-placement-seed",
        "status": "EXACT_FILES_RECOVERED_FROM_GIT_OBJECTS",
        "candidate_blobs_checked": candidate_blobs_checked,
        "recovered": provenance,
        "missing": [],
        "old_archive_bytes": old_archive_bytes,
        "old_archive_sha256": old_archive_sha,
        "new_archive_bytes": new_archive_bytes,
        "new_archive_sha256": new_archive_sha,
        "file_identities_preserved": True,
        "restore_performed": bool(args.restore),
        "note": "Archive container was deterministically regenerated because the committed Base64 payload was truncated; every archived file retains its recorded r11 byte count and SHA-256.",
    }

    if args.restore:
        encoded = base64.b64encode(archive).decode("ascii")
        PAYLOAD.write_text("\n".join(encoded[i:i + 120] for i in range(0, len(encoded), 120)) + "\n", encoding="ascii")
        manifest["archive_bytes"] = new_archive_bytes
        manifest["archive_sha256"] = new_archive_sha
        MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        # Strict post-write verification of the regenerated container.
        compact = "".join(PAYLOAD.read_text(encoding="ascii").split())
        decoded = base64.b64decode(compact, validate=True)
        if len(decoded) != new_archive_bytes or sha256(decoded) != new_archive_sha:
            raise SystemExit("post-write payload verification failed")

    RECOVERY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    RECOVERY_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
