"""Verify immutable historical metadata for each precision-labelled target."""
import hashlib,json,sys
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');target,old,result=sys.argv[1:];case=target.split('/')[-1];entries=json.loads((root/'precision-preapply-batch-history-20261110.json').read_text())['cases'];v,=(x for x in entries if x['target']==case)
for path,key in ((Path(old),'capture_record_sha256'),(Path(result),'capture_result_sha256')):assert hashlib.sha256(path.read_bytes()).hexdigest()==v[key],path
record=json.loads(Path(old).read_text());assert record['status']=='profiled_precision_failed' and record['reference_check']=='failed' and record['group']=='mhc_pre_apply_mix_bwd';print('HISTORICAL_PRECISION_FAILURE_AND_HASHES_VERIFIED',case)
