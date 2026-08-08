#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, hashlib, io, json, shutil, tarfile, tempfile

ROOT = Path(__file__).resolve().parents[1]
PAY = ROOT / 'hardware/main-board/pcb/placement-r11-payload'
OUT = ROOT / 'hardware/main-board/pcb/placement-r11'
manifest = json.loads((PAY / 'manifest.json').read_text(encoding='utf-8'))
encoded_path = ROOT / manifest['archive']
encoded = ''.join(encoded_path.read_text(encoding='ascii').split())
archive = base64.b64decode(encoded, validate=True)
if len(archive) != manifest['archive_bytes']:
    raise SystemExit('r11 archive size mismatch')
if hashlib.sha256(archive).hexdigest() != manifest['archive_sha256']:
    raise SystemExit('r11 archive SHA-256 mismatch')

with gzip.GzipFile(fileobj=io.BytesIO(archive), mode='rb') as gz:
    tar_bytes = gz.read()
with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode='r:') as tf:
    members = tf.getmembers()
    expected = set(manifest['files'])
    names = {m.name for m in members}
    if names != expected:
        raise SystemExit(f'r11 archive file-set mismatch: missing={sorted(expected-names)}, unexpected={sorted(names-expected)}')
    with tempfile.TemporaryDirectory(prefix='aegis-r11-') as td:
        staging = Path(td)
        for m in members:
            p = Path(m.name)
            if m.isdir() or m.issym() or m.islnk() or m.isdev() or p.is_absolute() or '..' in p.parts or len(p.parts) != 1:
                raise SystemExit(f'unsafe r11 archive member: {m.name}')
            src = tf.extractfile(m)
            if src is None:
                raise SystemExit(f'unable to read r11 archive member: {m.name}')
            raw = src.read()
            meta = manifest['files'][m.name]
            if len(raw) != meta['bytes'] or hashlib.sha256(raw).hexdigest() != meta['sha256']:
                raise SystemExit(f'r11 file verification failed: {m.name}')
            (staging / m.name).write_bytes(raw)
        if OUT.exists():
            shutil.rmtree(OUT)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staging, OUT)
print(f'PCB r11 placement seed materialized and hash-verified at {OUT}')
