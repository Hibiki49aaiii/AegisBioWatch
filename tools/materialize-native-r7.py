#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, hashlib, json

ROOT = Path(__file__).resolve().parents[1]
PAY = ROOT / 'hardware/main-board/kicad/native-r7-payload'
OUT = ROOT / 'hardware/main-board/kicad/capture'
manifest = json.loads((PAY / 'manifest.json').read_text())

for name, meta in manifest.items():
    raw = gzip.decompress(base64.b64decode((ROOT / meta['payload']).read_text()))
    digest = hashlib.sha256(raw).hexdigest()
    if digest != meta['sha256']:
        raise SystemExit(f'hash mismatch for {name}: {digest} != {meta["sha256"]}')
    (OUT / name).write_bytes(raw)
    print(f'Wrote {name} ({len(raw)} bytes, sha256={digest})')

print('Native r7 payload materialized successfully.')
