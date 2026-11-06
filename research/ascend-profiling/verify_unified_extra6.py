"""Verify the committed unified quant snapshot against original capture hashes."""
import hashlib
import json
from pathlib import Path
r=Path(__file__).resolve().parent/'runs/hidev-20261106-unified-extra6'
v=json.loads((r/'progress.json').read_text(encoding='utf8'))
counts={}
for c in v['cases']:
    d=r/'cases'/c['id']
    assert d.is_dir(),d
    counts[c['status']]=counts.get(c['status'],0)+1
    if c['status'] not in ('admitted','needs_review') or 'capture' not in c:continue
    a=json.loads((d/'prepare.json').read_text(encoding='utf8'))
    b=json.loads((d/'default.json').read_text(encoding='utf8'))
    assert a['status']==b['status']=='passed' and a['matched']==b['matched']==1
    assert a['source_sha256']==b['source_sha256'] and a['inputs']==b['inputs']
    for f in c['capture']['files'].values():
        p=r/f['path'];assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],p
print('UNIFIED_EXTRA6_VERIFIED',v['status'],counts)
