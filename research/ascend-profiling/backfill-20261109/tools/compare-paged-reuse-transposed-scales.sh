#!/usr/bin/env bash
set -Eeuo pipefail
echo __COMPARE_PAGED_SCALE_TRANSPOSE_BEGIN__
python3 - <<'PY'
from pathlib import Path
import struct
r=Path('/workspace/expert-profile-backfill-20261109-hidev/deepgemm-runs'); first=r/'paged-sparse-first-0-q4-k256-h8-b8-p64/hidev-npu0/attempt-002'; reuse=r/'paged-sparse-fp8-q4-k256-h8-b8/hidev-npu0/attempt-001'
b=(first/'paged-sparse-metadata-before-1570403.bin').read_bytes();a=(first/'paged-sparse-metadata-after-1570403.bin').read_bytes();u=(reuse/'paged-sparse-metadata-before.bin').read_bytes();ko=0x4000;co=0x15a00;nr=56
ranges=[struct.unpack_from('<II',b,ko+8*i) for i in range(nr)];idx={j for lo,hi in ranges for j in range(lo,hi)};bad=[];checked=0
for j in sorted(idx):
 w=struct.unpack_from('<10I',b,ko+nr*8+j*40);page=w[0];valid=((w[1]>>4)&127)*8;n=((valid+63)//64)*64;start=co+page*64*132+n*128
 for t in range(valid):
  for pair in range(2):
   off=start+(t//16)*64+pair*32+(t%16)*2; checked+=2
   if a[off:off+2]!=u[off:off+2]:bad.append((j,page,t,pair,a[off:off+2].hex(),u[off:off+2].hex()))
print('active_descriptors',len(idx),'bytes_checked',checked,'mismatched_2byte_values',len(bad))
for item in bad[:10]: print('record,page,token,pair,FIRST_after,REUSE_before',*item)
print('CAVEAT: compare uses source documented 16-token transpose; does not prove old postwarm state')
PY
echo __COMPARE_PAGED_SCALE_TRANSPOSE_END__
