"""Add the supported 64-channel MQA head and an 8-expert M-group shape."""
import json
from pathlib import Path

root=Path(__file__).resolve().parent
manifest=json.loads((root/'cases-next.json').read_text());cases=manifest['cases']
for fp4 in (False,True):
    cases.append({'id':f'mqa-{int(fp4)}-q32-k512-h32-d64-fullrange','family':'mqa',
        'target':'mqa_logits_impl','api':'fp8_fp4_mqa_logits','q':32,'k':512,
        'heads':32,'head_dim':64,'fp4':fp4,'mode':'FullRange'})
for a,b,target in [('bf16','bf16','bf16_gemm_impl'),('fp8','fp8','fp8_gemm_impl'),
                   ('fp4','fp4','fp8_gemm_impl'),('fp8','fp4','fp8_dequant_gemm_impl')]:
    kind='bf16' if a=='bf16' else 'fp8_fp4'
    cases.append({'id':f'mgroup-{a}{b}-nt-g8-m32-n256-k512','family':'gemm','target':target,
        'api':f'm_grouped_{kind}_gemm_nt_contiguous','a_dtype':a,'b_dtype':b,
        'gemm_type':'m_grouped','trans':'nt','a_major':'K','b_major':'K',
        'groups':8,'m':32,'n':256,'k':512})
assert len({c['id'] for c in cases})==len(cases)
(root/'cases-last.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
print('planned cases:',len(cases))
