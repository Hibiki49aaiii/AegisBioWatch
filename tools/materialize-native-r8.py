#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, hashlib, io, json, shutil, subprocess, sys, tarfile, tempfile

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'hardware/main-board/kicad/native-r8-patch'
R7_OUT = ROOT / 'hardware/main-board/kicad/native-r7'
OUT = ROOT / 'hardware/main-board/kicad/native-r8'
manifest = json.loads((PATCH / 'manifest.json').read_text(encoding='utf-8'))

# Materialize the already hash-verified r7 base first.
subprocess.run([sys.executable, str(ROOT / manifest['base_materializer'])], cwd=ROOT, check=True)
if not R7_OUT.is_dir():
    raise SystemExit(f'r7 materializer did not create {R7_OUT}')

# Verify r8 is applied to the exact expected r7 files.
for name, meta in manifest['replacements'].items():
    base = R7_OUT / name
    if meta.get('base_sha256') is None:
        if base.exists():
            raise SystemExit(f'expected r7 base file to be absent: {name}')
        continue
    if not base.is_file():
        raise SystemExit(f'missing expected r7 base file: {name}')
    raw = base.read_bytes()
    if len(raw) != meta['base_bytes'] or hashlib.sha256(raw).hexdigest() != meta['base_sha256']:
        raise SystemExit(f'r7 base verification failed for {name}')

encoded = ''.join((ROOT / manifest['patch_archive']).read_text(encoding='ascii').split())
archive = base64.b64decode(encoded, validate=True)
if len(archive) != manifest['patch_archive_bytes'] or hashlib.sha256(archive).hexdigest() != manifest['patch_archive_sha256']:
    raise SystemExit('r8 patch archive verification failed')

# Validate archive members before extraction.
with tarfile.open(fileobj=io.BytesIO(gzip.decompress(archive)), mode='r:') as tf:
    members = tf.getmembers()
    expected = set(manifest['replacements'])
    names = {m.name for m in members}
    if names != expected:
        raise SystemExit(f'r8 patch file set mismatch; missing={sorted(expected-names)}, unexpected={sorted(names-expected)}')
    replacement_bytes = {}
    for m in members:
        p = Path(m.name)
        if m.isdir() or m.issym() or m.islnk() or m.isdev() or p.is_absolute() or '..' in p.parts or len(p.parts) != 1:
            raise SystemExit(f'unsafe r8 patch member: {m.name}')
        src = tf.extractfile(m)
        if src is None:
            raise SystemExit(f'unable to read r8 patch member: {m.name}')
        raw = src.read()
        meta = manifest['replacements'][m.name]
        if len(raw) != meta['bytes'] or hashlib.sha256(raw).hexdigest() != meta['sha256']:
            raise SystemExit(f'r8 replacement verification failed for {m.name}')
        replacement_bytes[m.name] = raw

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(R7_OUT, OUT)
for name, raw in replacement_bytes.items():
    (OUT / name).write_bytes(raw)

# Exact post-materialization authority check.
for name, meta in manifest['final_files'].items():
    p = OUT / name
    if not p.is_file():
        raise SystemExit(f'missing r8 authoritative file: {name}')
    raw = p.read_bytes()
    if len(raw) != meta['bytes'] or hashlib.sha256(raw).hexdigest() != meta['sha256']:
        raise SystemExit(f'final r8 verification failed for {name}')

print(f'Native r8 materialized and hash-verified at {OUT}')
