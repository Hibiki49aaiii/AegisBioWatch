#!/usr/bin/env python3
from pathlib import Path
import base64
import hashlib
import io
import json
import shutil
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PAY = ROOT / 'hardware/main-board/kicad/native-r7-payload'
OUT = ROOT / 'hardware/main-board/kicad/native-r7'
MANIFEST = PAY / 'manifest.json'

manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
archive_path = ROOT / manifest['archive']
encoded = ''.join(archive_path.read_text(encoding='ascii').split())
archive = base64.b64decode(encoded, validate=True)

if len(archive) != manifest['archive_bytes']:
    raise SystemExit(f"archive size mismatch: {len(archive)} != {manifest['archive_bytes']}")
archive_sha = hashlib.sha256(archive).hexdigest()
if archive_sha != manifest['archive_sha256']:
    raise SystemExit(f"archive hash mismatch: {archive_sha} != {manifest['archive_sha256']}")

expected = set(manifest['files'])
with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tf:
    members = tf.getmembers()
    names = {m.name for m in members}
    if names != expected:
        missing = sorted(expected - names)
        unexpected = sorted(names - expected)
        raise SystemExit(f"archive file set mismatch; missing={missing}, unexpected={unexpected}")

    for m in members:
        p = Path(m.name)
        if m.isdir() or m.issym() or m.islnk() or m.isdev():
            raise SystemExit(f"unsafe/non-file tar member: {m.name}")
        if p.is_absolute() or '..' in p.parts or len(p.parts) != 1:
            raise SystemExit(f"unsafe tar path: {m.name}")

    with tempfile.TemporaryDirectory(prefix='aegis-r7-') as td:
        staging = Path(td)
        for m in members:
            src = tf.extractfile(m)
            if src is None:
                raise SystemExit(f"unable to read tar member: {m.name}")
            raw = src.read()
            meta = manifest['files'][m.name]
            if len(raw) != meta['bytes']:
                raise SystemExit(f"size mismatch for {m.name}: {len(raw)} != {meta['bytes']}")
            digest = hashlib.sha256(raw).hexdigest()
            if digest != meta['sha256']:
                raise SystemExit(f"hash mismatch for {m.name}: {digest} != {meta['sha256']}")
            (staging / m.name).write_bytes(raw)

        if OUT.exists():
            shutil.rmtree(OUT)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staging, OUT)

for name, meta in manifest['files'].items():
    p = OUT / name
    raw = p.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if len(raw) != meta['bytes'] or digest != meta['sha256']:
        raise SystemExit(f"post-write verification failed for {name}")
    print(f"Verified {name} ({len(raw)} bytes, sha256={digest})")

print(f"Native r7 materialized successfully at {OUT}")
