"""Archive early post capture or its standalone preflight failure."""
import importlib.util,subprocess,sys,shutil
from pathlib import Path
r=Path('/workspace/expert-profile-backfill-20261109-hidev');q=r/'early-expand-single-20261111-hidev-npu0';assert (q/'exit.txt').exists()
if (q/'attempt.txt').exists():
 group='early-expand-single-runs-20261111';label='mhc-expand-fwd-bf16-n512-h4096-m4';path=r/group/label;unit=path/'hidev-npu0'/(q/'attempt.txt').read_text().strip();evidence=unit/'queue-evidence';assert not evidence.exists();evidence.mkdir()
 for n in ('exit.txt','console.log','run.sh','attempt.txt'):shutil.copy2(q/n,evidence/n)
 if (q/'preflight').is_dir():shutil.copytree(q/'preflight',evidence/'preflight')
else:group=q.name;label='preflight';path=q
assert path.is_dir();spec=importlib.util.spec_from_file_location('archive_captures',r/'archive-captures.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.GROUPS=(group,)
subprocess.run([sys.executable,'-B',str(r/'scan-public-archive.py'),str(path)],check=True);m.scan_units=lambda root:iter([(group,label,path)])
def no_support(source,out):
 p=out/'support.jsonl';p.write_bytes(b'');return 0,m.sha(p)
m.copy_support=no_support
sys.argv=['archive-captures.py','--root',str(r),'--out','/workspace/expert-profile-backfill-20261109-early-expand-single-20261111'];m.main()
