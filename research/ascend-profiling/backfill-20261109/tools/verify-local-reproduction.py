"""Check the local reproduction snapshot without extracting its contents."""
import hashlib,json,sys,tarfile
from pathlib import PurePosixPath

prefix='local-reproduction-snapshot/'
with tarfile.open(sys.argv[1],'r:gz') as t:
 members=t.getmembers();assert all(x.isfile() or x.isdir() for x in members)
 assert all(not PurePosixPath(x.name).is_absolute() and '..' not in PurePosixPath(x.name).parts for x in members)
 assert len({x.name for x in members})==len(members)
 data=json.load(t.extractfile(prefix+'manifest.json'));expected={prefix+x['path']:x for x in data['files']}
 assert len(expected)==data['count']
 for m in members:
  if not m.isfile() or m.name==prefix+'manifest.json':continue
  rec=expected.pop(m.name);h=hashlib.sha256();size=0
  with t.extractfile(m) as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b);size+=len(b)
  assert size==rec['bytes'] and h.hexdigest()==rec['sha256'],m.name
 assert not expected
print('LOCAL_REPRODUCTION_VERIFIED',data['count'])
