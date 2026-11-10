echo __TEN03_IDENTITY_FILES_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;p="$r/extra-proxy-runs/unified-extra5/mhc_multilayer_recompute-03/hidev-npu0/attempt-001/detail"
python3 - "$p" <<'PY'
from pathlib import Path
import sys,json
p=Path(sys.argv[1]);
for f in sorted(p.glob('application-*.json')):
 a=json.loads(f.read_text());pid=f.stem.removeprefix('application-');print('PID',pid,'status',a.get('status'),'matched',a.get('matched'),'precision',str(a.get('precision',''))[:220],'error',str(a.get('error',''))[-1000:].replace('\n',' | '),'addr',(p/('tensor-addresses-'+pid+'.json')).exists(),'source',(p/('generated-kernel-'+pid+'.cpp')).exists())
PY
echo __TEN03_IDENTITY_FILES_END__
