"""Create a reviewable, unexecuted case inventory from the pinned TK tests.

This is intentionally a proposal, not an execution or an assertion that every
case runs on the selected NPU. The source's parameter generators are evaluated
using CPU-only stubs; device tensors and NPU APIs are never called.
"""
from __future__ import annotations

import ast
from collections import Counter
from itertools import product
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TK = next(p for p in Path(__file__).resolve().parents if (p / '.git').exists())
TESTS = TK / 'tests'
OUT = Path(__file__).resolve().parent


def read_generator_environment():
    path = TK / 'tile_kernels/testing/generator.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    names = {'generate_samples', 'generate_num_tokens', 'generate_hidden_sizes',
             'generate_cast_config', 'generate_num_sms', 'generate_moe_params'}
    defs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), *defs], type_ignores=[])
    env = {'product': product, 'is_precompile': lambda: False,
           'align': lambda x, a: (x + a - 1) // a * a,
           # The pinned config returns cube_core_num; get_num_vec_cores doubles it.
           # 28 is the working value implied by the observed 56 AIV cores.
           'get_device_num_sms': lambda: 28}
    exec(compile(ast.fix_missing_locations(module), str(path), 'exec'), env)
    env.update(is_ascend=lambda: True, itertools=itertools,
               DTYPES={'fp32': 'fp32', 'bf16': 'bf16'}, SR_PAIRS={('fp32', 'bf16')})
    return env


ENV = read_generator_environment()


def from_test(relative: str, func='generate_test_params', level=1):
    p = TESTS / relative
    tree = ast.parse(p.read_text(encoding='utf-8'))
    body = []
    for n in tree.body:
        if isinstance(n, ast.Assign) and all(isinstance(x, ast.Name) and x.id in {'_CORE_CONFIGS', '_FULL_CONFIGS'} for x in n.targets):
            body.append(n)
        if isinstance(n, ast.FunctionDef) and n.name == func:
            n.decorator_list = []
            body.append(n)
    if not any(isinstance(n, ast.FunctionDef) and n.name == func for n in body):
        raise ValueError((relative, func))
    mod = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), *body], type_ignores=[])
    env = dict(ENV)
    exec(compile(ast.fix_missing_locations(mod), str(p), 'exec'), env)
    return list(env[func](level))


