set -Eeuo pipefail
echo __REUSE3_ACTIVE_COMPARE_BEGIN__
python3 -B <<'PY'
from pathlib import Path
import struct,json
r=Path('/workspace/expert-profile-backfill-20261109-hidev/deepgemm-runs');first=r/'paged-sparse-first-0-q4-k256-h8-b8-p64/hidev-npu0/attempt-002';old=r/'paged-sparse-fp8-q4-k256-h8-b8/hidev-npu0/attempt-001';new=r/'paged-sparse-fp8-q4-k256-h8-b8/hidev-npu0/attempt-003';j=json.loads((new/'frozen-reuse-address-investigation.json').read_text());rec=j['records'][0]
b=(new/rec['prewarm']).read_bytes();a=(new/rec['after_warmups']).read_bytes();u=(old/'paged-sparse-metadata-before.bin').read_bytes();assert len(b)==len(a)==len(u)==4076032
ko=0x4000;po=0x11e00;co=0x15a00;nr=56;ranges=[struct.unpack_from('<II',b,ko+8*i) for i in range(nr)];idx={j for lo,hi in ranges for j in range(lo,hi)}
for name,(l,h) in {'mapping':(0,ko),'ranges':(ko,ko+nr*8),'physical':(po,co),'compact_all':(co,len(b))}.items():print(name,'equal',a[l:h]==u[l:h],'diff_bytes',sum(x!=y for x,y in zip(a[l:h],u[l:h])))
print('active_descriptors_equal',all(a[ko+nr*8+j*40:ko+nr*8+(j+1)*40]==u[ko+nr*8+j*40:ko+nr*8+(j+1)*40] for j in idx),'count',len(idx))
data=scale=bad_data=bad_scale=0
for j in sorted(idx):
 w=struct.unpack_from('<10I',b,ko+nr*8+j*40);page=w[0];valid=((w[1]>>4)&127)*8;n=((valid+63)//64)*64;start=co+page*64*132
 for frag in range(4):
  lo=start+frag*n*32;hi=lo+valid*32;data+=hi-lo;bad_data+=sum(x!=y for x,y in zip(a[lo:hi],u[lo:hi]))
 start+=n*128
 for t in range(valid):
  for pair in range(2):
   off=start+(t//16)*64+pair*32+(t%16)*2;scale+=2;bad_scale+=sum(x!=y for x,y in zip(a[off:off+2],u[off:off+2]))
print('active_data_bytes',data,'different',bad_data,'active_scale_bytes',scale,'different',bad_scale)
print('CAVEAT: this compares new frozen pre-target state with a separate old REUSE window, not unrecorded original pre-target metadata')
PY
echo __REUSE3_ACTIVE_COMPARE_END__
