"""Verify each support bundle file without extracting it."""
import hashlib,json,sys,tarfile
from pathlib import PurePosixPath
archive=sys.argv[1]
with tarfile.open(archive,'r:gz') as t:
 members=t.getmembers();assert all(x.isfile() or x.isdir() for x in members)
 assert all(not PurePosixPath(x.name).is_absolute() and '..' not in PurePosixPath(x.name).parts for x in members)
 prefixes=('expert-profile-backfill-20261109-support-snapshot/', 'expert-profile-backfill-20261109-support-snapshot-v2/', 'expert-profile-backfill-20261109-support-snapshot-v3/', 'expert-profile-backfill-20261109-support-snapshot-v4/', 'expert-profile-backfill-20261109-support-snapshot-v5/', 'expert-profile-backfill-20261109-support-snapshot-v6/', 'expert-profile-backfill-20261109-support-snapshot-v7/', 'expert-profile-backfill-20261109-support-snapshot-v9/', 'expert-profile-backfill-20261109-support-snapshot-v10/', 'expert-profile-backfill-20261109-support-snapshot-v11/', 'expert-profile-backfill-20261109-support-snapshot-v12/', 'expert-profile-backfill-20261109-support-snapshot-v13/', 'expert-profile-backfill-20261109-support-snapshot-v14/', 'expert-profile-backfill-20261109-support-snapshot-v15/')
 matches=[p for p in prefixes if any(x.name==p+'support-manifest.json' and x.isfile() for x in members)]
 assert len(matches)==1
 prefix,=matches
 data=json.load(t.extractfile(prefix+'support-manifest.json'));expected={prefix+x['path']:x for x in data['files']}
 assert len(expected)==data['count']
 for m in members:
  if not m.isfile() or m.name==prefix+'support-manifest.json':continue
  rec=expected.pop(m.name);h=hashlib.sha256();size=0
  with t.extractfile(m) as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b);size+=len(b)
  assert size==rec['bytes'] and h.hexdigest()==rec['sha256'],m.name
 assert not expected
print('SUPPORT_BUNDLE_VERIFIED',data['count'])
