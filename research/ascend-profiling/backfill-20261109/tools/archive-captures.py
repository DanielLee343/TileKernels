"""Archive immutable profiling runs with file hashes and directly readable CSVs.

Run after all selected queues have stopped. Each case is a separate gzip tar,
split below GitHub's single-file limit. `files.jsonl` is a full member manifest;
`tables.jsonl` maps every separately copied CSV to its exact archived member.
"""
import argparse,csv,hashlib,json,os,shutil,sys,tarfile,tempfile
from pathlib import Path

GROUPS=('runs','mhc-runs','fused-runs','topk-runs','hash-runs','classic-runs','deepgemm-runs','mega28-runs','unified-quant-runs','extra-proxy-runs','tbe-evidence','hidev-evidence')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def safe(s):
 import re
 return re.sub(r'[^a-zA-Z0-9_.-]','_',s)[:100]
def scan_units(root):
 for group in GROUPS:
  base=root/group
  if not base.is_dir():continue
  if group in ('tbe-evidence','hidev-evidence'):
   yield group,'full-evidence',base
   continue
  for first in sorted(base.iterdir()):
   if not first.is_dir():continue
   if group in ('classic-runs','extra-proxy-runs'):
    for second in sorted(first.iterdir()):
     if second.is_dir():yield group,first.name+'__'+second.name,second
   else:yield group,first.name,first
def copy_support(root,out):
 """Copy task scripts, manifests, adapters and historical identity inputs."""
 dirs=('classic-harness','unified-quant-harness','unified-quant-extra-harness','extra-proxy-harness','deepgemm-profile-harness','deepgemm-transform-harness','deepgemm-mix-harness','deepgemm-dequant-harness','deepgemm-paged-meta-harness','deepgemm-mgroup-harness','deepgemm-bf16-mgroup-harness','deepgemm-dequant-mgroup-harness','deepgemm-sleep-static-audit','deepgemm-paged-prepare-static-audit','deepgemm-dequant-direct-static-audit','deepgemm-pilot-direct-static-audit','deepgemm-sparse-meta-static-audit','head-bwd-static-audit','mega28-profile-harness',
       'topk-history','hash-history','fused-history','mhc-history','runner-version-evidence')
 files=[x for x in root.iterdir() if x.is_file() and not x.is_symlink() and x.suffix.lower() in ('.py','.sh','.json','.csv','.md','.log','.txt')]
 bases=[root/name for name in dirs]+list(root.glob('*-queue-hidev-npu0'))+list(root.glob('*-smoke-hidev-npu0'))
 for base in bases:
  if base.is_dir():
   entries=list(base.rglob('*'));assert not any(x.is_symlink() for x in entries),f'unresolved symlink in {base}'
   files.extend(x for x in entries if x.is_file())
 records=[]
 for src in sorted(files):
  rel=src.relative_to(root);dest=out/'support'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
  digest=sha(src);assert sha(dest)==digest
  records.append({'source_path':rel.as_posix(),'support_path':dest.relative_to(out).as_posix(),'bytes':src.stat().st_size,'sha256':digest})
 path=out/'support.jsonl'
 with path.open('w',encoding='utf8',newline='\n') as f:
  for x in records:f.write(json.dumps(x,ensure_ascii=False)+'\n')
 return len(records),sha(path)
def archive_unit(root,out,group,name,d,part_bytes,files_manifest,tables_manifest):
 unit=f'{safe(group)}/{safe(name)}';file_records=[];table_records=[]
 archive_dir=out/'archives'/unit;archive_dir.mkdir(parents=True,exist_ok=False)
 with tempfile.TemporaryDirectory(prefix='puma-profile-archive-') as tmp:
  archive=Path(tmp)/'content.tar.gz'
  entries=list(d.rglob('*'))
  assert not any(x.is_symlink() for x in entries),f'unresolved symlink in {d}'
  members=sorted(x for x in entries if x.is_file())
  assert members,(group,name)
  with tarfile.open(archive,'w:gz',compresslevel=5,format=tarfile.PAX_FORMAT) as tar:
   for src in members:
    rel=src.relative_to(root).as_posix();digest=sha(src)
    record={'source_path':rel,'bytes':src.stat().st_size,'sha256':digest,'archive':unit,'member':rel}
    file_records.append(record);tar.add(src,arcname=rel,recursive=False)
    if src.suffix.lower()=='.csv':
     tag=hashlib.sha256(rel.encode()).hexdigest()[:16]
     dest=out/'tables'/unit/tag/src.name;dest.parent.mkdir(parents=True,exist_ok=False);shutil.copyfile(src,dest)
     assert sha(dest)==digest
     table_records.append({'source_path':rel,'table_path':dest.relative_to(out).as_posix(),'sha256':digest,'archive':unit,'member':rel})
  expected={x['member']:x for x in file_records}
  with tarfile.open(archive,'r:gz') as tar:
   for info in tar:
    assert info.isfile() and info.name in expected
    rec=expected.pop(info.name);h=hashlib.sha256();size=0
    with tar.extractfile(info) as f:
     for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk);size+=len(chunk)
    assert size==rec['bytes'] and h.hexdigest()==rec['sha256'],info.name
  assert not expected
  archive_hash=sha(archive);parts=[]
  with archive.open('rb') as f:
   i=0
   while True:
    chunk=f.read(part_bytes)
    if not chunk:break
    dest=archive_dir/f'part-{i:04d}';dest.write_bytes(chunk)
    parts.append({'path':dest.relative_to(out).as_posix(),'bytes':len(chunk),'sha256':sha(dest)});i+=1
  h=hashlib.sha256()
  for part in parts:
   with (out/part['path']).open('rb') as f:
    for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  assert h.hexdigest()==archive_hash
  desc={'archive':unit,'source_dir':d.relative_to(root).as_posix(),'archive_sha256':archive_hash,
        'archive_bytes':archive.stat().st_size,'parts':parts,'member_count':len(file_records),'csv_count':len(table_records)}
 for x in file_records:files_manifest.write(json.dumps(x,ensure_ascii=False)+'\n')
 for x in table_records:tables_manifest.write(json.dumps(x,ensure_ascii=False)+'\n')
 return desc
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
 ap.add_argument('--part-mib',type=int,default=45);args=ap.parse_args()
 root=args.root.resolve(strict=True);out=args.out.resolve();assert root.is_dir() and 1<=args.part_mib<=90
 assert not out.exists() and not out.is_relative_to(root),'create an isolated new output directory outside capture root'
 out.mkdir(parents=True);units=[]
 with (out/'files.jsonl').open('w',encoding='utf8',newline='\n') as files,(out/'tables.jsonl').open('w',encoding='utf8',newline='\n') as tables:
  for group,name,d in scan_units(root):
   result=archive_unit(root,out,group,name,d,args.part_mib*1024*1024,files,tables);units.append(result)
   print('VERIFIED',result['archive'],'files',result['member_count'],'csv',result['csv_count'],flush=True)
 support_count,support_hash=copy_support(root,out)
 doc={'version':1,'source_root':str(root),'part_bytes':args.part_mib*1024*1024,'units':units,
      'files_jsonl_sha256':sha(out/'files.jsonl'),'tables_jsonl_sha256':sha(out/'tables.jsonl'),
      'support_count':support_count,'support_jsonl_sha256':support_hash,
      'note':'original capture windows preserved separately; CSV copies retain original bytes'}
 (out/'manifest.json').write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 print('ARCHIVE_VERIFIED units',len(units),'members',sum(x['member_count'] for x in units),'csv',sum(x['csv_count'] for x in units),flush=True)
if __name__=='__main__':main()
