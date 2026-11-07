"""Verify every indexed evidence blob preserves its source SHA256."""
import hashlib
import json
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parent
repo=root.parents[3]
folders=('replay-evidence','capture-evidence','accuracy-evidence','full-control-evidence')
proc=subprocess.Popen(['git','-C',str(repo),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
count=0
try:
    for name in folders:
        folder=root/name
        manifest=json.loads((folder/'manifest.json').read_text())
        for rel,meta in manifest.items():
            path=(folder/rel).relative_to(repo).as_posix()
            proc.stdin.write((':'+path+'\n').encode());proc.stdin.flush()
            header=proc.stdout.readline().decode().strip().split()
            assert len(header)==3 and header[1]=='blob',(path,header)
            size=int(header[2]);data=proc.stdout.read(size)
            assert proc.stdout.read(1)==b'\n' and len(data)==size
            assert size==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],path
            count+=1
finally:
    proc.stdin.close();proc.stdout.close();proc.wait(timeout=30)
assert proc.returncode==0 and count==1206,(proc.returncode,count)
print(f'GIT EVIDENCE PASS: {count} indexed files match original SHA256')
