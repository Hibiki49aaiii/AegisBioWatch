#!/usr/bin/env python3
from pathlib import Path
import base64, hashlib, io, json, re, shutil, tarfile, tempfile

ROOT = Path(__file__).resolve().parents[1]
PAY = ROOT / 'hardware/main-board/kicad/native-r7-payload'
OUT = ROOT / 'hardware/main-board/kicad/native-r7'
manifest = json.loads((PAY / 'manifest.json').read_text(encoding='utf-8'))
archive_path = ROOT / manifest['archive']
encoded = ''.join(archive_path.read_text(encoding='ascii').split())
archive = base64.b64decode(encoded, validate=True)

if len(archive) != manifest['archive_bytes']:
    raise SystemExit(f"archive size mismatch: {len(archive)} != {manifest['archive_bytes']}")
archive_sha = hashlib.sha256(archive).hexdigest()
if archive_sha != manifest['archive_sha256']:
    raise SystemExit(f"archive hash mismatch: {archive_sha} != {manifest['archive_sha256']}")

def balanced_end(text, start):
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        c = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == '"':
                in_string = False
        else:
            if c == '"':
                in_string = True
            elif c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    return i + 1
    raise ValueError('unbalanced S-expression')

def assign_footprints(path, assignments):
    text = path.read_text(encoding='utf-8')
    starts = []
    pos = 0
    token = '\n\t(symbol\n'
    while True:
        i = text.find(token, pos)
        if i < 0:
            break
        starts.append(i + 1)
        pos = i + len(token)
    replacements = []
    for st in reversed(starts):
        en = balanced_end(text, st)
        block = text[st:en]
        m = re.search(r'\(property "Reference" "([^"]+)"', block)
        if not m or m.group(1) not in assignments:
            continue
        fp = assignments[m.group(1)]
        new, n = re.subn(r'(\(property "Footprint" )"[^"]*"', lambda x: x.group(1) + '"' + fp + '"', block, count=1)
        if n and new != block:
            replacements.append((st, en, new))
    for st, en, new in replacements:
        text = text[:st] + new + text[en:]
    path.write_text(text, encoding='utf-8')

expected = set(manifest['files'])
with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tf:
    members = tf.getmembers()
    names = {m.name for m in members}
    if names != expected:
        raise SystemExit(f"archive file set mismatch; missing={sorted(expected-names)}, unexpected={sorted(names-expected)}")
    for m in members:
        p = Path(m.name)
        if m.isdir() or m.issym() or m.islnk() or m.isdev() or p.is_absolute() or '..' in p.parts or len(p.parts) != 1:
            raise SystemExit(f"unsafe tar member: {m.name}")
    with tempfile.TemporaryDirectory(prefix='aegis-r7-') as td:
        staging = Path(td)
        for m in members:
            src = tf.extractfile(m)
            if src is None:
                raise SystemExit(f"unable to read {m.name}")
            raw = src.read()
            meta = manifest['files'][m.name]
            if len(raw) != meta['bytes'] or hashlib.sha256(raw).hexdigest() != meta['sha256']:
                raise SystemExit(f"source verification failed for {m.name}")
            (staging / m.name).write_bytes(raw)

        assignments = manifest.get('footprint_assignments', {})
        for path in staging.glob('*.kicad_sch'):
            assign_footprints(path, assignments)

        target = manifest.get('materialized_files', manifest['files'])
        for name, meta in target.items():
            raw = (staging / name).read_bytes()
            if len(raw) != meta['bytes'] or hashlib.sha256(raw).hexdigest() != meta['sha256']:
                raise SystemExit(f"materialized verification failed for {name}")

        if OUT.exists():
            shutil.rmtree(OUT)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staging, OUT)

print(f"Native r7 materialized and hash-verified at {OUT}")
