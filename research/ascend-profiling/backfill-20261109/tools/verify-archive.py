"""Verify a split profiling archive and optionally restore all original files."""
import argparse,hashlib,json,shutil,tarfile,tempfile
from pathlib import Path
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def readlines(p):
 with p.open(encoding='utf8') as f:return [json.loads(x) for x in f if x.strip()]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);ap.add_argument('--restore',type=Path);args=ap.parse_args()
 root=args.archive.resolve(strict=True);doc=json.loads((root/'manifest.json').read_text(encoding='utf8'))
 for name,key in [('files.jsonl','files_jsonl_sha256'),('tables.jsonl','tables_jsonl_sha256'),('support.jsonl','support_jsonl_sha256')]:assert sha(root/name)==doc[key],name
 files=readlines(root/'files.jsonl');tables=readlines(root/'tables.jsonl');support=readlines(root/'support.jsonl')
 for x in tables:assert sha(root/x['table_path'])==x['sha256'],x['table_path']
 for x in support:assert sha(root/x['support_path'])==x['sha256'],x['support_path']
 assert len(support)==doc['support_count']
 restore=None
 if args.restore:
  restore=args.restore.resolve();assert not restore.exists();restore.mkdir(parents=True)
 for unit in doc['units']:
  expected={x['member']:x for x in files if x['archive']==unit['archive']};assert len(expected)==unit['member_count']
  with tempfile.TemporaryDirectory(prefix='puma-profile-verify-') as temp:
   archive=Path(temp)/'content.tar.gz'
   with archive.open('wb') as out:
    for part in unit['parts']:
     p=root/part['path'];assert p.stat().st_size==part['bytes'] and sha(p)==part['sha256'],part['path']
     with p.open('rb') as f:shutil.copyfileobj(f,out,1024*1024)
   assert archive.stat().st_size==unit['archive_bytes'] and sha(archive)==unit['archive_sha256']
   with tarfile.open(archive,'r:gz') as tar:
    for info in tar:
     assert info.isfile() and info.name in expected
     record=expected.pop(info.name);h=hashlib.sha256();size=0;dest=None
     if restore:
      path=(restore/info.name).resolve();assert path.is_relative_to(restore) and not path.exists();path.parent.mkdir(parents=True,exist_ok=True);dest=path.open('xb')
     try:
      with tar.extractfile(info) as f:
       for b in iter(lambda:f.read(1024*1024),b''):
        h.update(b);size+=len(b)
        if dest:dest.write(b)
     finally:
      if dest:dest.close()
     assert size==record['bytes'] and h.hexdigest()==record['sha256'],info.name
   assert not expected,unit['archive']
  print('VERIFIED',unit['archive'],flush=True)
 assert len(files)==sum(x['member_count'] for x in doc['units'])
 print('ARCHIVE_VERIFIED units',len(doc['units']),'files',len(files),'tables',len(tables),'support',len(support))
if __name__=='__main__':main()
