"""Add official 4096-row forward shapes after the active manifest finishes."""
import json
from pathlib import Path

root=Path(__file__).resolve().parent
manifest=json.loads((root/'cases-expanded.json').read_text())
cases=manifest['cases']
for a,b,target in [('bf16','bf16','bf16_gemm_impl'),('fp8','fp8','fp8_gemm_impl'),
                   ('fp4','fp4','fp8_gemm_impl'),('fp8','fp4','fp8_dequant_gemm_impl')]:
    m,n,k=4096,576,7168
    cases.append({'id':f'gemm-{a}{b}-nt-k-m{m}-n{n}-k{k}','family':'gemm','target':target,
                  'api':f'{"bf16" if a=="bf16" else "fp8_fp4"}_gemm_nt',
                  'a_dtype':a,'b_dtype':b,'trans':'nt','a_major':'K','b_major':'K',
                  'm':m,'n':n,'k':k})
for fp4 in (False,True):
    for q,k,heads,block,max_blocks,page in ((4,256,8,8,16,64),(8,512,12,16,16,128)):
        cases.append({'id':f'paged-sparse-first-{int(fp4)}-q{q}-k{k}-h{heads}-b{block}-p{page}',
            'family':'sparse','target':'paged_sparse_mqa_logits_impl','api':'fp8_fp4_paged_sparse_mqa_logits',
            'q':q,'k':k,'heads':heads,'fp4':fp4,'paged':True,'sparse_block':block,
            'max_blocks':max_blocks,'page':page,'sparse_phase':'first'})
assert len({c['id'] for c in cases})==len(cases)
(root/'cases-next.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
print('planned cases:',len(cases))
