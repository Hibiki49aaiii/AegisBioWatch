#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, hashlib, json, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
PATCH_DIR = ROOT / 'hardware/main-board/kicad/native-r8-patch'
R7_OUT = ROOT / 'hardware/main-board/kicad/native-r7'
OUT = ROOT / 'hardware/main-board/kicad/native-r8'
manifest = json.loads((PATCH_DIR / 'manifest.json').read_text(encoding='utf-8'))

# Reconstruct and hash-verify the exact r7 base first.
subprocess.run([sys.executable, str(ROOT / manifest['base_materializer'])], cwd=ROOT, check=True)
if not R7_OUT.is_dir():
    raise SystemExit(f'r7 materializer did not create {R7_OUT}')

for name, meta in manifest['base_files'].items():
    p = R7_OUT / name
    if meta is None:
        if p.exists():
            raise SystemExit(f'expected base file to be absent: {name}')
        continue
    if not p.is_file():
        raise SystemExit(f'missing r7 base file: {name}')
    raw = p.read_bytes()
    if len(raw) != meta['bytes'] or hashlib.sha256(raw).hexdigest() != meta['sha256']:
        raise SystemExit(f'r7 base verification failed for {name}')

# Strictly decode and identify the patch container before doing any write.
encoded = ''.join((ROOT / manifest['patch']).read_text(encoding='ascii').split())
compressed = base64.b64decode(encoded, validate=True)
if len(compressed) != manifest['patch_bytes'] or hashlib.sha256(compressed).hexdigest() != manifest['patch_sha256']:
    raise SystemExit('r8 patch verification failed')
patch_bytes = gzip.decompress(compressed)
try:
    patch_text = patch_bytes.decode('utf-8')
except UnicodeDecodeError as exc:
    raise SystemExit(f'r8 patch is not UTF-8: {exc}')

# Before delegating unified-diff mechanics to the standard patch engine, reject
# every path except a single top-level filename under a/ or b/.  /dev/null is
# allowed only for file creation/deletion headers.  Final-file hashes below are
# still the ultimate authority for the materialized result.
def safe_header_path(line: str, prefix: str) -> None:
    raw = line[len(prefix):].rstrip('\r\n')
    # Unified diffs may append timestamps after a tab.
    raw = raw.split('\t', 1)[0].strip()
    if raw == '/dev/null':
        return
    if not (raw.startswith('a/') or raw.startswith('b/')):
        raise SystemExit(f'unsafe r8 patch header path: {raw!r}')
    rel = Path(raw[2:])
    if rel.is_absolute() or '..' in rel.parts or len(rel.parts) != 1:
        raise SystemExit(f'unsafe r8 patch relative path: {raw!r}')
    if rel.name not in manifest['final_files'] and rel.name not in manifest['base_files']:
        raise SystemExit(f'r8 patch references undeclared file: {rel.name}')

header_count = 0
for line in patch_text.splitlines(keepends=True):
    if line.startswith('--- '):
        safe_header_path(line, '--- ')
        header_count += 1
    elif line.startswith('+++ '):
        safe_header_path(line, '+++ ')
        header_count += 1
if header_count == 0 or header_count % 2:
    raise SystemExit(f'r8 patch has invalid header count: {header_count}')

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(R7_OUT, OUT)

# The previous handwritten hunk parser was intentionally strict but rejected
# valid unified-diff variants.  Use the mature patch engine for mechanics while
# retaining strict input hash/path checks and byte-for-byte final-file hashes.
try:
    proc = subprocess.run(
        ['patch', '--batch', '--forward', '--reject-file=-', '-p1', '-d', str(OUT)],
        input=patch_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
except FileNotFoundError:
    raise SystemExit("system 'patch' command is required to materialize r8")
if proc.returncode != 0:
    raise SystemExit('r8 patch application failed:\n' + proc.stdout.decode('utf-8', errors='replace'))

# No undeclared files may be introduced, and every authoritative output must
# match the manifest exactly.  This prevents a permissive patch application
# from silently changing electrical authority.
actual_files = {p.name for p in OUT.iterdir() if p.is_file()}
expected_files = set(manifest['final_files'])
if actual_files != expected_files:
    raise SystemExit(
        f'r8 final file-set mismatch: missing={sorted(expected_files-actual_files)}, '
        f'unexpected={sorted(actual_files-expected_files)}'
    )

for name, meta in manifest['final_files'].items():
    p = OUT / name
    if not p.is_file():
        raise SystemExit(f'missing r8 authoritative file: {name}')
    raw = p.read_bytes()
    if len(raw) != meta['bytes'] or hashlib.sha256(raw).hexdigest() != meta['sha256']:
        raise SystemExit(f'final r8 verification failed for {name}')

print(f'Native r8 materialized and hash-verified at {OUT}')
