#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, hashlib, json, re, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
PATCH_DIR = ROOT / 'hardware/main-board/kicad/native-r8-patch'
R7_OUT = ROOT / 'hardware/main-board/kicad/native-r7'
OUT = ROOT / 'hardware/main-board/kicad/native-r8'
manifest = json.loads((PATCH_DIR / 'manifest.json').read_text(encoding='utf-8'))

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

encoded = ''.join((ROOT / manifest['patch']).read_text(encoding='ascii').split())
compressed = base64.b64decode(encoded, validate=True)
if len(compressed) != manifest['patch_bytes'] or hashlib.sha256(compressed).hexdigest() != manifest['patch_sha256']:
    raise SystemExit('r8 patch verification failed')
patch_lines = gzip.decompress(compressed).decode('utf-8').splitlines(keepends=True)

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(R7_OUT, OUT)

hunk_re = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')
i = 0
while i < len(patch_lines):
    if not patch_lines[i].startswith('--- '):
        raise SystemExit(f'invalid unified diff at line {i+1}')
    old_path = patch_lines[i][4:].strip()
    i += 1
    if i >= len(patch_lines) or not patch_lines[i].startswith('+++ '):
        raise SystemExit('missing +++ file header')
    new_path = patch_lines[i][4:].strip()
    i += 1
    if not new_path.startswith('b/'):
        raise SystemExit(f'unsafe r8 output path: {new_path}')
    name = new_path[2:]
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or len(p.parts) != 1:
        raise SystemExit(f'unsafe r8 patch path: {name}')
    src_path = OUT / name
    src = [] if old_path == '/dev/null' else src_path.read_text(encoding='utf-8').splitlines(keepends=True)
    out_lines = []
    src_idx = 0
    while i < len(patch_lines) and patch_lines[i].startswith('@@ '):
        m = hunk_re.match(patch_lines[i])
        if not m:
            raise SystemExit(f'invalid hunk header: {patch_lines[i].rstrip()}')
        old_start = int(m.group(1))
        i += 1
        target_idx = 0 if old_start == 0 else old_start - 1
        if target_idx < src_idx or target_idx > len(src):
            raise SystemExit(f'invalid hunk location for {name}')
        out_lines.extend(src[src_idx:target_idx])
        src_idx = target_idx
        while i < len(patch_lines) and not patch_lines[i].startswith('@@ ') and not patch_lines[i].startswith('--- '):
            line = patch_lines[i]
            if line.startswith('\\ No newline at end of file'):
                i += 1
                continue
            if not line or line[0] not in ' +-':
                raise SystemExit(f'invalid hunk line for {name}: {line!r}')
            payload = line[1:]
            if line[0] == ' ':
                if src_idx >= len(src) or src[src_idx] != payload:
                    raise SystemExit(f'context mismatch applying r8 patch to {name}')
                out_lines.append(payload)
                src_idx += 1
            elif line[0] == '-':
                if src_idx >= len(src) or src[src_idx] != payload:
                    raise SystemExit(f'removal mismatch applying r8 patch to {name}')
                src_idx += 1
            else:
                out_lines.append(payload)
            i += 1
    out_lines.extend(src[src_idx:])
    src_path.write_text(''.join(out_lines), encoding='utf-8')

for name, meta in manifest['final_files'].items():
    p = OUT / name
    if not p.is_file():
        raise SystemExit(f'missing r8 authoritative file: {name}')
    raw = p.read_bytes()
    if len(raw) != meta['bytes'] or hashlib.sha256(raw).hexdigest() != meta['sha256']:
        raise SystemExit(f'final r8 verification failed for {name}')

print(f'Native r8 materialized and hash-verified at {OUT}')
