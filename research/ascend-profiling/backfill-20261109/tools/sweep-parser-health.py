"""Read-only full DBI parser health sweep for indexed audited hidev captures."""
import gzip,json,re,sys,time
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');d=json.loads(gzip.decompress((root/'hidev-capture-index.json.gz').read_bytes()));fields=('droppedRecord','memoryCopyFailed','invalidParam','overflow','invalidDataCount','memoryCorruption','invalidRecordType','outOfBoundsRead')
out=[];missing=[];ok=0
for item in d['cases']:
 p=Path(item['raw_dir'])/'profile.log';found=0;errors=[]
 if not p.is_file():missing.append((item['target'],'profile.log missing'));continue
 with p.open(errors='replace') as f:
  for line in f:
   if 'processedRecord:' not in line:continue
   found+=1
   for k in fields:
    m=re.search(r'\b'+k+r'\s*:?\s*(\d+)',line)
    if not m:errors.append('missing '+k)
    elif int(m.group(1)):errors.append(k+'='+m.group(1))
   r=re.search(r'receivedPacket\s+(\d+),\s*processedPacket\s+(\d+)',line)
   if not r:errors.append('missing packet counts')
   elif r.group(1)!=r.group(2):errors.append('packet mismatch '+r.group(1)+'/'+r.group(2))
   z=re.search(r'each record type process fail count\s+([0-9, ]+)',line)
   if not z:errors.append('missing per-type failure counts')
   elif any(int(v) for v in re.findall(r'\d+',z.group(1))):errors.append('nonzero per-type failures')
 if not found:missing.append((item['target'],'no parser summary'))
 elif errors:out.append({'target':item['target'],'summaries':found,'errors':sorted(set(errors)),'path':str(p)})
 else:ok+=1
result={'source_index_cases':len(d['cases']),'ok':ok,'flagged':out,'missing':missing,'fields_checked':list(fields)+['packet count equality','per-type failures'],'status':'read-only audit; does not prove address coverage','timestamp_unix':time.time()}
(root/'hidev-parser-health-sweep.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
