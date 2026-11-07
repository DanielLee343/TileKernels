"""Recheck finite values and both references sequentially on the existing inputs."""
import json
from pathlib import Path
import subprocess
import sys

root=Path('/workspace/tilekernels-replay-watch-20261107')
names=('normalize_check','preapply_compare','post_compare')
for output in ('normalize-comparison.json','preapply-comparison.json','preapply-record.json',
               'post-comparison.json','post-record.json'):
    p=root/output
    if p.exists():p.rename(root/(output+'.v1'))
results=[]
for name in names:
    with (root/(name+'-finite.log')).open('w') as log:
        p=subprocess.run([sys.executable,'-B',str(root/(name+'.py'))],stdout=log,stderr=subprocess.STDOUT,timeout=900)
    results.append({'script':name,'returncode':p.returncode})
    (root/'accuracy-progress.json').write_text(json.dumps({'status':'running','results':results},indent=2))
(root/'accuracy-progress.json').write_text(json.dumps({'status':'finished','results':results},indent=2))
