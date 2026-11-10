echo __HARNESS_ROOT_FIX_BEGIN__
python3 -B <<'PY'
from pathlib import Path
import ast,hashlib,json,os
r=Path('/workspace/expert-profile-backfill-20261109-hidev');out=r/'harness-root-fix-20261110';out.mkdir(exist_ok=False)
items=[('extra-proxy-mhc-multilayer-app-harness/extra_multilayer.py',None),('extra6-finalize-app-harness/extra_finalize_retry.py','extra6-finalize-app-smoke-hidev-npu0'),('extra6-post-fwd-app-harness/extra_post_fwd_retry.py','extra6-post-fwd-app-smoke-hidev-npu0')]
changes=[]
for rel,q in items:
 p=r/rel;old=p.read_text();assert old.count("os.environ.get('TILEKERNELS_ROOT', str(Path(__file__).resolve().parents[4]))")==1
 if q:assert not (r/q/'attempt.txt').exists(),f'{q} already started; refuse to edit'
 new=old.replace("os.environ.get('TILEKERNELS_ROOT', str(Path(__file__).resolve().parents[4]))","(os.environ['TILEKERNELS_ROOT'] if 'TILEKERNELS_ROOT' in os.environ else str(Path(__file__).resolve().parents[4]))")
 ast.parse(new);oldb=old.encode();newb=new.encode();backup=out/(p.parent.name+'-'+p.name+'.original');backup.write_bytes(oldb)
 # Independently evaluate the assignment with a shallow path; os.environ.get eagerly evaluated the old fallback.
 node=next(x for x in ast.parse(new).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ROOT' for t in x.targets))
 env={'Path':Path,'os':os,'__file__':'/tmp/a.py'};os.environ['TILEKERNELS_ROOT']='/workspace/example';exec(compile(ast.Module(body=[node],type_ignores=[]),str(p),'exec'),env);assert env['ROOT']==Path('/workspace/example')
 tmp=p.with_suffix('.py.fix-tmp');tmp.write_bytes(newb);tmp.replace(p)
 changes.append({'path':rel,'original_backup':str(backup.relative_to(r)),'original_sha256':hashlib.sha256(oldb).hexdigest(),'new_sha256':hashlib.sha256(newb).hexdigest(),'test':'shallow __file__, explicit TILEKERNELS_ROOT'})
(out/'changes.json').write_text(json.dumps(changes,indent=2)+'\n');print(json.dumps(changes,indent=2))
PY
echo __HARNESS_ROOT_FIX_END__