def canon(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def select(candidates, target=20):
    """Deterministic greedy choice to cover values and pairs, not measured results."""
    uniq = {canon(c): c for c in candidates}
    pool = [uniq[k] for k in sorted(uniq)]
    if len(pool) <= target:
        return pool
    features = []
    for c in pool:
        pairs = [(k, canon(v)) for k, v in sorted(c.items())]
        fs = {('v', k, v) for k, v in pairs}
        fs |= {('p', a[0], a[1], b[0], b[1]) for i, a in enumerate(pairs) for b in pairs[i+1:]}
        features.append(fs)
    chosen, covered, remaining = [], set(), set(range(len(pool)))
    # Seed actual numeric extremes before greedy categorical/pair coverage.
    # Lexical order of JSON alone would otherwise pick mostly similar sizes.
    numeric_keys = ['num_tokens','numel','num_rows','num_partials','n1','n0',
                    'hidden','hidden_size','num_experts','shape']
    for key in numeric_keys:
        vals=[]
        for i in remaining:
            v=pool[i].get(key)
            if key=='shape' and isinstance(v,(list,tuple)) and len(v)==1: v=v[0]
            if isinstance(v,(int,float)) and not isinstance(v,bool): vals.append((v,i))
        if len(vals)<2: continue
        for _, idx in (min(vals), max(vals)):
            if idx in remaining and len(chosen)<target:
                chosen.append(pool[idx]); covered.update(features[idx]); remaining.remove(idx)
    while len(chosen)<target:
        best = max(remaining, key=lambda i: (len(features[i] - covered), -i))
        chosen.append(pool[best]); covered.update(features[best]); remaining.remove(best)
    return chosen


groups = []


def add(name, src, test, candidates, contract, history='库存无对应族', note='', target=20, extras=()):
    official={canon(c) for c in candidates}
    candidates=list(candidates)+list(extras)
    flattened_sources={'tile_kernels/mhc/expand_asc.py','tile_kernels/mhc/head_compute_mix_asc.py',
                       'tile_kernels/mhc/post_asc.py','tile_kernels/mhc/pre_apply_mix_asc.py',
                       'tile_kernels/mhc/pre_split_mixes_asc.py','tile_kernels/mhc/sinkhorn_asc.py'}
    if src in flattened_sources:
        # The pinned wrappers flatten n0*n1 before the kernel. With the same
        # other parameters, n0=1,n1=1024 and n0=2,n1=512 are one kernel case.
        dedup={}
        for c in candidates:
            k=dict(c); k['num_tokens']=k.pop('n0')*k.pop('n1'); key=canon(k)
            if key not in dedup or (canon(c) in official and canon(dedup[key]) not in official):
                dedup[key]=c
        candidates=list(dedup.values())
    cases = select(candidates, target)
    groups.append(dict(id=name, source=src, test=test, contract=contract,
                       historical_coverage=history, note=note,
                       official_candidate_pool=len(official),
                       candidate_pool=len({canon(c) for c in candidates}),
                       extended_cases=[canon(c) for c in cases if canon(c) not in official], cases=cases))


def source(group, name):
    return f'tile_kernels/{group}/{name}_asc.py'


for name, fname, contract, history in [
    ('engram_fused_weight', 'engram_fused_weight', 'wh/we：BF16 [hc,hidden]；输出 FP32 [hc,hidden]。', '已有 5 个 case'),
    ('engram_gate_fwd', 'engram_gate_fwd', 'x：BF16 [num_tokens,hc,hidden]；kv：BF16 [num_tokens,hc+1,hidden]；融合权重 FP32 [hc,hidden]；可选 mask。', ''),
    ('engram_gate_bwd', 'engram_gate_bwd', '与 forward 同输入，另有 BF16 梯度 [num_tokens,hc,hidden]；可选 mask。', ''),
    ('engram_grad_w_reduce', 'engram_grad_w_reduce', '输入 FP32 [14,4,hidden] 和两份 BF16 [4,hidden] 权重；14 按目前 28 个 Cube 核的测试条件推导，采集前核对。', ''),
    ('engram_hash', 'engram_hash', 'token IDs INT32 [num_tokens,ngram]；multiplier INT64 [layers,ngram]；其他表按上游测试生成。', '已有 4 个 case'),
]:
    t=f'engram/test_{fname}.py'
    candidates=from_test(t)
    if name=='engram_grad_w_reduce':
        # The test ignores params['num_sms'] on Ascend; do not count it twice.
        candidates=[{'hidden':c['hidden']} for c in candidates]
    extras=[]
    if name=='engram_fused_weight':
        extras=[{'hc':4,'hidden':h} for h in range(256,8193,256)]
    if name=='engram_grad_w_reduce':
        extras=[{'hidden':h} for h in [64,128,192,256,320,384,512,768,1024,1280,1536,1792,2048,2560,3072,3584,4096,5120,6144,7168]]
    if name=='engram_hash':
        extras=[dict(num_tokens=n,ngram=k,with_mask=m,layers=2,tables=8)
                for n,k,m in product([1,128,1024,8192],[3,4],[False,True])]
    add(name, source('engram', fname), t, candidates, contract, history or '库存无对应族',
        note='标注“扩展”的组合按源码限制补充，尚未经设备验证；并非上游完整测试原参数。',extras=extras)

t='engram/test_engram_sinkhorn.py'
for n, fun, desc in [
    ('engram_sinkhorn_momentum_update','generate_momentum_test_params','grad 和 momentum 各为 [numel]，dtype 分别由 grad_dtype、momentum_dtype 指定；beta1 和 nesterov 如 case。'),
    ('engram_sinkhorn_step','generate_row_step_test_params','matrix FP32 [num_rows,head_dim]，row_scale FP32 [num_rows]，col_scale FP32 [head_dim]。'),
    ('engram_sinkhorn_step_reduce','generate_step_reduce_test_params','partial FP32 [num_partials,head_dim]，输出 FP32 [head_dim]。'),
    ('engram_sinkhorn_finalize','generate_row_step_test_params','matrix FP32 [num_rows,head_dim]，row_scale FP32 [num_rows]，col_scale FP32 [head_dim]；alpha=sqrt(head_dim)。'),
]:
    extras=[]
    if fun=='generate_row_step_test_params':
        extras=[{'num_rows':r,'head_dim':h,'eps':1e-20} for r,h in product([1,128,512,1024,4096,8192,16384,32768],[256,5120])]
    if fun=='generate_step_reduce_test_params':
        extras=[{'num_partials':p,'head_dim':h} for p,h in product([1,18,28,56,112],[256,512,1024,2048,5120])]
    add(n, source('engram','engram_sinkhorn'), t, from_test(t,fun), desc, extras=extras,
        note='扩展项沿用上游支持的 FP32 输入，设备合法性和输出精度待验证；大矩阵先检查显存。')


def rows(keys, vals, **fixed):
    return [dict(zip(keys, v), **fixed) for v in product(*vals)]


t='mhc/test_expand.py'; c=rows(('n0','n1','hidden'),([1,2],[1024,4096],[1280,1920,2560,4224,5120,7168]),mhc_mult=4)
extra=rows(('n0','n1','hidden'),([1],[128,512,8001],[1280,1920,2560,4224,5120,7168]),mhc_mult=4)
add('mhc_expand_fwd',source('mhc','expand'),t,c,'x BF16 [n0,n1,hidden]；输出 BF16 [n0,n1,4,hidden]。','已有 1 个 case',extras=extra)
add('mhc_expand_bwd',source('mhc','expand'),t,c,'输出梯度 BF16 [n0,n1,4,hidden]；返回 BF16 [n0,n1,hidden]。',extras=extra)
t='mhc/test_head_compute_mix.py'; c=rows(('n0','n1'),([1,2],[1001,1024,4096,24576]),mhc_mult=4,eps=0.01)
for name in ('mhc_head_compute_mix_fwd','mhc_head_compute_mix_bwd'):
    extra=rows(('n0','n1'),([1],[1,17,64,127,128,257,511,512,513,2048,2049,4097,8001,8192,16384,16385]),mhc_mult=4,eps=0.01)
    add(name,source('mhc','head_compute_mix'),t,c,'input_mix FP32 [n0,n1,4]；scale FP32 [1]，base FP32 [4]；反向另需同形状梯度。', 'forward 已有 2 个 case' if name.endswith('fwd') else '库存无对应族', note='补充不同序列长度覆盖小规模和尾部；扩展项尚需设备验证。',extras=extra)
t='mhc/test_post.py'; c=rows(('n0','n1','hidden'),([1,2],[4096],[1280,2560,5120,7168]),mhc_mult=4)
for name in ('mhc_post_fwd','mhc_post_bwd'):
    extra=rows(('n0','n1','hidden'),([1,2],[512,1024,2048,8192],[1280,2560,5120,7168]),mhc_mult=4)
    add(name,source('mhc','post'),t,c,'x BF16 [n0,n1,hidden]；residual BF16 [n0,n1,4,hidden]；post_mix FP32 [n0,n1,4,1]；comb_mix FP32 [n0,n1,4,4]；反向另有 BF16 输出梯度。','backward 已有 7 个历史 case' if name.endswith('bwd') else '库存无对应族',note='扩展 token 规模；旧 backward 的其它 shape 另见原库存，扩展项待验证。',extras=extra)
t='mhc/test_pre_apply_mix.py'; c=rows(('n0','n1','hidden'),([1,2],[1024,4096],[1280,2560,4096,5120,7168]),mhc_mult=4)
extra=rows(('n0','n1','hidden'),([1],[128,512,8001],[1280,2560,4096,5120,7168]),mhc_mult=4)
for name in ('mhc_pre_apply_mix_fwd','mhc_pre_apply_mix_bwd'):
    add(name,source('mhc','pre_apply_mix'),t,c,'x BF16 [n0,n1,4,hidden]；mix FP32 [n0,n1,4,1]；反向另有 BF16 [n0,n1,hidden] 梯度。',extras=extra)
t='mhc/test_pre_split_mixes.py'; c=rows(('n0','n1'),([1,2],[1001,1024,4096]),mhc_mult=4)
for name in ('mhc_pre_split_mixes_fwd','mhc_pre_split_mixes_bwd'):
    extra=rows(('n0','n1'),([1],[1,17,64,127,128,257,511,512,513,2048,2049,4097,8001,8192,16384,16385]),mhc_mult=4)
    add(name,source('mhc','pre_split_mixes'),t,c,'input_mixes FP32 [n0,n1,24]；scale FP32 [3]，base FP32 [24]；反向另有 pre/post/comb 梯度。',note='公开入口按实现选择具体 kernel；扩展项需核对所走分支和运行合法性。',extras=extra)
t='mhc/test_sinkhorn.py'; c=rows(('n0','n1'),([1,2],[1,1024,4096]),mhc=4,repeat=10,eps=1e-6)
for name in ('mhc_sinkhorn_fwd','mhc_sinkhorn_bwd'):
    extra=rows(('n0','n1'),([1],[17,64,127,128,257,511,512,513,1001,2048,2049,4097,8001,8192,16385,32769]),mhc=4,repeat=10,eps=1e-6)
    add(name,source('mhc','sinkhorn'),t,c,'matrix FP32 [n0,n1,4,4]；反向另需同形状 FP32 梯度。','forward 已有 18 个不同 case（含旧口径）' if name.endswith('fwd') else '库存无对应族',note='扩展序列长度，具体是否与旧 case 等价需核对 repeat 和计时口径。',extras=extra)
t='mhc/test_pre_big_fuse.py'; c=rows(('n1','hidden_size'),([512,1024,2048,8192,509,1021],[1280,2560,4096,4160,5120]),mhc_mult=4,repeat=10,n_splits=1)
add('mhc_pre_big_fuse_fwd',source('mhc','pre_big_fuse'),t,c,'目标输入：GEMM 中间量 FP32 [1,n1,24]、平方和 FP32 [1,n1]、scale FP32 [3]、base FP32 [24]、residual BF16 [n1,4,hidden_size]；输出包括 post_mix、comb_mix 和 layer_input。',note='Ascend 实际 n_splits=1；上游测试覆盖 509/1021，但源码注释声称 token 数需整除 16，这两项先验收。生成中间量的矩阵乘不应混入目标采集。')
t='mhc/test_norm_fn.py'
for name in ('mhc_fn_normw_merge_fwd','mhc_fn_normw_merge_bwd'):
    c=[{'hidden_size':h,'mhc_mult':4,'dtype':'fp32'} for h in [320,1280,2560,4096,5120,7168]]
    extra=[{'hidden_size':h,'mhc_mult':4,'dtype':'fp32'} for h in [64,128,192,256,384,512,768,1024,1536,1792,2048,3072,3584,4608,6144,8192]]
    add(name,source('mhc','norm_fn'),t,c,'fn FP32 [24,4*hidden_size]；normw FP32 [4*hidden_size]；反向另需同 fn 形状梯度。',note='仅扩展 hidden_size；该入口与 token 数无关。扩展尺寸满足源码分块整除约束，仍需设备验证。',extras=extra)
for name in ('mhc_reduce_partials_and_rmsnorm_fwd','mhc_reduce_partials_and_rmsnorm_bwd'):
    c=rows(('n1','hidden_size'),([4096,8192],[320,1280,2560,4096,5120,7168]),mhc_mult=4,n_splits=1,dtype='fp32')
    extra=rows(('n1','hidden_size'),([128,512,1024,8001],[320,1280,2560,4096,5120,7168]),mhc_mult=4,n_splits=1,dtype='fp32')
    contract=('输入全为 FP32：out_mul_splitted [1,n1,1,24]、sqrsum_splitted [1,n1,1]；输出 [n1,1,24]、[n1,1]、[n1,24]。'
              if name.endswith('fwd') else
              '输入全为 FP32：out_grad [n1,24]、out_mul [n1,1,24]、sqrsum [n1,1]；输出为后两项的同形状梯度。')
    contract+='rms_group_size=4*hidden_size、eps=1e-6；正向 n_splits=1。'
    add(name,source('mhc','norm_fn'),t,c,contract,note='扩展 token 数以覆盖不同规模；尚需设备验证。',extras=extra)
t='mhc/test_multilayer_recompute.py'; tr=ast.parse((TESTS/t).read_text(encoding='utf8'))
cs=next(ast.literal_eval(n.value) for n in tr.body if isinstance(n,ast.Assign) and any(isinstance(q,ast.Name) and q.id=='_CORRECTNESS_CASES' for q in n.targets))
c=[dict(num_layers=a,num_post=b,hidden=h,bs=1,seq=8192,mhc_mult=4) for a,b,h in cs]
extra=[dict(num_layers=1,num_post=1,hidden=h,bs=1,seq=8192,mhc_mult=4) for h in [1280,4096,5120]]
add('mhc_multilayer_recompute',source('mhc','multilayer_recompute'),t,c,'initial residual BF16 [bs,seq,4,hidden]；各层 BF16 数据与 FP32 mix 的列表按 num_layers/num_post 构造。',note='官方 17 组加 3 组扩展；大 shape 和层数需要先核对显存，不能默认可在 hidev 运行。',extras=extra)

for name, fname in [('moe_topk_gate','topk_gate'),('moe_topk_gate_forward','moe_topk_gate_forward'),('moe_topk_gate_backward','moe_topk_gate_backward')]:
    t=f'moe/test_{fname}.py'
    desc=('scores FP32 [num_tokens,num_experts]；输出索引 INT64 [num_tokens,num_topk]。' if fname=='topk_gate' else
          'logits FP32；forward 的行数为 num_tokens+num_padded_tokens，backward 为 num_seqs*(num_tokens+num_padded_tokens)；专家数及可选项见 case，上游测试生成其余输入。')
    extra=([{'num_tokens':n,'num_experts':e,'num_topk':k} for n,e,k in product([1,128,1024],[1,35,1025],[1,9,32]) if k<=e] if fname=='topk_gate' else [])
    candidates=from_test(t)
    if fname in ('moe_topk_gate_forward','moe_topk_gate_backward'):
        candidates=[dict(c,fix_routing=fix) for c in candidates for fix in (False,True)]
    add(name,source('moe',fname),t,candidates,desc,extras=extra,
        note='扩展组合满足公开接口的 topk 范围约束，具体设备可运行性待确认。' if extra else '')
t='moe/test_normalize_weight.py'
c=[{'num_tokens':n,'num_topk':k,'dtype':'fp32'} for n,k in product([1,127,128,512,4001,8001],[1,6,8,9,32])]
add('moe_normalize_weight',source('moe','normalize_weight'),t,[], 'topk_weights FP32 [num_tokens,num_topk]，连续。','已有 4 个 case',
    note='按公开 API 直接构造确定的输入 shape；不同于上游先随机路由后决定行数的 fixture，需独立做数值校验。',extras=c)

quant = [
 ('quant_cast','cast','generate_test_params','输入 FP32 [shape[0]]，输出 BF16；Ascend 上游测试的 stochastic_rounding=True。','库存无对应族'),
 ('quant_cast_back_per_token','cast_back','generate_test_params_per_token','量化输入逻辑形状 [num_tokens,hidden]，格式 fmt；输出 dtype=out_dtype；scale 布局及粒度见参数。','cast back 合计已有 4 个 case'),
 ('quant_cast_back_block','cast_back','generate_test_params','量化输入逻辑形状 [num_tokens,hidden]，格式 fmt；输出 dtype=out_dtype；scale 粒度为 (num_per_tokens,num_per_channels)。','cast back 合计已有 4 个 case'),
 ('quant_norm_forward','norm_forward','generate_test_params','输入 shape [num_tokens,hidden] 或 [batch_size,num_tokens,hidden]；输入 dtype=in_dtype 或 fmt，输出格式 fmt；row_padding 由参数规定。','RMSNorm 已有 13 个 case'),
 ('quant_norm_backward','norm_backward','generate_test_params','norm_input/out_grad dtype=fmt，shape [num_tokens,hidden]；权重和其梯度按参数启用。','库存无对应族'),
 ('quant_per_block_cast','per_block_cast','generate_test_params','输入 dtype=in_dtype，逻辑 shape [num_tokens,hidden]；输出格式 fmt，scale block=block_size。','库存无对应族'),
 ('quant_per_block_cast_lossless','per_block_cast_lossless','generate_test_params','输入逻辑 FP4 e2m1 [num_tokens,hidden]，用 packed INT8 保存；输出 e4m3，scale block 见 case。','库存无对应族'),
 ('quant_per_channel_cast','per_channel_cast','generate_test_params','输入逻辑 shape [num_tokens,hidden]、格式 in_dtype；输出 scale 的布局及粒度见 case。','库存无对应族'),
 ('quant_per_token_cast','per_token_cast','generate_test_params','输入逻辑 shape [num_tokens,hidden]、格式 in_dtype；输出格式 fmt，scale 与 block 属性见 case。','库存无对应族'),
 ('quant_per_token_cast_and_cast_back','per_token_cast_and_cast_back','generate_test_params','输入 dtype=in_dtype [num_tokens,hidden]，内部格式 fmt；输出与输入 dtype 相同。','库存无对应族'),
 ('quant_swiglu_forward','swiglu_forward','generate_test_params','x BF16 [实际扩展 token 数,2*hidden]；输出格式 fmt。实际 token 数由路由与对齐生成，运行前记录准确 shape。','SwiGLU 已有 19 个 case'),
 ('quant_swiglu_backward','swiglu_backward','generate_test_params','x 逻辑 shape [实际扩展 token 数,2*hidden]，梯度 [实际扩展 token 数,hidden]；输入格式与 fmt、可选权重由参数决定。','库存无对应族'),
]
for name,fname,fun,contract,history in quant:
    t=f'quant/test_{fname}.py'; candidates=from_test(t,fun)
    extras=[]
    if fname=='cast':
        candidates=[c for c in candidates if c['shape'][0] <= 2**27+128]
    note='上游参数组合候选；具体输入以对应测试构造器为准，合法性和数值正确性尚未在 hidev 逐例验证。'
    if fname=='per_token_cast': note += ' 上游 Ascend 测试明确跳过 stochastic rounding，本清单不含该路径。'
    if fname.startswith('swiglu'):
        # Upstream random routing has data-dependent shape. Use a fixed shape
        # and (when requested) a deterministic four-expert equal prefix sum.
        candidates=[]
        for n,h,fmt,with_weights,with_psum,clamp in product(
                [128,512,1024,4096,8192],[128,768,2048,3584],
                ['bf16','fp32','e4m3'],[False,True],[False,True],[None,0.5]):
            if with_psum and (n<1024 or n%1024): continue
            c=dict(num_tokens=n,hidden=h,fmt=fmt,with_weights=with_weights,
                   num_experts=4 if with_psum else 0,
                   alignment=256 if with_psum else 1,clamp_value=clamp,
                   routed_scaling_factor=2.5 if with_weights else None,
                   num_per_channels=32 if fmt=='e4m3' else None,
                   round_sf=(fmt=='e4m3'),use_tma_aligned_col_major_sf=False,
                   use_packed_ue8m0=False)
            if fname=='swiglu_backward': c['do_recompute']=with_weights
            extras.append(c)
        contract=('x BF16 [num_tokens,2*hidden]；输出格式 fmt；'
                  if fname=='swiglu_forward' else
                  'x 逻辑 shape [num_tokens,2*hidden]，梯度 [num_tokens,hidden]；fmt=e4m3 时 x 为 FP8，其余情况 x dtype=fmt；')
        contract+='可选 topk_weights FP32 [num_tokens]；num_experts=4 时 prefix INT32 为 [N/4,N/2,3N/4,N]，N=num_tokens。'
        note=('为固定真实输入 shape，按公开 API 构造明确的 token 数和等分 expert 前缀；全部标为扩展，尚未设备验证。'
              '该组不等同于上游随机路由数据；BF16/FP32/FP8 路径分别核对正确性。')
    add(name,source('quant',fname),t,candidates,contract,history,note,extras=extras)

# The public sf-only and precomputed-scale modes select distinct generated
# kernels, so record them separately instead of hiding them under generic cast.
for fname in ('per_token_cast','per_block_cast'):
    t=f'quant/test_{fname}.py'; pool=from_test(t)
    if fname=='per_token_cast':
        pool=[c for c in pool if c['in_dtype'] in ('fp32','bf16') and c['num_per_channels']!=c['hidden']]
    for mode in ('sf_only','precomputed_sf'):
        subset=pool
        if mode=='precomputed_sf':
            subset=[c for c in pool if not c['use_tma_aligned_col_major_sf'] and not c['use_packed_ue8m0']
                    and (fname!='per_token_cast' or c['round_sf'])]
        name=f'quant_{fname}_with_{mode}'
        contract=('x dtype=in_dtype [num_tokens,hidden]；fmt 和 scale 粒度见参数。'
                  + ('该入口只计算 scale。' if mode=='sf_only' else '该入口额外接收上游算出的 scale，且要求非 TMA、非 packed 布局。'))
        add(name,source('quant',fname),t,subset,contract,note='上游正确性测试包含该模式；必须单独圈定其设备 kernel，不能把同一测试中其它调用混入。')

t='quant/test_batched_transpose_weight_sf.py'
weights=[(128,128,None,False),(384,512,2,True),(768,1152,3,False),(640,1280,1,True),(2048,2560,2,False),(384,384,None,True),(6144,4096,None,False)]
extra=[{'block_size':32,'weight_configs':[(n,k,g,trans)]} for (n,k),g,trans in product([(128,128),(512,768),(2048,2560),(6144,4096),(384,1152)],[None,2],[False,True])]
add('quant_batched_transpose_weight_sf',source('quant','batched_transpose_weight_sf'),t,[{'block_size':32,'weight_configs':weights}],
    '输入为每个 (n,k,num_groups,transpose_sf1) 配置生成的 FP32 scale，shape 为 [n/32,k/32] 或 [num_groups,n/32,k/32]。',
    note='原上游 case 是 7 个权重一起运行；扩展 case 每次是新的单权重调用。block=128 在 Ascend 不支持。',extras=extra)
t='rand/test_randn.py'; shapes=[(1,), (127,129), (7,11,13), (16383,), (16384,), (16385,), (1024,1024), (4096,4096)]
add('randn',source('rand','randn'),t,[{'shape':s,'dtype':d} for s,d in product(shapes,['bf16','fp32'])],
    '输出 shape 和 dtype 见 case；seed=42。',note='扩展项补充小尺寸，分布检查与固定种子可重复性都需验证；上游另有超大 shape，不在本批。',extras=[{'shape':s,'dtype':d} for s,d in product([(64,),(128,),(1024,)],['bf16','fp32'])])
t='transform/test_rope.py'
c=rows(('nheads','dim','dtype','interleaved','conjugate','head_split'),([1,5,32,128],[64,128],['bf16','fp32'],[False,True],[False,True],[False,True]),seqlen=2001,seqlen_total=8192)
add('rotary_embedding',source('transform','rope'),t,c,'query/key 各 [seqlen,nheads,dim]、dtype=dtype；cos_sin FP32 [seqlen_total,dim]，positions INT32 [seqlen]。','已有 20 个 case（Q/K 分别采集）',note='本批还需记录 head_split 对实际 stride 的影响；此处列上游 3D 测试组合，旧库存部分为 4D。')


def check():
    names=[g['id'] for g in groups]
    assert len(names)==len(set(names))
    for g in groups:
        assert (TK/g['source']).is_file(), g['source']
        assert (TESTS/g['test']).is_file(), g['test']
        assert g['cases'] and len(g['cases']) <= 20
        assert len({canon(c) for c in g['cases']}) == len(g['cases'])
    asc={p.relative_to(TK).as_posix() for p in (TK/'tile_kernels').rglob('*_asc.py')}
    covered={g['source'] for g in groups}
    assert covered == asc, (sorted(asc-covered),sorted(covered-asc))


def possible_history(group, case, inventory):
    """Identify primary-shape overlaps only; never claim full equivalence."""
    name=group['id']; shape=None; dtype=None
    if name=='engram_fused_weight':
        family='engram_fused_weight'; shape=[case['hc'],case['hidden']]; dtype='bfloat16'
    elif name=='engram_hash':
        family='engram_hash'; shape=[case['num_tokens'],case['ngram']]; dtype='int32'
    elif name=='mhc_expand_fwd':
        family='mhc_expand_fwd'; shape=[case['n0']*case['n1'],case['hidden']]; dtype='bfloat16'
    elif name=='mhc_head_compute_mix_fwd':
        family='mhc_head'; shape=[case['n0']*case['n1'],case['mhc_mult']]; dtype='float32'
    elif name=='mhc_post_bwd':
        family='mhc_post_bwd'; shape=[case['n0'],case['n1'],case['mhc_mult'],case['hidden']]; dtype='bfloat16'
    elif name=='mhc_sinkhorn_fwd':
        family='sinkhorn'; shape=[case['n0']*case['n1'],case['mhc'],case['mhc']]; dtype='float32'
    elif name=='moe_normalize_weight':
        family='moe_normalize_weight'; shape=[case['num_tokens'],case['num_topk']]; dtype='float32'
    elif name=='quant_norm_forward':
        family='rmsnorm'; shape=([case['num_tokens'],case['hidden']] if case['batch_size'] is None else
                                [case['batch_size'],case['num_tokens'],case['hidden']])
        dtype={'bf16':'bfloat16','fp32':'float32'}.get(case['in_dtype'] or case['fmt'])
    elif name=='quant_swiglu_forward':
        family='swiglu'; shape=[case['num_tokens'],2*case['hidden']]; dtype='bfloat16'
    elif name in ('quant_cast_back_per_token','quant_cast_back_block') and case['fmt']=='e4m3':
        family='quant_cast_back'; shape=[case['num_tokens'],case['hidden']]; dtype='float8_e4m3fn'
    else:
        return []
    hits=[]
    for cid, old in inventory['cases'].items():
        if old['family']!=family: continue
        d=old['definition']
        if d.get('input_shapes',[None])[0]==shape and d.get('input_dtypes',[None])[0]==dtype:
            hits.append(cid)
    return sorted(hits)


def main():
    check()
    inv=json.loads((ROOT/'outputs/tilekernels-profile-inventory-reset-20261105/inventory.json').read_text(encoding='utf8'))
    for g in groups:
        g['possible_history_by_case']=[possible_history(g,c,inv) for c in g['cases']]
    counts=Counter(g['source'].split('/')[1] for g in groups)
    payload={'status':'candidate plans only; no device validation or profile',
             'source_commit':'c1cf914a82e6901c679445f872051ce44ac2cc63',
             'input_source':'pinned upstream tests and explicitly marked extensions; CPU-only extraction with 28 Cube/56 Vector core assumption',
             'entry_count':len(groups),'case_count':sum(len(g['cases']) for g in groups),
             'categories':dict(counts),'groups':groups}
    (OUT/'cases.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    lines=['# TileKernels Ascend profile 候选 case 清单', '',
           '> 状态：仅是从固定源码测试中整理的候选，没有在 hidev 逐例验证，也没有启动 profile。', '',
           f"固定提交 `c1cf914a82e6901c679445f872051ce44ac2cc63`；{len(groups)} 个入口/任务组，{sum(len(g['cases']) for g in groups)} 个候选任务。",
           '', '每行 `case` 参数均是一个候选。输入的 shape/dtype 由本节的“输入合同”结合该行参数展开；其余输入遵循对应上游测试。实际 kernel 名和编译结果仍需准备阶段确认。', '',
           '20 是目标上限，不用随机种子、无关维度或同一 tensor 内部元素凑数。标记“扩展”的是按对应公开接口和源码约束扩充的组合，不是已执行的上游测试。大 shape 可能需要较多内存，运行前应检查。', '',
           'mHC 的相关入口会把 n0、n1 合并后交给设备 kernel，因此按 n0×n1 去掉等价任务，避免把相同 kernel 输入计两次。', '',
           '历史研究曾把 topk_gate 作为整族留出候选，本表覆盖了该族；正式采集前须重新确定留出安排，不把采集后已用于规则开发的数据继续称作独立留出。', '',
           '生成测试参数时暂按 28 个 Cube 核、56 个 Vector 核建表；这里的 num_sms 指上游定义的 Cube 核数，不是 56 个 Vector 核。实际 profile 前须读取 hidev 设备属性确认。', '',
           '已有记录列说明该族在历史库存的数量。行内列出的“可能重合”仅表示主输入 shape/dtype 相同，不代表全部输入、参数、stride 和采集口径相同；未标记也不证明一定不同。正式排队前仍需完整去重。', '',
           '## 总览', '', '| 入口/任务组 | 候选数 | 候选池（含扩展） | 历史记录 |', '|---|---:|---:|---|']
    for g in groups:
        lines.append(f"| `{g['id']}` | {len(g['cases'])} | {g['candidate_pool']} | {g['historical_coverage']} |")
    for g in groups:
        lines += ['',f"## {g['id']}",'',f"- 实现：`{g['source']}`",f"- 上游测试：`tests/{g['test']}`",f"- 输入合同：{g['contract']}",f"- 已有情况：{g['historical_coverage']}"]
        if g['note']: lines.append(f"- 注意：{g['note']}")
        lines += ['', '| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |', '|---:|---|---|---|']
        for i,c in enumerate(g['cases'],1):
            origin='扩展' if canon(c) in g['extended_cases'] else '上游测试参数'
            hits=', '.join(g['possible_history_by_case'][i-1]) or '待核/未命中'
            lines.append(f"| {i:02d} | `{canon(c)}` | {origin} | {hits} |")
    lines += ['', '## 历史 case 完整索引', '',
              '以下是旧库存的 99 个登记 ID，对应 97 个不同任务定义。这里列出完整 shape/dtype/attrs，用于逐项对照；旧 Sinkhorn 等历史口径不能直接当成本次正式同口径结果。', '',
              '| 历史 ID | 族 | 完整任务定义 | 已登记采集口径 |', '|---|---|---|---|']
    for cid, item in sorted(inv['cases'].items()):
        regimes=sorted({p['regime'] for p in inv['profiles'] if p['case_id']==cid})
        lines.append(f"| `{cid}` | `{item['family']}` | `{canon(item['definition'])}` | {', '.join(regimes)} |")
    (OUT/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps({'entries':len(groups),'cases':payload['case_count'],'asc_files':len({g['source'] for g in groups}),'categories':counts},ensure_ascii=False))


if __name__=='__main__': main()
