"""Snapshot completed starter cases from the user's existing hidev tmux session.

Run on the Windows workstation with the authenticated Arch WSL pane in tmux 0.
The byte transfer is checksummed; only completed case directories are copied.
No private key or credentials are copied. `--push` commits only the run folder.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PUMA = Path(os.environ.get('PUMA_WORKSPACE', 'D:/puma_v2'))
sys.path.insert(0, str(PUMA / 'outputs/reprofile-60-cold-20261101/scripts'))
import transport  # existing authenticated tmux transport with an interprocess lock

REMOTE = '/workspace/tilekernels-expert-profiles-20261106'
DEST = HERE / 'runs/hidev-20261106-starter'
DEST_REL = 'research/ascend-profiling/runs/hidev-20261106-starter'


def query(code):
    return transport.query(code)


def remote_progress():
    code = f"from pathlib import Path;import json;p=Path({REMOTE!r})/'progress.json';v=json.loads(p.read_text()) if p.exists() else {{}};print(json.dumps({{'status':v.get('status'),'ids':[c['id'] for c in v.get('cases',[])]}}))"
    return json.loads(query(code))


def make_archive():
    source = f'''
from pathlib import Path
import json,tarfile,hashlib,time
p=Path({REMOTE!r})
v=json.loads((p/'progress.json').read_text())
ids=[c['id'] for c in v['cases']]
assert all('/' not in x and x not in ('.','..') for x in ids)
target=Path('/workspace')/('tk-starter-sync-'+str(time.time_ns())+'.tar.gz')
with tarfile.open(target,'w:gz') as out:
 for name in ('progress.json','cases.json','environment.json','pilot.log','remaining.log','queue-v2.log'):
  f=p/name
  if f.exists(): out.add(f,arcname=name)
 for cid in ids:
  d=p/'cases'/cid
  assert d.is_dir(),d
  out.add(d,arcname='cases/'+cid)
b=target.read_bytes()
print(json.dumps({{'path':str(target),'size':len(b),'sha256':hashlib.sha256(b).hexdigest(),'ids':ids,'status':v['status']}}))
'''
    return json.loads(query('exec(' + repr(source) + ')'))


def download(info):
    assert info['path'].startswith('/workspace/tk-starter-sync-') and info['size'] < 200_000_000
    data = bytearray()
    for off in range(0, info['size'], 24000):
        code = (f"from pathlib import Path;import base64;f=Path({info['path']!r}).open('rb');"
                f"f.seek({off});print(base64.b64encode(f.read(24000)).decode())")
        chunk = base64.b64decode(''.join(query(code).split()), validate=True)
        assert len(chunk) == min(24000, info['size'] - off)
        data.extend(chunk)
    assert sha256(data).hexdigest() == info['sha256']
    return data


def verify_and_merge(data, info):
    DEST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='tk-profile-sync-') as tmp:
        root = Path(tmp)
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
            for m in archive.getmembers():
                assert (root / m.name).resolve().is_relative_to(root.resolve())
                assert m.isfile() or m.isdir()
            archive.extractall(root, filter='data')
        progress = json.loads((root / 'progress.json').read_text(encoding='utf8'))
        assert [c['id'] for c in progress['cases']] == info['ids']
        for c in progress['cases']:
            case_dir = root / 'cases' / c['id']
            assert case_dir.is_dir()
            if c['status'] == 'admitted':
                a = json.loads((case_dir/'prepare.json').read_text(encoding='utf8'))
                b = json.loads((case_dir/'default.json').read_text(encoding='utf8'))
                assert a['status'] == b['status'] == 'passed'
                assert a['inputs'] == b['inputs'] and a['source_sha256'] == b['source_sha256']
                assert all(v['passed'] for v in a['precision'] + b['precision'])
                for f in c['capture']['files'].values():
                    q = root / f['path']
                    assert q.is_file() and sha256(q.read_bytes()).hexdigest() == f['sha256'], q
        for source in root.rglob('*'):
            if not source.is_file():
                continue
            rel = source.relative_to(root)
            dest = DEST / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if rel.parts[0] == 'cases' and dest.exists():
                assert sha256(dest.read_bytes()).digest() == sha256(source.read_bytes()).digest(), dest
            else:
                shutil.copy2(source, dest)
    (DEST/'sync-info.json').write_text(json.dumps(info, indent=2)+'\n', encoding='utf8')
    return progress


def git(*args, check=True):
    return subprocess.run(['git', '-C', str(REPO), *args], text=True, capture_output=True, check=check)


def publish():
    assert git('branch', '--show-current').stdout.strip() == 'main', 'checkout is not main'
    assert git('diff', '--cached', '--quiet', check=False).returncode == 0, 'index has unrelated staged changes'
    local_head = git('rev-parse', 'HEAD').stdout.strip()
    # The SSH key stays in WSL; this command transmits Git objects only.
    remote = subprocess.run(['wsl','-d','archlinux','--','git','ls-remote',
                             'git@github.com:DanielLee343/TileKernels.git','refs/heads/main'],
                            text=True,encoding='utf8',errors='replace',capture_output=True,check=True).stdout.split()[0]
    assert local_head == remote, 'remote has moved; pull/review before syncing'
    # wsl.exe passes arguments through a Unix shell; forward slashes avoid
    # backslashes being consumed before wslpath sees the Windows path.
    wsl_path = subprocess.run(['wsl','-d','archlinux','--','wslpath','-a',REPO.as_posix()],
                              text=True,encoding='utf8',errors='replace',capture_output=True,check=True).stdout.strip()
    git('add', '--', DEST_REL)
    if git('diff','--cached','--quiet',check=False).returncode == 0:
        print('No new run data to commit', flush=True)
        return
    staged = git('diff','--cached','--name-only').stdout.splitlines()
    assert staged and all(p.startswith(DEST_REL+'/') for p in staged), staged
    git('-c','user.name=lyuze','-c','user.email=670525945@qq.com','commit','-q','-m','Sync hidev Default profiling results')
    subprocess.run(['wsl','-d','archlinux','--','git','-C',wsl_path,'push','origin','main'],check=True)
    print('SYNC_PUSHED',git('rev-parse','HEAD').stdout.strip(),flush=True)


def sync(push):
    info = make_archive()
    try:
        data = download(info)
        progress = verify_and_merge(data, info)
    finally:
        query(f"from pathlib import Path;Path({info['path']!r}).unlink(missing_ok=True);print('removed')")
    print('SYNC_VERIFIED',len(progress['cases']),progress['status'],flush=True)
    if push:
        publish()
    return progress


def main():
    global REMOTE, DEST, DEST_REL
    parser=argparse.ArgumentParser()
    parser.add_argument('--watch',action='store_true')
    parser.add_argument('--push',action='store_true')
    parser.add_argument('--batch',choices=('starter','second','third','fourth','fifth'),default='starter')
    args=parser.parse_args()
    if args.batch=='second':
        REMOTE='/workspace/tilekernels-expert-profiles-second-20261106'
        DEST=HERE/'runs/hidev-20261106-second'
        DEST_REL='research/ascend-profiling/runs/hidev-20261106-second'
    elif args.batch=='third':
        REMOTE='/workspace/tilekernels-expert-profiles-third-20261106'
        DEST=HERE/'runs/hidev-20261106-third'
        DEST_REL='research/ascend-profiling/runs/hidev-20261106-third'
    elif args.batch=='fourth':
        REMOTE='/workspace/tilekernels-expert-profiles-fourth-20261106'
        DEST=HERE/'runs/hidev-20261106-fourth'
        DEST_REL='research/ascend-profiling/runs/hidev-20261106-fourth'
    elif args.batch=='fifth':
        REMOTE='/workspace/tilekernels-expert-profiles-fifth-20261106'
        DEST=HERE/'runs/hidev-20261106-fifth'
        DEST_REL='research/ascend-profiling/runs/hidev-20261106-fifth'
    if not args.watch:
        sync(args.push)
        return
    last=None
    while True:
        p=remote_progress()
        marker=(p['status'],tuple(p['ids']))
        if p['ids'] and marker!=last:
            result=sync(args.push)
            last=(result['status'],tuple(c['id'] for c in result['cases']))
            if result['status']=='finished':
                return
        time.sleep(45)


if __name__=='__main__':
    main()
