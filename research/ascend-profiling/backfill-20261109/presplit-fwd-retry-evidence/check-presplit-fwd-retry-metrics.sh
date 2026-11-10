echo __PRESPLIT_FWD_RETRY_METRICS_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;p="$r/classic-runs/sixth/presplit-fwd-01/hidev-npu0/attempt-003/detail/profile.log"
grep 'processedRecord:' "$p" | tail -n 3
python3 - "$p" <<'PY'
import re,sys,collections
s=open(sys.argv[1],errors='replace').read();a=[x for x in s.splitlines() if 'DBI record core:' in x and 'dst:(type:GM;' in x and 'src:(type:UB;' in x];print('events',len(a),'PCs',collections.Counter(re.search(r'pc:(0x[0-9a-f]+)',x).group(1) for x in a))
PY
echo __PRESPLIT_FWD_RETRY_METRICS_END__
