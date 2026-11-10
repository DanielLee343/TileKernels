"""Compare frozen historical prewarm contract and new post-warmup snapshots."""
import hashlib,importlib.util,json,re,sys
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');case,attempt=sys.argv[1:];assert case=='paged-sparse-fp8-q4-k256-h8-b8' and re.fullmatch(r'attempt-[0-9]+',attempt)
p=root/'deepgemm-runs'/case/'hidev-npu0'/attempt;h=root/'deepgemm-paged-reuse-address-harness';history=root/'deepgemm-paged-sparse-app-harness/history'/case/'profile.json';old=json.loads(history.read_text());assert old['status']=='passed'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();apps=sorted(p.glob('profile-[0-9]*.json'));assert len(apps)>=2;records=[]
for f in apps:
 pid=f.stem.removeprefix('profile-');a=json.loads(f.read_text());assert a['status']=='passed' and a['target_input']==old['target_input']
 pre=p/('frozen-prewarm-'+pid+'.bin');warm=p/('frozen-after-warmups-'+pid+'.bin');after=p/('frozen-after-target-'+pid+'.bin');state=p/('frozen-post-warmup-state-'+pid+'.json')
 assert all(x.is_file() for x in (pre,warm,after,state));meta=old['target_input']['kwargs']['metadata'];assert sha(pre)==meta['sha256'] and pre.stat().st_size==warm.stat().st_size==after.stat().st_size==meta['shape'][0]
 info=json.loads(state.read_text());assert sha(warm)==info['sha256'];af=p/('frozen-addresses-'+pid+'.json');assert af.is_file();addresses=json.loads(af.read_text());assert addresses['kwargs']['metadata']['dtype']=='torch.uint8' and addresses['returned']['dtype']=='torch.bfloat16'
 if records:assert addresses==first_addresses,'application processes differ in allocation addresses'
 else:first_addresses=addresses
 records.append({'pid':pid,'profile':f.name,'profile_sha256':sha(f),'prewarm':pre.name,'prewarm_sha256':sha(pre),'after_warmups':warm.name,'after_warmups_sha256':sha(warm),'after_target':after.name,'after_target_sha256':sha(after),'addresses':af.name,'addresses_sha256':sha(af),'state':info})
command=json.loads((p/'detail/command.json').read_text());assert '--replay-mode=application' in command and '--warm-up=5' in command
spec=importlib.util.spec_from_file_location('frozen_collector',h/'campaign-13/collect.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);manifest=json.loads((h/'campaign-13/cases.json').read_text());selected,=(x for x in manifest['cases'] if x['id']==case)
capture=mod.inspect_profile(selected,p/'detail/capture',root/'deepgemm-cache'/case);jit=Path(capture['jit_directory']);historical=root/'deepgemm-paged-sparse-app-harness/history'/case/'kernel.asc';assert sha(historical)==sha(jit/'kernel.asc')
prior=root/'deepgemm-runs'/case/'hidev-npu0/attempt-001/paged-sparse-metadata-before.bin';assert prior.is_file();prior_sha=sha(prior);warms={x['after_warmups_sha256'] for x in records};posts={x['after_target_sha256'] for x in records}
out={'case':'campaign-13/'+case,'status':'prewarm_verified_postwarm_comparison','historical_prewarm_input_match':True,'historical_jit_source_match':True,'processes':len(records),'historical_prewarm_metadata_sha256':old['target_input']['kwargs']['metadata']['sha256'],'distinct_after_warmups_sha256':sorted(warms),'distinct_after_target_sha256':sorted(posts),'previous_reuse_window_metadata_sha256':prior_sha,'previous_reuse_matches_all_postwarm':warms=={prior_sha},'capture':capture,'records':records,'scope':'reconstruction follows archived prewarm order; equality is observed only across new application processes, not a byte snapshot of historical postwarm state; address audit remains pending'}
(p/'frozen-reuse-address-investigation.json').write_text(json.dumps(out,indent=2)+'\n');print('FROZEN_REUSE_ADDRESS_PROCESSES',len(records),'POSTWARM_HASHES',len(warms),'PRIOR_MATCH',warms=={prior_sha},'POST_TARGET_HASHES',len(posts))
