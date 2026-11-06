# TileKernels Ascend profile 候选 case 清单

> 状态：仅是从固定源码测试中整理的候选，没有在 hidev 逐例验证，也没有启动 profile。

固定提交 `c1cf914a82e6901c679445f872051ce44ac2cc63`；50 个入口/任务组，1000 个候选任务。

每行 `case` 参数均是一个候选。输入的 shape/dtype 由本节的“输入合同”结合该行参数展开；其余输入遵循对应上游测试。实际 kernel 名和编译结果仍需准备阶段确认。

20 是目标上限，不用随机种子、无关维度或同一 tensor 内部元素凑数。标记“扩展”的是按对应公开接口和源码约束扩充的组合，不是已执行的上游测试。大 shape 可能需要较多内存，运行前应检查。

mHC 的相关入口会把 n0、n1 合并后交给设备 kernel，因此按 n0×n1 去掉等价任务，避免把相同 kernel 输入计两次。

历史研究曾把 topk_gate 作为整族留出候选，本表覆盖了该族；正式采集前须重新确定留出安排，不把采集后已用于规则开发的数据继续称作独立留出。

生成测试参数时暂按 28 个 Cube 核、56 个 Vector 核建表；这里的 num_sms 指上游定义的 Cube 核数，不是 56 个 Vector 核。实际 profile 前须读取 hidev 设备属性确认。

已有记录列说明该族在历史库存的数量。行内列出的“可能重合”仅表示主输入 shape/dtype 相同，不代表全部输入、参数、stride 和采集口径相同；未标记也不证明一定不同。正式排队前仍需完整去重。

## 总览

| 入口/任务组 | 候选数 | 候选池（含扩展） | 历史记录 |
|---|---:|---:|---|
| `engram_fused_weight` | 20 | 32 | 已有 5 个 case |
| `engram_gate_fwd` | 20 | 36 | 库存无对应族 |
| `engram_gate_bwd` | 20 | 28 | 库存无对应族 |
| `engram_grad_w_reduce` | 20 | 20 | 库存无对应族 |
| `engram_hash` | 20 | 24 | 已有 4 个 case |
| `engram_sinkhorn_momentum_update` | 20 | 32 | 库存无对应族 |
| `engram_sinkhorn_step` | 20 | 22 | 库存无对应族 |
| `engram_sinkhorn_step_reduce` | 20 | 25 | 库存无对应族 |
| `engram_sinkhorn_finalize` | 20 | 22 | 库存无对应族 |
| `mhc_expand_fwd` | 20 | 42 | 已有 1 个 case |
| `mhc_expand_bwd` | 20 | 42 | 库存无对应族 |
| `mhc_head_compute_mix_fwd` | 20 | 22 | forward 已有 2 个 case |
| `mhc_head_compute_mix_bwd` | 20 | 22 | 库存无对应族 |
| `mhc_post_fwd` | 20 | 24 | 库存无对应族 |
| `mhc_post_bwd` | 20 | 24 | backward 已有 7 个历史 case |
| `mhc_pre_apply_mix_fwd` | 20 | 35 | 库存无对应族 |
| `mhc_pre_apply_mix_bwd` | 20 | 35 | 库存无对应族 |
| `mhc_pre_split_mixes_fwd` | 20 | 20 | 库存无对应族 |
| `mhc_pre_split_mixes_bwd` | 20 | 20 | 库存无对应族 |
| `mhc_sinkhorn_fwd` | 20 | 20 | forward 已有 18 个不同 case（含旧口径） |
| `mhc_sinkhorn_bwd` | 20 | 20 | 库存无对应族 |
| `mhc_pre_big_fuse_fwd` | 20 | 30 | 库存无对应族 |
| `mhc_fn_normw_merge_fwd` | 20 | 22 | 库存无对应族 |
| `mhc_fn_normw_merge_bwd` | 20 | 22 | 库存无对应族 |
| `mhc_reduce_partials_and_rmsnorm_fwd` | 20 | 36 | 库存无对应族 |
| `mhc_reduce_partials_and_rmsnorm_bwd` | 20 | 36 | 库存无对应族 |
| `mhc_multilayer_recompute` | 20 | 20 | 库存无对应族 |
| `moe_topk_gate` | 20 | 35 | 库存无对应族 |
| `moe_topk_gate_forward` | 20 | 1280 | 库存无对应族 |
| `moe_topk_gate_backward` | 20 | 1280 | 库存无对应族 |
| `moe_normalize_weight` | 20 | 30 | 已有 4 个 case |
| `quant_cast` | 20 | 92 | 库存无对应族 |
| `quant_cast_back_per_token` | 20 | 216 | cast back 合计已有 4 个 case |
| `quant_cast_back_block` | 20 | 480 | cast back 合计已有 4 个 case |
| `quant_norm_forward` | 20 | 640 | RMSNorm 已有 13 个 case |
| `quant_norm_backward` | 20 | 180 | 库存无对应族 |
| `quant_per_block_cast` | 20 | 216 | 库存无对应族 |
| `quant_per_block_cast_lossless` | 20 | 64 | 库存无对应族 |
| `quant_per_channel_cast` | 20 | 144 | 库存无对应族 |
| `quant_per_token_cast` | 20 | 864 | 库存无对应族 |
| `quant_per_token_cast_and_cast_back` | 20 | 216 | 库存无对应族 |
| `quant_swiglu_forward` | 20 | 384 | SwiGLU 已有 19 个 case |
| `quant_swiglu_backward` | 20 | 384 | 库存无对应族 |
| `quant_per_token_cast_with_sf_only` | 20 | 432 | 库存无对应族 |
| `quant_per_token_cast_with_precomputed_sf` | 20 | 72 | 库存无对应族 |
| `quant_per_block_cast_with_sf_only` | 20 | 216 | 库存无对应族 |
| `quant_per_block_cast_with_precomputed_sf` | 20 | 144 | 库存无对应族 |
| `quant_batched_transpose_weight_sf` | 20 | 21 | 库存无对应族 |
| `randn` | 20 | 22 | 库存无对应族 |
| `rotary_embedding` | 20 | 128 | 已有 20 个 case（Q/K 分别采集） |

## engram_fused_weight

- 实现：`tile_kernels/engram/engram_fused_weight_asc.py`
- 上游测试：`tests/engram/test_engram_fused_weight.py`
- 输入合同：wh/we：BF16 [hc,hidden]；输出 FP32 [hc,hidden]。
- 已有情况：已有 5 个 case
- 注意：标注“扩展”的组合按源码限制补充，尚未经设备验证；并非上游完整测试原参数。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hc":4,"hidden":256}` | 扩展 | 待核/未命中 |
| 02 | `{"hc":4,"hidden":8192}` | 扩展 | 待核/未命中 |
| 03 | `{"hc":4,"hidden":1024}` | 扩展 | 待核/未命中 |
| 04 | `{"hc":4,"hidden":1280}` | 扩展 | 待核/未命中 |
| 05 | `{"hc":4,"hidden":1536}` | 扩展 | 待核/未命中 |
| 06 | `{"hc":4,"hidden":1792}` | 扩展 | 待核/未命中 |
| 07 | `{"hc":4,"hidden":2048}` | 上游测试参数 | fused-h2048 |
| 08 | `{"hc":4,"hidden":2304}` | 扩展 | 待核/未命中 |
| 09 | `{"hc":4,"hidden":2560}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"hc":4,"hidden":2816}` | 扩展 | 待核/未命中 |
| 11 | `{"hc":4,"hidden":3072}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"hc":4,"hidden":3328}` | 扩展 | 待核/未命中 |
| 13 | `{"hc":4,"hidden":3584}` | 扩展 | fused-h3584 |
| 14 | `{"hc":4,"hidden":3840}` | 扩展 | 待核/未命中 |
| 15 | `{"hc":4,"hidden":4096}` | 上游测试参数 | fused-h4096 |
| 16 | `{"hc":4,"hidden":4352}` | 扩展 | 待核/未命中 |
| 17 | `{"hc":4,"hidden":4608}` | 扩展 | 待核/未命中 |
| 18 | `{"hc":4,"hidden":4864}` | 扩展 | 待核/未命中 |
| 19 | `{"hc":4,"hidden":5120}` | 扩展 | 待核/未命中 |
| 20 | `{"hc":4,"hidden":512}` | 扩展 | 待核/未命中 |

## engram_gate_fwd

- 实现：`tile_kernels/engram/engram_gate_fwd_asc.py`
- 上游测试：`tests/engram/test_engram_gate_fwd.py`
- 输入合同：x：BF16 [num_tokens,hc,hidden]；kv：BF16 [num_tokens,hc+1,hidden]；融合权重 FP32 [hc,hidden]；可选 mask。
- 已有情况：库存无对应族
- 注意：标注“扩展”的组合按源码限制补充，尚未经设备验证；并非上游完整测试原参数。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hc":4,"hidden":128,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"hc":4,"hidden":768,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"hc":4,"hidden":128,"num_tokens":512,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"hc":4,"hidden":7168,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"hc":4,"hidden":2048,"num_tokens":8001,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"hc":4,"hidden":2560,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"hc":4,"hidden":3072,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"hc":4,"hidden":384,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"hc":4,"hidden":4096,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"hc":4,"hidden":6144,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"hc":4,"hidden":2048,"num_tokens":512,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"hc":4,"hidden":2560,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"hc":4,"hidden":3072,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"hc":4,"hidden":384,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"hc":4,"hidden":4096,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"hc":4,"hidden":6144,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"hc":4,"hidden":7168,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"hc":4,"hidden":768,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"hc":4,"hidden":128,"num_tokens":8001,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"hc":4,"hidden":128,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |

## engram_gate_bwd

- 实现：`tile_kernels/engram/engram_gate_bwd_asc.py`
- 上游测试：`tests/engram/test_engram_gate_bwd.py`
- 输入合同：与 forward 同输入，另有 BF16 梯度 [num_tokens,hc,hidden]；可选 mask。
- 已有情况：库存无对应族
- 注意：标注“扩展”的组合按源码限制补充，尚未经设备验证；并非上游完整测试原参数。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hc":4,"hidden":2048,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"hc":4,"hidden":768,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"hc":4,"hidden":768,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"hc":4,"hidden":7168,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"hc":4,"hidden":2560,"num_tokens":512,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"hc":4,"hidden":3072,"num_tokens":8001,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"hc":4,"hidden":4096,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"hc":4,"hidden":6144,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"hc":4,"hidden":2048,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"hc":4,"hidden":2560,"num_tokens":8001,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"hc":4,"hidden":3072,"num_tokens":512,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"hc":4,"hidden":4096,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"hc":4,"hidden":6144,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"hc":4,"hidden":7168,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"hc":4,"hidden":2048,"num_tokens":512,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"hc":4,"hidden":2048,"num_tokens":8001,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"hc":4,"hidden":2560,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"hc":4,"hidden":2560,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"hc":4,"hidden":3072,"num_tokens":512,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"hc":4,"hidden":3072,"num_tokens":8001,"with_mask":true}` | 上游测试参数 | 待核/未命中 |

## engram_grad_w_reduce

- 实现：`tile_kernels/engram/engram_grad_w_reduce_asc.py`
- 上游测试：`tests/engram/test_engram_grad_w_reduce.py`
- 输入合同：输入 FP32 [14,4,hidden] 和两份 BF16 [4,hidden] 权重；14 按目前 28 个 Cube 核的测试条件推导，采集前核对。
- 已有情况：库存无对应族
- 注意：标注“扩展”的组合按源码限制补充，尚未经设备验证；并非上游完整测试原参数。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hidden":1024}` | 扩展 | 待核/未命中 |
| 02 | `{"hidden":1280}` | 扩展 | 待核/未命中 |
| 03 | `{"hidden":128}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"hidden":1536}` | 扩展 | 待核/未命中 |
| 05 | `{"hidden":1792}` | 扩展 | 待核/未命中 |
| 06 | `{"hidden":192}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"hidden":2048}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"hidden":2560}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"hidden":256}` | 扩展 | 待核/未命中 |
| 10 | `{"hidden":3072}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"hidden":320}` | 扩展 | 待核/未命中 |
| 12 | `{"hidden":3584}` | 扩展 | 待核/未命中 |
| 13 | `{"hidden":384}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"hidden":4096}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"hidden":5120}` | 扩展 | 待核/未命中 |
| 16 | `{"hidden":512}` | 扩展 | 待核/未命中 |
| 17 | `{"hidden":6144}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"hidden":64}` | 扩展 | 待核/未命中 |
| 19 | `{"hidden":7168}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"hidden":768}` | 上游测试参数 | 待核/未命中 |

## engram_hash

- 实现：`tile_kernels/engram/engram_hash_asc.py`
- 上游测试：`tests/engram/test_engram_hash.py`
- 输入合同：token IDs INT32 [num_tokens,ngram]；multiplier INT64 [layers,ngram]；其他表按上游测试生成。
- 已有情况：已有 4 个 case
- 注意：标注“扩展”的组合按源码限制补充，尚未经设备验证；并非上游完整测试原参数。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"layers":2,"ngram":3,"num_tokens":1,"tables":8,"with_mask":false}` | 扩展 | hash-n1-g3 |
| 02 | `{"layers":2,"ngram":4,"num_tokens":8192,"tables":8,"with_mask":true}` | 扩展 | 待核/未命中 |
| 03 | `{"layers":2,"ngram":3,"num_tokens":1024,"tables":8,"with_mask":true}` | 扩展 | 待核/未命中 |
| 04 | `{"layers":2,"ngram":4,"num_tokens":128,"tables":8,"with_mask":false}` | 扩展 | 待核/未命中 |
| 05 | `{"layers":2,"ngram":3,"num_tokens":512,"tables":8,"with_mask":false}` | 上游测试参数 | hash-n512-g3 |
| 06 | `{"layers":2,"ngram":3,"num_tokens":8001,"tables":8,"with_mask":false}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"layers":2,"ngram":3,"num_tokens":128,"tables":8,"with_mask":true}` | 扩展 | 待核/未命中 |
| 08 | `{"layers":2,"ngram":3,"num_tokens":8192,"tables":8,"with_mask":false}` | 扩展 | 待核/未命中 |
| 09 | `{"layers":2,"ngram":4,"num_tokens":1,"tables":8,"with_mask":true}` | 扩展 | 待核/未命中 |
| 10 | `{"layers":2,"ngram":4,"num_tokens":1024,"tables":8,"with_mask":false}` | 扩展 | 待核/未命中 |
| 11 | `{"layers":2,"ngram":4,"num_tokens":512,"tables":8,"with_mask":true}` | 上游测试参数 | hash-n512-g4-mask |
| 12 | `{"layers":2,"ngram":4,"num_tokens":8001,"tables":8,"with_mask":true}` | 上游测试参数 | hash-n8001-g4 |
| 13 | `{"layers":2,"ngram":3,"num_tokens":1,"tables":8,"with_mask":true}` | 扩展 | hash-n1-g3 |
| 14 | `{"layers":2,"ngram":3,"num_tokens":1024,"tables":8,"with_mask":false}` | 扩展 | 待核/未命中 |
| 15 | `{"layers":2,"ngram":3,"num_tokens":128,"tables":8,"with_mask":false}` | 扩展 | 待核/未命中 |
| 16 | `{"layers":2,"ngram":3,"num_tokens":512,"tables":8,"with_mask":true}` | 上游测试参数 | hash-n512-g3 |
| 17 | `{"layers":2,"ngram":3,"num_tokens":8001,"tables":8,"with_mask":true}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"layers":2,"ngram":3,"num_tokens":8192,"tables":8,"with_mask":true}` | 扩展 | 待核/未命中 |
| 19 | `{"layers":2,"ngram":4,"num_tokens":1,"tables":8,"with_mask":false}` | 扩展 | 待核/未命中 |
| 20 | `{"layers":2,"ngram":4,"num_tokens":1024,"tables":8,"with_mask":true}` | 扩展 | 待核/未命中 |

## engram_sinkhorn_momentum_update

- 实现：`tile_kernels/engram/engram_sinkhorn_asc.py`
- 上游测试：`tests/engram/test_engram_sinkhorn.py`
- 输入合同：grad 和 momentum 各为 [numel]，dtype 分别由 grad_dtype、momentum_dtype 指定；beta1 和 nesterov 如 case。
- 已有情况：库存无对应族
- 注意：扩展项沿用上游支持的 FP32 输入，设备合法性和输出精度待验证；大矩阵先检查显存。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"bf16","nesterov":false,"numel":256256}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"beta1":0.95,"grad_dtype":"fp32","momentum_dtype":"fp32","nesterov":true,"numel":512000512}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"bf16","nesterov":true,"numel":2560256}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"fp32","nesterov":false,"numel":51200512}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"beta1":0.95,"grad_dtype":"fp32","momentum_dtype":"bf16","nesterov":false,"numel":2560256}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"bf16","nesterov":false,"numel":512000512}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"beta1":0.95,"grad_dtype":"fp32","momentum_dtype":"bf16","nesterov":true,"numel":51200512}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"beta1":0.95,"grad_dtype":"fp32","momentum_dtype":"fp32","nesterov":true,"numel":256256}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"fp32","nesterov":false,"numel":2560256}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"bf16","nesterov":false,"numel":2560256}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"bf16","nesterov":false,"numel":51200512}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"bf16","nesterov":true,"numel":256256}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"bf16","nesterov":true,"numel":512000512}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"bf16","nesterov":true,"numel":51200512}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"fp32","nesterov":false,"numel":256256}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"fp32","nesterov":false,"numel":512000512}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"fp32","nesterov":true,"numel":2560256}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"fp32","nesterov":true,"numel":256256}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"fp32","nesterov":true,"numel":512000512}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"beta1":0.95,"grad_dtype":"bf16","momentum_dtype":"fp32","nesterov":true,"numel":51200512}` | 上游测试参数 | 待核/未命中 |

## engram_sinkhorn_step

- 实现：`tile_kernels/engram/engram_sinkhorn_asc.py`
- 上游测试：`tests/engram/test_engram_sinkhorn.py`
- 输入合同：matrix FP32 [num_rows,head_dim]，row_scale FP32 [num_rows]，col_scale FP32 [head_dim]。
- 已有情况：库存无对应族
- 注意：扩展项沿用上游支持的 FP32 输入，设备合法性和输出精度待验证；大矩阵先检查显存。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"eps":1e-20,"head_dim":256,"num_rows":1}` | 扩展 | 待核/未命中 |
| 02 | `{"eps":1e-20,"head_dim":5120,"num_rows":100001}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"eps":1e-20,"head_dim":256,"num_rows":10001}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"eps":1e-20,"head_dim":256,"num_rows":1001}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"eps":1e-20,"head_dim":256,"num_rows":1024}` | 扩展 | 待核/未命中 |
| 06 | `{"eps":1e-20,"head_dim":256,"num_rows":128}` | 扩展 | 待核/未命中 |
| 07 | `{"eps":1e-20,"head_dim":256,"num_rows":16384}` | 扩展 | 待核/未命中 |
| 08 | `{"eps":1e-20,"head_dim":256,"num_rows":32768}` | 扩展 | 待核/未命中 |
| 09 | `{"eps":1e-20,"head_dim":256,"num_rows":4096}` | 扩展 | 待核/未命中 |
| 10 | `{"eps":1e-20,"head_dim":256,"num_rows":512}` | 扩展 | 待核/未命中 |
| 11 | `{"eps":1e-20,"head_dim":256,"num_rows":8192}` | 扩展 | 待核/未命中 |
| 12 | `{"eps":1e-20,"head_dim":256,"num_rows":100001}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"eps":1e-20,"head_dim":5120,"num_rows":10001}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"eps":1e-20,"head_dim":5120,"num_rows":1001}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"eps":1e-20,"head_dim":5120,"num_rows":1024}` | 扩展 | 待核/未命中 |
| 16 | `{"eps":1e-20,"head_dim":5120,"num_rows":128}` | 扩展 | 待核/未命中 |
| 17 | `{"eps":1e-20,"head_dim":5120,"num_rows":16384}` | 扩展 | 待核/未命中 |
| 18 | `{"eps":1e-20,"head_dim":5120,"num_rows":1}` | 扩展 | 待核/未命中 |
| 19 | `{"eps":1e-20,"head_dim":5120,"num_rows":32768}` | 扩展 | 待核/未命中 |
| 20 | `{"eps":1e-20,"head_dim":5120,"num_rows":4096}` | 扩展 | 待核/未命中 |

## engram_sinkhorn_step_reduce

- 实现：`tile_kernels/engram/engram_sinkhorn_asc.py`
- 上游测试：`tests/engram/test_engram_sinkhorn.py`
- 输入合同：partial FP32 [num_partials,head_dim]，输出 FP32 [head_dim]。
- 已有情况：库存无对应族
- 注意：扩展项沿用上游支持的 FP32 输入，设备合法性和输出精度待验证；大矩阵先检查显存。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"head_dim":1024,"num_partials":1}` | 扩展 | 待核/未命中 |
| 02 | `{"head_dim":5120,"num_partials":112}` | 扩展 | 待核/未命中 |
| 03 | `{"head_dim":2048,"num_partials":18}` | 扩展 | 待核/未命中 |
| 04 | `{"head_dim":256,"num_partials":28}` | 扩展 | 待核/未命中 |
| 05 | `{"head_dim":512,"num_partials":56}` | 扩展 | 待核/未命中 |
| 06 | `{"head_dim":1024,"num_partials":112}` | 扩展 | 待核/未命中 |
| 07 | `{"head_dim":1024,"num_partials":18}` | 扩展 | 待核/未命中 |
| 08 | `{"head_dim":1024,"num_partials":28}` | 扩展 | 待核/未命中 |
| 09 | `{"head_dim":1024,"num_partials":56}` | 扩展 | 待核/未命中 |
| 10 | `{"head_dim":2048,"num_partials":112}` | 扩展 | 待核/未命中 |
| 11 | `{"head_dim":2048,"num_partials":1}` | 扩展 | 待核/未命中 |
| 12 | `{"head_dim":2048,"num_partials":28}` | 扩展 | 待核/未命中 |
| 13 | `{"head_dim":2048,"num_partials":56}` | 扩展 | 待核/未命中 |
| 14 | `{"head_dim":256,"num_partials":112}` | 扩展 | 待核/未命中 |
| 15 | `{"head_dim":256,"num_partials":18}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"head_dim":256,"num_partials":1}` | 扩展 | 待核/未命中 |
| 17 | `{"head_dim":256,"num_partials":56}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"head_dim":512,"num_partials":112}` | 扩展 | 待核/未命中 |
| 19 | `{"head_dim":512,"num_partials":18}` | 扩展 | 待核/未命中 |
| 20 | `{"head_dim":512,"num_partials":1}` | 扩展 | 待核/未命中 |

## engram_sinkhorn_finalize

- 实现：`tile_kernels/engram/engram_sinkhorn_asc.py`
- 上游测试：`tests/engram/test_engram_sinkhorn.py`
- 输入合同：matrix FP32 [num_rows,head_dim]，row_scale FP32 [num_rows]，col_scale FP32 [head_dim]；alpha=sqrt(head_dim)。
- 已有情况：库存无对应族
- 注意：扩展项沿用上游支持的 FP32 输入，设备合法性和输出精度待验证；大矩阵先检查显存。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"eps":1e-20,"head_dim":256,"num_rows":1}` | 扩展 | 待核/未命中 |
| 02 | `{"eps":1e-20,"head_dim":5120,"num_rows":100001}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"eps":1e-20,"head_dim":256,"num_rows":10001}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"eps":1e-20,"head_dim":256,"num_rows":1001}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"eps":1e-20,"head_dim":256,"num_rows":1024}` | 扩展 | 待核/未命中 |
| 06 | `{"eps":1e-20,"head_dim":256,"num_rows":128}` | 扩展 | 待核/未命中 |
| 07 | `{"eps":1e-20,"head_dim":256,"num_rows":16384}` | 扩展 | 待核/未命中 |
| 08 | `{"eps":1e-20,"head_dim":256,"num_rows":32768}` | 扩展 | 待核/未命中 |
| 09 | `{"eps":1e-20,"head_dim":256,"num_rows":4096}` | 扩展 | 待核/未命中 |
| 10 | `{"eps":1e-20,"head_dim":256,"num_rows":512}` | 扩展 | 待核/未命中 |
| 11 | `{"eps":1e-20,"head_dim":256,"num_rows":8192}` | 扩展 | 待核/未命中 |
| 12 | `{"eps":1e-20,"head_dim":256,"num_rows":100001}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"eps":1e-20,"head_dim":5120,"num_rows":10001}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"eps":1e-20,"head_dim":5120,"num_rows":1001}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"eps":1e-20,"head_dim":5120,"num_rows":1024}` | 扩展 | 待核/未命中 |
| 16 | `{"eps":1e-20,"head_dim":5120,"num_rows":128}` | 扩展 | 待核/未命中 |
| 17 | `{"eps":1e-20,"head_dim":5120,"num_rows":16384}` | 扩展 | 待核/未命中 |
| 18 | `{"eps":1e-20,"head_dim":5120,"num_rows":1}` | 扩展 | 待核/未命中 |
| 19 | `{"eps":1e-20,"head_dim":5120,"num_rows":32768}` | 扩展 | 待核/未命中 |
| 20 | `{"eps":1e-20,"head_dim":5120,"num_rows":4096}` | 扩展 | 待核/未命中 |

## mhc_expand_fwd

- 实现：`tile_kernels/mhc/expand_asc.py`
- 上游测试：`tests/mhc/test_expand.py`
- 输入合同：x BF16 [n0,n1,hidden]；输出 BF16 [n0,n1,4,hidden]。
- 已有情况：已有 1 个 case

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 02 | `{"hidden":7168,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 03 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"hidden":7168,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"hidden":7168,"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"hidden":1920,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 08 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"hidden":4224,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"hidden":5120,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"hidden":1920,"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"hidden":2560,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"hidden":4224,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"hidden":5120,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 16 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 17 | `{"hidden":1280,"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"hidden":1920,"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 19 | `{"hidden":1920,"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"hidden":1920,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |

## mhc_expand_bwd

- 实现：`tile_kernels/mhc/expand_asc.py`
- 上游测试：`tests/mhc/test_expand.py`
- 输入合同：输出梯度 BF16 [n0,n1,4,hidden]；返回 BF16 [n0,n1,hidden]。
- 已有情况：库存无对应族

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 02 | `{"hidden":7168,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 03 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"hidden":7168,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"hidden":7168,"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"hidden":1920,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 08 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"hidden":4224,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"hidden":5120,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"hidden":1920,"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"hidden":2560,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"hidden":4224,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"hidden":5120,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 16 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 17 | `{"hidden":1280,"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"hidden":1920,"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 19 | `{"hidden":1920,"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"hidden":1920,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |

## mhc_head_compute_mix_fwd

- 实现：`tile_kernels/mhc/head_compute_mix_asc.py`
- 上游测试：`tests/mhc/test_head_compute_mix.py`
- 输入合同：input_mix FP32 [n0,n1,4]；scale FP32 [1]，base FP32 [4]；反向另需同形状梯度。
- 已有情况：forward 已有 2 个 case
- 注意：补充不同序列长度覆盖小规模和尾部；扩展项尚需设备验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":1}` | 扩展 | 待核/未命中 |
| 02 | `{"eps":0.01,"mhc_mult":4,"n0":2,"n1":24576}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":1001}` | 上游测试参数 | head-fp32-1001 |
| 04 | `{"eps":0.01,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | head-fp32-1024 |
| 06 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":127}` | 扩展 | 待核/未命中 |
| 07 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 08 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":16384}` | 扩展 | 待核/未命中 |
| 09 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":16385}` | 扩展 | 待核/未命中 |
| 10 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":17}` | 扩展 | 待核/未命中 |
| 11 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":2049}` | 扩展 | 待核/未命中 |
| 12 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":257}` | 扩展 | 待核/未命中 |
| 13 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":4097}` | 扩展 | 待核/未命中 |
| 14 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":511}` | 扩展 | 待核/未命中 |
| 15 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 16 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":513}` | 扩展 | 待核/未命中 |
| 17 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":64}` | 扩展 | 待核/未命中 |
| 18 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 19 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":24576}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |

## mhc_head_compute_mix_bwd

- 实现：`tile_kernels/mhc/head_compute_mix_asc.py`
- 上游测试：`tests/mhc/test_head_compute_mix.py`
- 输入合同：input_mix FP32 [n0,n1,4]；scale FP32 [1]，base FP32 [4]；反向另需同形状梯度。
- 已有情况：库存无对应族
- 注意：补充不同序列长度覆盖小规模和尾部；扩展项尚需设备验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":1}` | 扩展 | 待核/未命中 |
| 02 | `{"eps":0.01,"mhc_mult":4,"n0":2,"n1":24576}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":1001}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"eps":0.01,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":127}` | 扩展 | 待核/未命中 |
| 07 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 08 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":16384}` | 扩展 | 待核/未命中 |
| 09 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":16385}` | 扩展 | 待核/未命中 |
| 10 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":17}` | 扩展 | 待核/未命中 |
| 11 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":2049}` | 扩展 | 待核/未命中 |
| 12 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":257}` | 扩展 | 待核/未命中 |
| 13 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":4097}` | 扩展 | 待核/未命中 |
| 14 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":511}` | 扩展 | 待核/未命中 |
| 15 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 16 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":513}` | 扩展 | 待核/未命中 |
| 17 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":64}` | 扩展 | 待核/未命中 |
| 18 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 19 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":24576}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"eps":0.01,"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |

## mhc_post_fwd

- 实现：`tile_kernels/mhc/post_asc.py`
- 上游测试：`tests/mhc/test_post.py`
- 输入合同：x BF16 [n0,n1,hidden]；residual BF16 [n0,n1,4,hidden]；post_mix FP32 [n0,n1,4,1]；comb_mix FP32 [n0,n1,4,4]；反向另有 BF16 输出梯度。
- 已有情况：库存无对应族
- 注意：扩展 token 规模；旧 backward 的其它 shape 另见原库存，扩展项待验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 02 | `{"hidden":7168,"mhc_mult":4,"n0":2,"n1":8192}` | 扩展 | 待核/未命中 |
| 03 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":1024}` | 扩展 | 待核/未命中 |
| 04 | `{"hidden":7168,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":2048}` | 扩展 | 待核/未命中 |
| 06 | `{"hidden":7168,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 07 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"hidden":5120,"mhc_mult":4,"n0":1,"n1":1024}` | 扩展 | 待核/未命中 |
| 09 | `{"hidden":1280,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"hidden":2560,"mhc_mult":4,"n0":2,"n1":8192}` | 扩展 | 待核/未命中 |
| 11 | `{"hidden":5120,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"hidden":1280,"mhc_mult":4,"n0":2,"n1":8192}` | 扩展 | 待核/未命中 |
| 13 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":1024}` | 扩展 | 待核/未命中 |
| 14 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":2048}` | 扩展 | 待核/未命中 |
| 15 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 16 | `{"hidden":5120,"mhc_mult":4,"n0":1,"n1":2048}` | 扩展 | 待核/未命中 |
| 17 | `{"hidden":5120,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 18 | `{"hidden":5120,"mhc_mult":4,"n0":2,"n1":8192}` | 扩展 | 待核/未命中 |
| 19 | `{"hidden":7168,"mhc_mult":4,"n0":1,"n1":1024}` | 扩展 | 待核/未命中 |
| 20 | `{"hidden":7168,"mhc_mult":4,"n0":1,"n1":2048}` | 扩展 | 待核/未命中 |

## mhc_post_bwd

- 实现：`tile_kernels/mhc/post_asc.py`
- 上游测试：`tests/mhc/test_post.py`
- 输入合同：x BF16 [n0,n1,hidden]；residual BF16 [n0,n1,4,hidden]；post_mix FP32 [n0,n1,4,1]；comb_mix FP32 [n0,n1,4,4]；反向另有 BF16 输出梯度。
- 已有情况：backward 已有 7 个历史 case
- 注意：扩展 token 规模；旧 backward 的其它 shape 另见原库存，扩展项待验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 02 | `{"hidden":7168,"mhc_mult":4,"n0":2,"n1":8192}` | 扩展 | 待核/未命中 |
| 03 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":1024}` | 扩展 | 待核/未命中 |
| 04 | `{"hidden":7168,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":2048}` | 扩展 | 待核/未命中 |
| 06 | `{"hidden":7168,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 07 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"hidden":5120,"mhc_mult":4,"n0":1,"n1":1024}` | 扩展 | mhc_post_bwd-cann-2 |
| 09 | `{"hidden":1280,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"hidden":2560,"mhc_mult":4,"n0":2,"n1":8192}` | 扩展 | 待核/未命中 |
| 11 | `{"hidden":5120,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"hidden":1280,"mhc_mult":4,"n0":2,"n1":8192}` | 扩展 | 待核/未命中 |
| 13 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":1024}` | 扩展 | 待核/未命中 |
| 14 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":2048}` | 扩展 | mhc_post_bwd-cann-4 |
| 15 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 16 | `{"hidden":5120,"mhc_mult":4,"n0":1,"n1":2048}` | 扩展 | 待核/未命中 |
| 17 | `{"hidden":5120,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 18 | `{"hidden":5120,"mhc_mult":4,"n0":2,"n1":8192}` | 扩展 | 待核/未命中 |
| 19 | `{"hidden":7168,"mhc_mult":4,"n0":1,"n1":1024}` | 扩展 | 待核/未命中 |
| 20 | `{"hidden":7168,"mhc_mult":4,"n0":1,"n1":2048}` | 扩展 | 待核/未命中 |

## mhc_pre_apply_mix_fwd

- 实现：`tile_kernels/mhc/pre_apply_mix_asc.py`
- 上游测试：`tests/mhc/test_pre_apply_mix.py`
- 输入合同：x BF16 [n0,n1,4,hidden]；mix FP32 [n0,n1,4,1]；反向另有 BF16 [n0,n1,hidden] 梯度。
- 已有情况：库存无对应族

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 02 | `{"hidden":7168,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 03 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"hidden":7168,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"hidden":7168,"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 08 | `{"hidden":4096,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"hidden":5120,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"hidden":2560,"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"hidden":4096,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"hidden":5120,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 14 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 15 | `{"hidden":1280,"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 17 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 19 | `{"hidden":4096,"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 20 | `{"hidden":4096,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |

## mhc_pre_apply_mix_bwd

- 实现：`tile_kernels/mhc/pre_apply_mix_asc.py`
- 上游测试：`tests/mhc/test_pre_apply_mix.py`
- 输入合同：x BF16 [n0,n1,4,hidden]；mix FP32 [n0,n1,4,1]；反向另有 BF16 [n0,n1,hidden] 梯度。
- 已有情况：库存无对应族

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 02 | `{"hidden":7168,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 03 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"hidden":7168,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"hidden":7168,"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 08 | `{"hidden":4096,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"hidden":5120,"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"hidden":2560,"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"hidden":4096,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"hidden":5120,"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 14 | `{"hidden":1280,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 15 | `{"hidden":1280,"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 17 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"hidden":2560,"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 19 | `{"hidden":4096,"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 20 | `{"hidden":4096,"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |

## mhc_pre_split_mixes_fwd

- 实现：`tile_kernels/mhc/pre_split_mixes_asc.py`
- 上游测试：`tests/mhc/test_pre_split_mixes.py`
- 输入合同：input_mixes FP32 [n0,n1,24]；scale FP32 [3]，base FP32 [24]；反向另有 pre/post/comb 梯度。
- 已有情况：库存无对应族
- 注意：公开入口按实现选择具体 kernel；扩展项需核对所走分支和运行合法性。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"mhc_mult":4,"n0":1,"n1":1001}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"mhc_mult":4,"n0":1,"n1":127}` | 扩展 | 待核/未命中 |
| 04 | `{"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 05 | `{"mhc_mult":4,"n0":1,"n1":16384}` | 扩展 | 待核/未命中 |
| 06 | `{"mhc_mult":4,"n0":1,"n1":16385}` | 扩展 | 待核/未命中 |
| 07 | `{"mhc_mult":4,"n0":1,"n1":17}` | 扩展 | 待核/未命中 |
| 08 | `{"mhc_mult":4,"n0":1,"n1":1}` | 扩展 | 待核/未命中 |
| 09 | `{"mhc_mult":4,"n0":1,"n1":2049}` | 扩展 | 待核/未命中 |
| 10 | `{"mhc_mult":4,"n0":1,"n1":257}` | 扩展 | 待核/未命中 |
| 11 | `{"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"mhc_mult":4,"n0":1,"n1":4097}` | 扩展 | 待核/未命中 |
| 13 | `{"mhc_mult":4,"n0":1,"n1":511}` | 扩展 | 待核/未命中 |
| 14 | `{"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 15 | `{"mhc_mult":4,"n0":1,"n1":513}` | 扩展 | 待核/未命中 |
| 16 | `{"mhc_mult":4,"n0":1,"n1":64}` | 扩展 | 待核/未命中 |
| 17 | `{"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 18 | `{"mhc_mult":4,"n0":2,"n1":1001}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |

## mhc_pre_split_mixes_bwd

- 实现：`tile_kernels/mhc/pre_split_mixes_asc.py`
- 上游测试：`tests/mhc/test_pre_split_mixes.py`
- 输入合同：input_mixes FP32 [n0,n1,24]；scale FP32 [3]，base FP32 [24]；反向另有 pre/post/comb 梯度。
- 已有情况：库存无对应族
- 注意：公开入口按实现选择具体 kernel；扩展项需核对所走分支和运行合法性。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"mhc_mult":4,"n0":1,"n1":1001}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"mhc_mult":4,"n0":1,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"mhc_mult":4,"n0":1,"n1":127}` | 扩展 | 待核/未命中 |
| 04 | `{"mhc_mult":4,"n0":1,"n1":128}` | 扩展 | 待核/未命中 |
| 05 | `{"mhc_mult":4,"n0":1,"n1":16384}` | 扩展 | 待核/未命中 |
| 06 | `{"mhc_mult":4,"n0":1,"n1":16385}` | 扩展 | 待核/未命中 |
| 07 | `{"mhc_mult":4,"n0":1,"n1":17}` | 扩展 | 待核/未命中 |
| 08 | `{"mhc_mult":4,"n0":1,"n1":1}` | 扩展 | 待核/未命中 |
| 09 | `{"mhc_mult":4,"n0":1,"n1":2049}` | 扩展 | 待核/未命中 |
| 10 | `{"mhc_mult":4,"n0":1,"n1":257}` | 扩展 | 待核/未命中 |
| 11 | `{"mhc_mult":4,"n0":1,"n1":4096}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"mhc_mult":4,"n0":1,"n1":4097}` | 扩展 | 待核/未命中 |
| 13 | `{"mhc_mult":4,"n0":1,"n1":511}` | 扩展 | 待核/未命中 |
| 14 | `{"mhc_mult":4,"n0":1,"n1":512}` | 扩展 | 待核/未命中 |
| 15 | `{"mhc_mult":4,"n0":1,"n1":513}` | 扩展 | 待核/未命中 |
| 16 | `{"mhc_mult":4,"n0":1,"n1":64}` | 扩展 | 待核/未命中 |
| 17 | `{"mhc_mult":4,"n0":1,"n1":8001}` | 扩展 | 待核/未命中 |
| 18 | `{"mhc_mult":4,"n0":2,"n1":1001}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"mhc_mult":4,"n0":2,"n1":1024}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"mhc_mult":4,"n0":2,"n1":4096}` | 上游测试参数 | 待核/未命中 |

## mhc_sinkhorn_fwd

- 实现：`tile_kernels/mhc/sinkhorn_asc.py`
- 上游测试：`tests/mhc/test_sinkhorn.py`
- 输入合同：matrix FP32 [n0,n1,4,4]；反向另需同形状 FP32 梯度。
- 已有情况：forward 已有 18 个不同 case（含旧口径）
- 注意：扩展序列长度，具体是否与旧 case 等价需核对 repeat 和计时口径。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":1,"repeat":10}` | 上游测试参数 | sinkhorn-cann-1, sinkhorn-supp-01 |
| 02 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":1001,"repeat":10}` | 扩展 | 待核/未命中 |
| 03 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":1024,"repeat":10}` | 上游测试参数 | sinkhorn-cann-13, sinkhorn-cann-14, sinkhorn-cann-15, sinkhorn-cann-16, sinkhorn-cann-17, sinkhorn-cann-19, sinkhorn-cann-20, sinkhorn-cann-4, sinkhorn-supp-06 |
| 04 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":127,"repeat":10}` | 扩展 | 待核/未命中 |
| 05 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":128,"repeat":10}` | 扩展 | sinkhorn-supp-04 |
| 06 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":16385,"repeat":10}` | 扩展 | 待核/未命中 |
| 07 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":17,"repeat":10}` | 扩展 | 待核/未命中 |
| 08 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":2049,"repeat":10}` | 扩展 | 待核/未命中 |
| 09 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":257,"repeat":10}` | 扩展 | 待核/未命中 |
| 10 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":32769,"repeat":10}` | 扩展 | 待核/未命中 |
| 11 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":4096,"repeat":10}` | 上游测试参数 | sinkhorn-cann-5, sinkhorn-supp-07 |
| 12 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":4097,"repeat":10}` | 扩展 | 待核/未命中 |
| 13 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":511,"repeat":10}` | 扩展 | sinkhorn-supp-05 |
| 14 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":512,"repeat":10}` | 扩展 | sinkhorn-cann-3 |
| 15 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":513,"repeat":10}` | 扩展 | 待核/未命中 |
| 16 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":64,"repeat":10}` | 扩展 | sinkhorn-cann-2 |
| 17 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":8001,"repeat":10}` | 扩展 | 待核/未命中 |
| 18 | `{"eps":1e-06,"mhc":4,"n0":2,"n1":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"eps":1e-06,"mhc":4,"n0":2,"n1":1024,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"eps":1e-06,"mhc":4,"n0":2,"n1":4096,"repeat":10}` | 上游测试参数 | 待核/未命中 |

## mhc_sinkhorn_bwd

- 实现：`tile_kernels/mhc/sinkhorn_asc.py`
- 上游测试：`tests/mhc/test_sinkhorn.py`
- 输入合同：matrix FP32 [n0,n1,4,4]；反向另需同形状 FP32 梯度。
- 已有情况：库存无对应族
- 注意：扩展序列长度，具体是否与旧 case 等价需核对 repeat 和计时口径。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":1001,"repeat":10}` | 扩展 | 待核/未命中 |
| 03 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":1024,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":127,"repeat":10}` | 扩展 | 待核/未命中 |
| 05 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":128,"repeat":10}` | 扩展 | 待核/未命中 |
| 06 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":16385,"repeat":10}` | 扩展 | 待核/未命中 |
| 07 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":17,"repeat":10}` | 扩展 | 待核/未命中 |
| 08 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":2049,"repeat":10}` | 扩展 | 待核/未命中 |
| 09 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":257,"repeat":10}` | 扩展 | 待核/未命中 |
| 10 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":32769,"repeat":10}` | 扩展 | 待核/未命中 |
| 11 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":4096,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":4097,"repeat":10}` | 扩展 | 待核/未命中 |
| 13 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":511,"repeat":10}` | 扩展 | 待核/未命中 |
| 14 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":512,"repeat":10}` | 扩展 | 待核/未命中 |
| 15 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":513,"repeat":10}` | 扩展 | 待核/未命中 |
| 16 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":64,"repeat":10}` | 扩展 | 待核/未命中 |
| 17 | `{"eps":1e-06,"mhc":4,"n0":1,"n1":8001,"repeat":10}` | 扩展 | 待核/未命中 |
| 18 | `{"eps":1e-06,"mhc":4,"n0":2,"n1":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"eps":1e-06,"mhc":4,"n0":2,"n1":1024,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"eps":1e-06,"mhc":4,"n0":2,"n1":4096,"repeat":10}` | 上游测试参数 | 待核/未命中 |

## mhc_pre_big_fuse_fwd

- 实现：`tile_kernels/mhc/pre_big_fuse_asc.py`
- 上游测试：`tests/mhc/test_pre_big_fuse.py`
- 输入合同：目标输入：GEMM 中间量 FP32 [1,n1,24]、平方和 FP32 [1,n1]、scale FP32 [3]、base FP32 [24]、residual BF16 [n1,4,hidden_size]；输出包括 post_mix、comb_mix 和 layer_input。
- 已有情况：库存无对应族
- 注意：Ascend 实际 n_splits=1；上游测试覆盖 509/1021，但源码注释声称 token 数需整除 16，这两项先验收。生成中间量的矩阵乘不应混入目标采集。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hidden_size":1280,"mhc_mult":4,"n1":509,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"hidden_size":5120,"mhc_mult":4,"n1":8192,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"hidden_size":1280,"mhc_mult":4,"n1":1021,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"hidden_size":5120,"mhc_mult":4,"n1":512,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"hidden_size":2560,"mhc_mult":4,"n1":1024,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"hidden_size":4096,"mhc_mult":4,"n1":2048,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"hidden_size":4160,"mhc_mult":4,"n1":1021,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"hidden_size":1280,"mhc_mult":4,"n1":1024,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"hidden_size":1280,"mhc_mult":4,"n1":2048,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"hidden_size":1280,"mhc_mult":4,"n1":512,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"hidden_size":1280,"mhc_mult":4,"n1":8192,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"hidden_size":2560,"mhc_mult":4,"n1":1021,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"hidden_size":2560,"mhc_mult":4,"n1":2048,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"hidden_size":2560,"mhc_mult":4,"n1":509,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"hidden_size":2560,"mhc_mult":4,"n1":512,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"hidden_size":2560,"mhc_mult":4,"n1":8192,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"hidden_size":4096,"mhc_mult":4,"n1":1021,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"hidden_size":4096,"mhc_mult":4,"n1":1024,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"hidden_size":4096,"mhc_mult":4,"n1":509,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"hidden_size":4096,"mhc_mult":4,"n1":512,"n_splits":1,"repeat":10}` | 上游测试参数 | 待核/未命中 |

## mhc_fn_normw_merge_fwd

- 实现：`tile_kernels/mhc/norm_fn_asc.py`
- 上游测试：`tests/mhc/test_norm_fn.py`
- 输入合同：fn FP32 [24,4*hidden_size]；normw FP32 [4*hidden_size]；反向另需同 fn 形状梯度。
- 已有情况：库存无对应族
- 注意：仅扩展 hidden_size；该入口与 token 数无关。扩展尺寸满足源码分块整除约束，仍需设备验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"dtype":"fp32","hidden_size":64,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 02 | `{"dtype":"fp32","hidden_size":8192,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 03 | `{"dtype":"fp32","hidden_size":1024,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 04 | `{"dtype":"fp32","hidden_size":128,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 05 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"dtype":"fp32","hidden_size":1536,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 07 | `{"dtype":"fp32","hidden_size":1792,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 08 | `{"dtype":"fp32","hidden_size":192,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 09 | `{"dtype":"fp32","hidden_size":2048,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 10 | `{"dtype":"fp32","hidden_size":256,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 11 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"dtype":"fp32","hidden_size":3072,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 13 | `{"dtype":"fp32","hidden_size":320,"mhc_mult":4}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"dtype":"fp32","hidden_size":3584,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 15 | `{"dtype":"fp32","hidden_size":384,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 16 | `{"dtype":"fp32","hidden_size":4096,"mhc_mult":4}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"dtype":"fp32","hidden_size":4608,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 18 | `{"dtype":"fp32","hidden_size":512,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 19 | `{"dtype":"fp32","hidden_size":5120,"mhc_mult":4}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"dtype":"fp32","hidden_size":6144,"mhc_mult":4}` | 扩展 | 待核/未命中 |

## mhc_fn_normw_merge_bwd

- 实现：`tile_kernels/mhc/norm_fn_asc.py`
- 上游测试：`tests/mhc/test_norm_fn.py`
- 输入合同：fn FP32 [24,4*hidden_size]；normw FP32 [4*hidden_size]；反向另需同 fn 形状梯度。
- 已有情况：库存无对应族
- 注意：仅扩展 hidden_size；该入口与 token 数无关。扩展尺寸满足源码分块整除约束，仍需设备验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"dtype":"fp32","hidden_size":64,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 02 | `{"dtype":"fp32","hidden_size":8192,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 03 | `{"dtype":"fp32","hidden_size":1024,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 04 | `{"dtype":"fp32","hidden_size":128,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 05 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"dtype":"fp32","hidden_size":1536,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 07 | `{"dtype":"fp32","hidden_size":1792,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 08 | `{"dtype":"fp32","hidden_size":192,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 09 | `{"dtype":"fp32","hidden_size":2048,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 10 | `{"dtype":"fp32","hidden_size":256,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 11 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"dtype":"fp32","hidden_size":3072,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 13 | `{"dtype":"fp32","hidden_size":320,"mhc_mult":4}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"dtype":"fp32","hidden_size":3584,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 15 | `{"dtype":"fp32","hidden_size":384,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 16 | `{"dtype":"fp32","hidden_size":4096,"mhc_mult":4}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"dtype":"fp32","hidden_size":4608,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 18 | `{"dtype":"fp32","hidden_size":512,"mhc_mult":4}` | 扩展 | 待核/未命中 |
| 19 | `{"dtype":"fp32","hidden_size":5120,"mhc_mult":4}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"dtype":"fp32","hidden_size":6144,"mhc_mult":4}` | 扩展 | 待核/未命中 |

## mhc_reduce_partials_and_rmsnorm_fwd

- 实现：`tile_kernels/mhc/norm_fn_asc.py`
- 上游测试：`tests/mhc/test_norm_fn.py`
- 输入合同：输入全为 FP32：out_mul_splitted [1,n1,1,24]、sqrsum_splitted [1,n1,1]；输出 [n1,1,24]、[n1,1]、[n1,24]。rms_group_size=4*hidden_size、eps=1e-6；正向 n_splits=1。
- 已有情况：库存无对应族
- 注意：扩展 token 数以覆盖不同规模；尚需设备验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4,"n1":128,"n_splits":1}` | 扩展 | 待核/未命中 |
| 02 | `{"dtype":"fp32","hidden_size":7168,"mhc_mult":4,"n1":8192,"n_splits":1}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"dtype":"fp32","hidden_size":320,"mhc_mult":4,"n1":1024,"n_splits":1}` | 扩展 | 待核/未命中 |
| 04 | `{"dtype":"fp32","hidden_size":7168,"mhc_mult":4,"n1":8001,"n_splits":1}` | 扩展 | 待核/未命中 |
| 05 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4,"n1":4096,"n_splits":1}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"dtype":"fp32","hidden_size":4096,"mhc_mult":4,"n1":512,"n_splits":1}` | 扩展 | 待核/未命中 |
| 07 | `{"dtype":"fp32","hidden_size":5120,"mhc_mult":4,"n1":1024,"n_splits":1}` | 扩展 | 待核/未命中 |
| 08 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4,"n1":1024,"n_splits":1}` | 扩展 | 待核/未命中 |
| 09 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4,"n1":4096,"n_splits":1}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4,"n1":512,"n_splits":1}` | 扩展 | 待核/未命中 |
| 11 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4,"n1":8001,"n_splits":1}` | 扩展 | 待核/未命中 |
| 12 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4,"n1":8192,"n_splits":1}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4,"n1":1024,"n_splits":1}` | 扩展 | 待核/未命中 |
| 14 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4,"n1":128,"n_splits":1}` | 扩展 | 待核/未命中 |
| 15 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4,"n1":512,"n_splits":1}` | 扩展 | 待核/未命中 |
| 16 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4,"n1":8001,"n_splits":1}` | 扩展 | 待核/未命中 |
| 17 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4,"n1":8192,"n_splits":1}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"dtype":"fp32","hidden_size":320,"mhc_mult":4,"n1":128,"n_splits":1}` | 扩展 | 待核/未命中 |
| 19 | `{"dtype":"fp32","hidden_size":320,"mhc_mult":4,"n1":4096,"n_splits":1}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"dtype":"fp32","hidden_size":320,"mhc_mult":4,"n1":512,"n_splits":1}` | 扩展 | 待核/未命中 |

## mhc_reduce_partials_and_rmsnorm_bwd

- 实现：`tile_kernels/mhc/norm_fn_asc.py`
- 上游测试：`tests/mhc/test_norm_fn.py`
- 输入合同：输入全为 FP32：out_grad [n1,24]、out_mul [n1,1,24]、sqrsum [n1,1]；输出为后两项的同形状梯度。rms_group_size=4*hidden_size、eps=1e-6；正向 n_splits=1。
- 已有情况：库存无对应族
- 注意：扩展 token 数以覆盖不同规模；尚需设备验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4,"n1":128,"n_splits":1}` | 扩展 | 待核/未命中 |
| 02 | `{"dtype":"fp32","hidden_size":7168,"mhc_mult":4,"n1":8192,"n_splits":1}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"dtype":"fp32","hidden_size":320,"mhc_mult":4,"n1":1024,"n_splits":1}` | 扩展 | 待核/未命中 |
| 04 | `{"dtype":"fp32","hidden_size":7168,"mhc_mult":4,"n1":8001,"n_splits":1}` | 扩展 | 待核/未命中 |
| 05 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4,"n1":4096,"n_splits":1}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"dtype":"fp32","hidden_size":4096,"mhc_mult":4,"n1":512,"n_splits":1}` | 扩展 | 待核/未命中 |
| 07 | `{"dtype":"fp32","hidden_size":5120,"mhc_mult":4,"n1":1024,"n_splits":1}` | 扩展 | 待核/未命中 |
| 08 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4,"n1":1024,"n_splits":1}` | 扩展 | 待核/未命中 |
| 09 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4,"n1":4096,"n_splits":1}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4,"n1":512,"n_splits":1}` | 扩展 | 待核/未命中 |
| 11 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4,"n1":8001,"n_splits":1}` | 扩展 | 待核/未命中 |
| 12 | `{"dtype":"fp32","hidden_size":1280,"mhc_mult":4,"n1":8192,"n_splits":1}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4,"n1":1024,"n_splits":1}` | 扩展 | 待核/未命中 |
| 14 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4,"n1":128,"n_splits":1}` | 扩展 | 待核/未命中 |
| 15 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4,"n1":512,"n_splits":1}` | 扩展 | 待核/未命中 |
| 16 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4,"n1":8001,"n_splits":1}` | 扩展 | 待核/未命中 |
| 17 | `{"dtype":"fp32","hidden_size":2560,"mhc_mult":4,"n1":8192,"n_splits":1}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"dtype":"fp32","hidden_size":320,"mhc_mult":4,"n1":128,"n_splits":1}` | 扩展 | 待核/未命中 |
| 19 | `{"dtype":"fp32","hidden_size":320,"mhc_mult":4,"n1":4096,"n_splits":1}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"dtype":"fp32","hidden_size":320,"mhc_mult":4,"n1":512,"n_splits":1}` | 扩展 | 待核/未命中 |

## mhc_multilayer_recompute

- 实现：`tile_kernels/mhc/multilayer_recompute_asc.py`
- 上游测试：`tests/mhc/test_multilayer_recompute.py`
- 输入合同：initial residual BF16 [bs,seq,4,hidden]；各层 BF16 数据与 FP32 mix 的列表按 num_layers/num_post 构造。
- 已有情况：库存无对应族
- 注意：官方 17 组加 3 组扩展；大 shape 和层数需要先核对显存，不能默认可在 hidev 运行。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"bs":1,"hidden":1280,"mhc_mult":4,"num_layers":1,"num_post":1,"seq":8192}` | 扩展 | 待核/未命中 |
| 02 | `{"bs":1,"hidden":1280,"mhc_mult":4,"num_layers":10,"num_post":10,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"bs":1,"hidden":1280,"mhc_mult":4,"num_layers":10,"num_post":9,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"bs":1,"hidden":2304,"mhc_mult":4,"num_layers":10,"num_post":10,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"bs":1,"hidden":2304,"mhc_mult":4,"num_layers":10,"num_post":9,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"bs":1,"hidden":2560,"mhc_mult":4,"num_layers":1,"num_post":1,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"bs":1,"hidden":2560,"mhc_mult":4,"num_layers":10,"num_post":10,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"bs":1,"hidden":2560,"mhc_mult":4,"num_layers":10,"num_post":9,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"bs":1,"hidden":2560,"mhc_mult":4,"num_layers":3,"num_post":2,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"bs":1,"hidden":2560,"mhc_mult":4,"num_layers":3,"num_post":3,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"bs":1,"hidden":4096,"mhc_mult":4,"num_layers":1,"num_post":1,"seq":8192}` | 扩展 | 待核/未命中 |
| 12 | `{"bs":1,"hidden":4096,"mhc_mult":4,"num_layers":10,"num_post":10,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"bs":1,"hidden":4096,"mhc_mult":4,"num_layers":10,"num_post":9,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"bs":1,"hidden":5120,"mhc_mult":4,"num_layers":1,"num_post":1,"seq":8192}` | 扩展 | 待核/未命中 |
| 15 | `{"bs":1,"hidden":5120,"mhc_mult":4,"num_layers":10,"num_post":10,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"bs":1,"hidden":5120,"mhc_mult":4,"num_layers":10,"num_post":9,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"bs":1,"hidden":7168,"mhc_mult":4,"num_layers":10,"num_post":10,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"bs":1,"hidden":7168,"mhc_mult":4,"num_layers":10,"num_post":9,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"bs":1,"hidden":8192,"mhc_mult":4,"num_layers":10,"num_post":10,"seq":8192}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"bs":1,"hidden":8192,"mhc_mult":4,"num_layers":10,"num_post":9,"seq":8192}` | 上游测试参数 | 待核/未命中 |

## moe_topk_gate

- 实现：`tile_kernels/moe/topk_gate_asc.py`
- 上游测试：`tests/moe/test_topk_gate.py`
- 输入合同：scores FP32 [num_tokens,num_experts]；输出索引 INT64 [num_tokens,num_topk]。
- 已有情况：库存无对应族
- 注意：扩展组合满足公开接口的 topk 范围约束，具体设备可运行性待确认。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"num_experts":1,"num_tokens":1,"num_topk":1}` | 扩展 | 待核/未命中 |
| 02 | `{"num_experts":35,"num_tokens":8001,"num_topk":9}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"num_experts":1,"num_tokens":1024,"num_topk":1}` | 扩展 | 待核/未命中 |
| 04 | `{"num_experts":1025,"num_tokens":8001,"num_topk":9}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"num_experts":1025,"num_tokens":128,"num_topk":32}` | 扩展 | 待核/未命中 |
| 06 | `{"num_experts":1025,"num_tokens":512,"num_topk":1}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"num_experts":35,"num_tokens":1,"num_topk":32}` | 扩展 | 待核/未命中 |
| 08 | `{"num_experts":35,"num_tokens":128,"num_topk":1}` | 扩展 | 待核/未命中 |
| 09 | `{"num_experts":1,"num_tokens":8001,"num_topk":1}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"num_experts":1025,"num_tokens":1,"num_topk":9}` | 扩展 | 待核/未命中 |
| 11 | `{"num_experts":1025,"num_tokens":1024,"num_topk":32}` | 扩展 | 待核/未命中 |
| 12 | `{"num_experts":35,"num_tokens":1024,"num_topk":9}` | 扩展 | 待核/未命中 |
| 13 | `{"num_experts":35,"num_tokens":512,"num_topk":32}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"num_experts":1,"num_tokens":128,"num_topk":1}` | 扩展 | 待核/未命中 |
| 15 | `{"num_experts":1,"num_tokens":512,"num_topk":1}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"num_experts":1025,"num_tokens":128,"num_topk":9}` | 扩展 | 待核/未命中 |
| 17 | `{"num_experts":1025,"num_tokens":512,"num_topk":9}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"num_experts":1025,"num_tokens":8001,"num_topk":32}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"num_experts":1025,"num_tokens":1,"num_topk":1}` | 扩展 | 待核/未命中 |
| 20 | `{"num_experts":1025,"num_tokens":1,"num_topk":32}` | 扩展 | 待核/未命中 |

## moe_topk_gate_forward

- 实现：`tile_kernels/moe/moe_topk_gate_forward_asc.py`
- 上游测试：`tests/moe/test_moe_topk_gate_forward.py`
- 输入合同：logits FP32；forward 的行数为 num_tokens+num_padded_tokens，backward 为 num_seqs*(num_tokens+num_padded_tokens)；专家数及可选项见 case，上游测试生成其余输入。
- 已有情况：库存无对应族

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"bias_exists":false,"fix_routing":false,"force_random_exists":false,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":108,"num_shared_experts":2,"num_tokens":512,"num_topk":6,"scores_exists":true,"use_shared_as_routed":false}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"bias_exists":true,"fix_routing":true,"force_random_exists":true,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":96,"num_shared_experts":2,"num_tokens":8001,"num_topk":6,"scores_exists":true,"use_shared_as_routed":true}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"bias_exists":false,"fix_routing":false,"force_random_exists":false,"image_bias_exists":false,"num_padded_tokens":10,"num_routed_experts":256,"num_shared_experts":2,"num_tokens":8001,"num_topk":8,"scores_exists":true,"use_shared_as_routed":true}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"bias_exists":false,"fix_routing":true,"force_random_exists":true,"image_bias_exists":true,"num_padded_tokens":0,"num_routed_experts":72,"num_shared_experts":1,"num_tokens":512,"num_topk":6,"scores_exists":true,"use_shared_as_routed":false}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"bias_exists":true,"fix_routing":false,"force_random_exists":false,"image_bias_exists":true,"num_padded_tokens":0,"num_routed_experts":128,"num_shared_experts":2,"num_tokens":512,"num_topk":6,"scores_exists":true,"use_shared_as_routed":true}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"bias_exists":true,"fix_routing":false,"force_random_exists":true,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":144,"num_shared_experts":2,"num_tokens":8001,"num_topk":6,"scores_exists":true,"use_shared_as_routed":false}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"bias_exists":false,"fix_routing":true,"force_random_exists":false,"image_bias_exists":false,"num_padded_tokens":10,"num_routed_experts":16,"num_shared_experts":2,"num_tokens":512,"num_topk":6,"scores_exists":true,"use_shared_as_routed":false}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"bias_exists":true,"fix_routing":false,"force_random_exists":false,"image_bias_exists":false,"num_padded_tokens":10,"num_routed_experts":72,"num_shared_experts":1,"num_tokens":8001,"num_topk":6,"scores_exists":true,"use_shared_as_routed":true}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"bias_exists":true,"fix_routing":true,"force_random_exists":true,"image_bias_exists":true,"num_padded_tokens":0,"num_routed_experts":256,"num_shared_experts":2,"num_tokens":512,"num_topk":8,"scores_exists":true,"use_shared_as_routed":false}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"bias_exists":false,"fix_routing":false,"force_random_exists":false,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":32,"num_shared_experts":2,"num_tokens":512,"num_topk":6,"scores_exists":true,"use_shared_as_routed":false}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"bias_exists":false,"fix_routing":false,"force_random_exists":false,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":36,"num_shared_experts":2,"num_tokens":512,"num_topk":6,"scores_exists":true,"use_shared_as_routed":false}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"bias_exists":false,"fix_routing":false,"force_random_exists":false,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":64,"num_shared_experts":2,"num_tokens":512,"num_topk":6,"scores_exists":true,"use_shared_as_routed":false}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"bias_exists":false,"fix_routing":false,"force_random_exists":false,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":96,"num_shared_experts":2,"num_tokens":512,"num_topk":6,"scores_exists":true,"use_shared_as_routed":false}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"bias_exists":false,"fix_routing":true,"force_random_exists":false,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":144,"num_shared_experts":2,"num_tokens":512,"num_topk":6,"scores_exists":true,"use_shared_as_routed":true}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"bias_exists":false,"fix_routing":true,"force_random_exists":true,"image_bias_exists":false,"num_padded_tokens":10,"num_routed_experts":128,"num_shared_experts":2,"num_tokens":8001,"num_topk":6,"scores_exists":true,"use_shared_as_routed":false}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"bias_exists":true,"fix_routing":false,"force_random_exists":true,"image_bias_exists":true,"num_padded_tokens":0,"num_routed_experts":16,"num_shared_experts":2,"num_tokens":8001,"num_topk":6,"scores_exists":true,"use_shared_as_routed":true}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"bias_exists":true,"fix_routing":true,"force_random_exists":true,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":108,"num_shared_experts":2,"num_tokens":8001,"num_topk":6,"scores_exists":true,"use_shared_as_routed":true}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"bias_exists":true,"fix_routing":true,"force_random_exists":true,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":32,"num_shared_experts":2,"num_tokens":8001,"num_topk":6,"scores_exists":true,"use_shared_as_routed":true}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"bias_exists":true,"fix_routing":true,"force_random_exists":true,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":36,"num_shared_experts":2,"num_tokens":8001,"num_topk":6,"scores_exists":true,"use_shared_as_routed":true}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"bias_exists":true,"fix_routing":true,"force_random_exists":true,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":64,"num_shared_experts":2,"num_tokens":8001,"num_topk":6,"scores_exists":true,"use_shared_as_routed":true}` | 上游测试参数 | 待核/未命中 |

## moe_topk_gate_backward

- 实现：`tile_kernels/moe/moe_topk_gate_backward_asc.py`
- 上游测试：`tests/moe/test_moe_topk_gate_backward.py`
- 输入合同：logits FP32；forward 的行数为 num_tokens+num_padded_tokens，backward 为 num_seqs*(num_tokens+num_padded_tokens)；专家数及可选项见 case，上游测试生成其余输入。
- 已有情况：库存无对应族

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"aux_exists":false,"bias_exists":false,"fix_routing":false,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":108,"num_seqs":1,"num_shared_experts":2,"num_tokens":512,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"aux_exists":true,"bias_exists":true,"fix_routing":true,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":96,"num_seqs":2,"num_shared_experts":2,"num_tokens":8001,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"aux_exists":false,"bias_exists":false,"fix_routing":false,"image_bias_exists":false,"num_padded_tokens":10,"num_routed_experts":256,"num_seqs":2,"num_shared_experts":2,"num_tokens":8001,"num_topk":8}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"aux_exists":false,"bias_exists":true,"fix_routing":true,"image_bias_exists":true,"num_padded_tokens":0,"num_routed_experts":72,"num_seqs":1,"num_shared_experts":1,"num_tokens":512,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"aux_exists":true,"bias_exists":false,"fix_routing":false,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":72,"num_seqs":2,"num_shared_experts":1,"num_tokens":8001,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"aux_exists":true,"bias_exists":false,"fix_routing":false,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":128,"num_seqs":1,"num_shared_experts":2,"num_tokens":512,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"aux_exists":true,"bias_exists":true,"fix_routing":true,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":256,"num_seqs":1,"num_shared_experts":2,"num_tokens":512,"num_topk":8}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"aux_exists":false,"bias_exists":false,"fix_routing":true,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":144,"num_seqs":1,"num_shared_experts":2,"num_tokens":8001,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"aux_exists":false,"bias_exists":true,"fix_routing":false,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":16,"num_seqs":2,"num_shared_experts":2,"num_tokens":512,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"aux_exists":false,"bias_exists":false,"fix_routing":false,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":32,"num_seqs":1,"num_shared_experts":2,"num_tokens":512,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"aux_exists":false,"bias_exists":false,"fix_routing":false,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":36,"num_seqs":1,"num_shared_experts":2,"num_tokens":512,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"aux_exists":false,"bias_exists":false,"fix_routing":false,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":64,"num_seqs":1,"num_shared_experts":2,"num_tokens":512,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"aux_exists":false,"bias_exists":false,"fix_routing":false,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":96,"num_seqs":1,"num_shared_experts":2,"num_tokens":512,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"aux_exists":false,"bias_exists":true,"fix_routing":true,"image_bias_exists":false,"num_padded_tokens":0,"num_routed_experts":128,"num_seqs":2,"num_shared_experts":2,"num_tokens":8001,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"aux_exists":true,"bias_exists":false,"fix_routing":true,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":16,"num_seqs":1,"num_shared_experts":2,"num_tokens":8001,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"aux_exists":true,"bias_exists":true,"fix_routing":false,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":144,"num_seqs":2,"num_shared_experts":2,"num_tokens":512,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"aux_exists":true,"bias_exists":true,"fix_routing":true,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":108,"num_seqs":2,"num_shared_experts":2,"num_tokens":8001,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"aux_exists":true,"bias_exists":true,"fix_routing":true,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":32,"num_seqs":2,"num_shared_experts":2,"num_tokens":8001,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"aux_exists":true,"bias_exists":true,"fix_routing":true,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":36,"num_seqs":2,"num_shared_experts":2,"num_tokens":8001,"num_topk":6}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"aux_exists":true,"bias_exists":true,"fix_routing":true,"image_bias_exists":true,"num_padded_tokens":10,"num_routed_experts":64,"num_seqs":2,"num_shared_experts":2,"num_tokens":8001,"num_topk":6}` | 上游测试参数 | 待核/未命中 |

## moe_normalize_weight

- 实现：`tile_kernels/moe/normalize_weight_asc.py`
- 上游测试：`tests/moe/test_normalize_weight.py`
- 输入合同：topk_weights FP32 [num_tokens,num_topk]，连续。
- 已有情况：已有 4 个 case
- 注意：按公开 API 直接构造确定的输入 shape；不同于上游先随机路由后决定行数的 fixture，需独立做数值校验。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"dtype":"fp32","num_tokens":1,"num_topk":1}` | 扩展 | 待核/未命中 |
| 02 | `{"dtype":"fp32","num_tokens":8001,"num_topk":9}` | 扩展 | 待核/未命中 |
| 03 | `{"dtype":"fp32","num_tokens":127,"num_topk":32}` | 扩展 | 待核/未命中 |
| 04 | `{"dtype":"fp32","num_tokens":128,"num_topk":6}` | 扩展 | 待核/未命中 |
| 05 | `{"dtype":"fp32","num_tokens":4001,"num_topk":8}` | 扩展 | 待核/未命中 |
| 06 | `{"dtype":"fp32","num_tokens":512,"num_topk":1}` | 扩展 | 待核/未命中 |
| 07 | `{"dtype":"fp32","num_tokens":1,"num_topk":32}` | 扩展 | 待核/未命中 |
| 08 | `{"dtype":"fp32","num_tokens":1,"num_topk":6}` | 扩展 | 待核/未命中 |
| 09 | `{"dtype":"fp32","num_tokens":1,"num_topk":8}` | 扩展 | normalize-n1-k8 |
| 10 | `{"dtype":"fp32","num_tokens":1,"num_topk":9}` | 扩展 | 待核/未命中 |
| 11 | `{"dtype":"fp32","num_tokens":127,"num_topk":1}` | 扩展 | 待核/未命中 |
| 12 | `{"dtype":"fp32","num_tokens":127,"num_topk":6}` | 扩展 | 待核/未命中 |
| 13 | `{"dtype":"fp32","num_tokens":127,"num_topk":8}` | 扩展 | 待核/未命中 |
| 14 | `{"dtype":"fp32","num_tokens":127,"num_topk":9}` | 扩展 | 待核/未命中 |
| 15 | `{"dtype":"fp32","num_tokens":128,"num_topk":1}` | 扩展 | 待核/未命中 |
| 16 | `{"dtype":"fp32","num_tokens":128,"num_topk":32}` | 扩展 | 待核/未命中 |
| 17 | `{"dtype":"fp32","num_tokens":128,"num_topk":8}` | 扩展 | 待核/未命中 |
| 18 | `{"dtype":"fp32","num_tokens":128,"num_topk":9}` | 扩展 | 待核/未命中 |
| 19 | `{"dtype":"fp32","num_tokens":4001,"num_topk":1}` | 扩展 | 待核/未命中 |
| 20 | `{"dtype":"fp32","num_tokens":4001,"num_topk":32}` | 扩展 | 待核/未命中 |

## quant_cast

- 实现：`tile_kernels/quant/cast_asc.py`
- 上游测试：`tests/quant/test_cast.py`
- 输入合同：输入 FP32 [shape[0]]，输出 BF16；Ascend 上游测试的 stochastic_rounding=True。
- 已有情况：库存无对应族
- 注意：上游参数组合候选；具体输入以对应测试构造器为准，合法性和数值正确性尚未在 hidev 逐例验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[65536],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[134217856],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1024128],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1024132],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1024160],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1024256],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1024384],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1048576],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1048580],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1048608],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1048704],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1048832],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1310720],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1310724],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1310752],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1310848],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1310976],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[134217728],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1572864],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"in_dtype":"fp32","out_dtype":"bf16","shape":[1572868],"stochastic_rounding":true}` | 上游测试参数 | 待核/未命中 |

## quant_cast_back_per_token

- 实现：`tile_kernels/quant/cast_back_asc.py`
- 上游测试：`tests/quant/test_cast_back.py`
- 输入合同：量化输入逻辑形状 [num_tokens,hidden]，格式 fmt；输出 dtype=out_dtype；scale 布局及粒度见参数。
- 已有情况：cast back 合计已有 4 个 case
- 注意：上游参数组合候选；具体输入以对应测试构造器为准，合法性和数值正确性尚未在 hidev 逐例验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"fmt":"e2m1","hidden":128,"num_per_channels":32,"num_tokens":512,"out_dtype":"bf16","round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"fmt":"e4m3","hidden":768,"num_per_channels":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"fmt":"e2m1","hidden":128,"num_per_channels":32,"num_tokens":512,"out_dtype":"bf16","round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"fmt":"e4m3","hidden":7168,"num_per_channels":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"fmt":"e4m3","hidden":2048,"num_per_channels":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | castback-n8001-h2048-fp32 |
| 06 | `{"fmt":"e2m1","hidden":2560,"num_per_channels":32,"num_tokens":512,"out_dtype":"bf16","round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"fmt":"e2m1","hidden":3072,"num_per_channels":32,"num_tokens":512,"out_dtype":"fp32","round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"fmt":"e2m1","hidden":384,"num_per_channels":32,"num_tokens":8001,"out_dtype":"bf16","round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"fmt":"e4m3","hidden":4096,"num_per_channels":32,"num_tokens":512,"out_dtype":"bf16","round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"fmt":"e2m1","hidden":6144,"num_per_channels":32,"num_tokens":512,"out_dtype":"bf16","round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"fmt":"e2m1","hidden":2048,"num_per_channels":32,"num_tokens":512,"out_dtype":"bf16","round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"fmt":"e2m1","hidden":4096,"num_per_channels":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"fmt":"e2m1","hidden":7168,"num_per_channels":32,"num_tokens":512,"out_dtype":"bf16","round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"fmt":"e2m1","hidden":768,"num_per_channels":32,"num_tokens":512,"out_dtype":"bf16","round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"fmt":"e4m3","hidden":2560,"num_per_channels":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"fmt":"e4m3","hidden":3072,"num_per_channels":32,"num_tokens":8001,"out_dtype":"bf16","round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"fmt":"e4m3","hidden":384,"num_per_channels":32,"num_tokens":512,"out_dtype":"fp32","round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"fmt":"e4m3","hidden":6144,"num_per_channels":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"fmt":"e4m3","hidden":128,"num_per_channels":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"fmt":"e2m1","hidden":128,"num_per_channels":32,"num_tokens":512,"out_dtype":"bf16","round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |

## quant_cast_back_block

- 实现：`tile_kernels/quant/cast_back_asc.py`
- 上游测试：`tests/quant/test_cast_back.py`
- 输入合同：量化输入逻辑形状 [num_tokens,hidden]，格式 fmt；输出 dtype=out_dtype；scale 粒度为 (num_per_tokens,num_per_channels)。
- 已有情况：cast back 合计已有 4 个 case
- 注意：上游参数组合候选；具体输入以对应测试构造器为准，合法性和数值正确性尚未在 hidev 逐例验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"fmt":"e2m1","hidden":128,"num_per_channels":1,"num_per_tokens":32,"num_tokens":512,"out_dtype":"bf16","round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"fmt":"e4m3","hidden":768,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"fmt":"e2m1","hidden":128,"num_per_channels":1,"num_per_tokens":32,"num_tokens":512,"out_dtype":"bf16","round_sf":true,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"fmt":"e4m3","hidden":7168,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"fmt":"e2m1","hidden":192,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"fmt":"e2m1","hidden":2048,"num_per_channels":32,"num_per_tokens":32,"num_tokens":512,"out_dtype":"bf16","round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"fmt":"e4m3","hidden":2560,"num_per_channels":1,"num_per_tokens":32,"num_tokens":512,"out_dtype":"fp32","round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"fmt":"e4m3","hidden":3072,"num_per_channels":1,"num_per_tokens":32,"num_tokens":8001,"out_dtype":"bf16","round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"fmt":"e2m1","hidden":384,"num_per_channels":1,"num_per_tokens":32,"num_tokens":512,"out_dtype":"bf16","round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"fmt":"e2m1","hidden":4096,"num_per_channels":1,"num_per_tokens":32,"num_tokens":512,"out_dtype":"bf16","round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"fmt":"e2m1","hidden":6144,"num_per_channels":1,"num_per_tokens":32,"num_tokens":512,"out_dtype":"bf16","round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"fmt":"e2m1","hidden":2560,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8001,"out_dtype":"bf16","round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"fmt":"e2m1","hidden":7168,"num_per_channels":1,"num_per_tokens":32,"num_tokens":512,"out_dtype":"bf16","round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"fmt":"e2m1","hidden":768,"num_per_channels":1,"num_per_tokens":32,"num_tokens":512,"out_dtype":"bf16","round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"fmt":"e4m3","hidden":2048,"num_per_channels":1,"num_per_tokens":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | castback-n8001-h2048-fp32 |
| 16 | `{"fmt":"e4m3","hidden":384,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"fmt":"e4m3","hidden":4096,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"fmt":"e4m3","hidden":6144,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"fmt":"e2m1","hidden":3072,"num_per_channels":32,"num_per_tokens":32,"num_tokens":512,"out_dtype":"fp32","round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"fmt":"e4m3","hidden":128,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8001,"out_dtype":"fp32","round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |

## quant_norm_forward

- 实现：`tile_kernels/quant/norm_forward_asc.py`
- 上游测试：`tests/quant/test_norm_forward.py`
- 输入合同：输入 shape [num_tokens,hidden] 或 [batch_size,num_tokens,hidden]；输入 dtype=in_dtype 或 fmt，输出格式 fmt；row_padding 由参数规定。
- 已有情况：RMSNorm 已有 13 个 case
- 注意：上游参数组合候选；具体输入以对应测试构造器为准，合法性和数值正确性尚未在 hidev 逐例验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"batch_size":2,"eps":1e-06,"fmt":"bf16","has_residual":true,"hidden":128,"in_dtype":null,"mega_moe_block_m":0,"num_per_channels":null,"num_tokens":512,"out_scale":1.0,"round_sf":false,"row_padding":16,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"use_weight":false,"with_out_bf16":false,"with_rstd":false}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"batch_size":null,"eps":1e-06,"fmt":"fp32","has_residual":false,"hidden":768,"in_dtype":null,"mega_moe_block_m":0,"num_per_channels":null,"num_tokens":8001,"out_scale":1.0,"round_sf":false,"row_padding":16,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"use_weight":true,"with_out_bf16":false,"with_rstd":true}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"batch_size":2,"eps":1e-06,"fmt":"bf16","has_residual":true,"hidden":128,"in_dtype":null,"mega_moe_block_m":0,"num_per_channels":null,"num_tokens":512,"out_scale":1.0,"round_sf":false,"row_padding":16,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"use_weight":true,"with_out_bf16":false,"with_rstd":false}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"batch_size":null,"eps":1e-06,"fmt":"fp32","has_residual":false,"hidden":7168,"in_dtype":null,"mega_moe_block_m":0,"num_per_channels":null,"num_tokens":8001,"out_scale":1.0,"round_sf":false,"row_padding":16,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"use_weight":true,"with_out_bf16":false,"with_rstd":true}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"batch_size":null,"eps":1e-06,"fmt":"e4m3","has_residual":false,"hidden":192,"in_dtype":"bf16","mega_moe_block_m":0,"num_per_channels":32,"num_tokens":512,"out_scale":1.0,"round_sf":true,"row_padding":16,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"use_weight":false,"with_out_bf16":true,"with_rstd":true}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"batch_size":2,"eps":1e-06,"fmt":"e4m3","has_residual":true,"hidden":2048,"in_dtype":"fp32","mega_moe_block_m":0,"num_per_channels":32,"num_tokens":8001,"out_scale":1.0,"round_sf":true,"row_padding":16,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"use_weight":true,"with_out_bf16":false,"with_rstd":false}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"batch_size":null,"eps":1e-06,"fmt":"e4m3","has_residual":false,"hidden":2560,"in_dtype":"fp32","mega_moe_block_m":0,"num_per_channels":32,"num_tokens":8001,"out_scale":1.0,"round_sf":false,"row_padding":16,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"use_weight":false,"with_out_bf16":true,"with_rstd":true}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"batch_size":2,"eps":1e-06,"fmt":"e4m3","has_residual":true,"hidden":3072,"in_dtype":"bf16","mega_moe_block_m":0,"num_per_channels":32,"num_tokens":8001,"out_scale":1.0,"round_sf":true,"row_padding":16,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"use_weight":true,"with_out_bf16":false,"with_rstd":false}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"batch_size":2,"eps":1e-06,"fmt":"fp32","has_residual":true,"hidden":384,"in_dtype":null,"mega_moe_block_m":0,"num_per_channels":null,"num_tokens":512,"out_scale":1.0,"round_sf":false,"row_padding":16,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"use_weight":false,"with_out_bf16":false,"with_rstd":false}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"batch_size":null,"eps":1e-06,"fmt":"bf16","has_residual":false,"hidden":4096,"in_dtype":null,"mega_moe_block_m":0,"num_per_channels":null,"num_tokens":8001,"out_scale":1.0,"round_sf":false,"row_padding":16,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"use_weight":false,"with_out_bf16":false,"with_rstd":true}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"batch_size":null,"eps":1e-06,"fmt":"e4m3","has_residual":false,"hidden":6144,"in_dtype":"bf16","mega_moe_block_m":0,"num_per_channels":32,"num_tokens":512,"out_scale":1.0,"round_sf":false,"row_padding":16,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"use_weight":true,"with_out_bf16":true,"with_rstd":true}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"batch_size":2,"eps":1e-06,"fmt":"bf16","has_residual":true,"hidden":192,"in_dtype":null,"mega_moe_block_m":0,"num_per_channels":null,"num_tokens":8001,"out_scale":1.0,"round_sf":false,"row_padding":16,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"use_weight":true,"with_out_bf16":false,"with_rstd":false}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"batch_size":2,"eps":1e-06,"fmt":"e4m3","has_residual":true,"hidden":4096,"in_dtype":"fp32","mega_moe_block_m":0,"num_per_channels":32,"num_tokens":512,"out_scale":1.0,"round_sf":true,"row_padding":16,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"use_weight":true,"with_out_bf16":false,"with_rstd":false}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"batch_size":null,"eps":1e-06,"fmt":"e4m3","has_residual":false,"hidden":384,"in_dtype":"bf16","mega_moe_block_m":0,"num_per_channels":32,"num_tokens":8001,"out_scale":1.0,"round_sf":true,"row_padding":16,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"use_weight":true,"with_out_bf16":true,"with_rstd":true}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"batch_size":2,"eps":1e-06,"fmt":"e4m3","has_residual":true,"hidden":7168,"in_dtype":"bf16","mega_moe_block_m":0,"num_per_channels":32,"num_tokens":512,"out_scale":1.0,"round_sf":true,"row_padding":16,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"use_weight":false,"with_out_bf16":false,"with_rstd":false}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"batch_size":2,"eps":1e-06,"fmt":"e4m3","has_residual":true,"hidden":768,"in_dtype":"bf16","mega_moe_block_m":0,"num_per_channels":32,"num_tokens":512,"out_scale":1.0,"round_sf":true,"row_padding":16,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"use_weight":false,"with_out_bf16":false,"with_rstd":false}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"batch_size":null,"eps":1e-06,"fmt":"bf16","has_residual":false,"hidden":2048,"in_dtype":null,"mega_moe_block_m":0,"num_per_channels":null,"num_tokens":512,"out_scale":1.0,"round_sf":false,"row_padding":16,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"use_weight":false,"with_out_bf16":false,"with_rstd":true}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"batch_size":null,"eps":1e-06,"fmt":"e4m3","has_residual":false,"hidden":128,"in_dtype":"bf16","mega_moe_block_m":0,"num_per_channels":32,"num_tokens":8001,"out_scale":1.0,"round_sf":true,"row_padding":16,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"use_weight":false,"with_out_bf16":true,"with_rstd":true}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"batch_size":2,"eps":1e-06,"fmt":"e4m3","has_residual":true,"hidden":2560,"in_dtype":"bf16","mega_moe_block_m":0,"num_per_channels":32,"num_tokens":512,"out_scale":1.0,"round_sf":true,"row_padding":16,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"use_weight":true,"with_out_bf16":false,"with_rstd":false}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"batch_size":2,"eps":1e-06,"fmt":"e4m3","has_residual":true,"hidden":6144,"in_dtype":"fp32","mega_moe_block_m":0,"num_per_channels":32,"num_tokens":8001,"out_scale":1.0,"round_sf":true,"row_padding":16,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"use_weight":false,"with_out_bf16":false,"with_rstd":false}` | 上游测试参数 | 待核/未命中 |

## quant_norm_backward

- 实现：`tile_kernels/quant/norm_backward_asc.py`
- 上游测试：`tests/quant/test_norm_backward.py`
- 输入合同：norm_input/out_grad dtype=fmt，shape [num_tokens,hidden]；权重和其梯度按参数启用。
- 已有情况：库存无对应族
- 注意：上游参数组合候选；具体输入以对应测试构造器为准，合法性和数值正确性尚未在 hidev 逐例验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"accumulate":false,"eps":1e-06,"fmt":"bf16","has_out_grad":true,"has_residual_out_grad":false,"hidden":128,"num_sms":9,"num_tokens":512,"out_scale":1.0,"row_padding":0,"use_weight":false,"weight_grad_fmt":null}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"accumulate":true,"eps":1e-06,"fmt":"fp32","has_out_grad":true,"has_residual_out_grad":true,"hidden":768,"num_sms":28,"num_tokens":8001,"out_scale":0.3,"row_padding":16,"use_weight":true,"weight_grad_fmt":"fp32"}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"accumulate":false,"eps":1e-06,"fmt":"bf16","has_out_grad":true,"has_residual_out_grad":false,"hidden":128,"num_sms":9,"num_tokens":512,"out_scale":1.0,"row_padding":0,"use_weight":true,"weight_grad_fmt":null}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"accumulate":true,"eps":1e-06,"fmt":"fp32","has_out_grad":true,"has_residual_out_grad":true,"hidden":7168,"num_sms":28,"num_tokens":8001,"out_scale":0.3,"row_padding":16,"use_weight":true,"weight_grad_fmt":"fp32"}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"accumulate":true,"eps":1e-06,"fmt":"bf16","has_out_grad":true,"has_residual_out_grad":true,"hidden":2048,"num_sms":28,"num_tokens":512,"out_scale":0.3,"row_padding":16,"use_weight":true,"weight_grad_fmt":"bf16"}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"accumulate":false,"eps":1e-06,"fmt":"fp32","has_out_grad":true,"has_residual_out_grad":true,"hidden":2560,"num_sms":28,"num_tokens":8001,"out_scale":0.3,"row_padding":16,"use_weight":false,"weight_grad_fmt":null}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"accumulate":false,"eps":1e-06,"fmt":"fp32","has_out_grad":true,"has_residual_out_grad":false,"hidden":3072,"num_sms":9,"num_tokens":8001,"out_scale":1.0,"row_padding":0,"use_weight":false,"weight_grad_fmt":null}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"accumulate":true,"eps":1e-06,"fmt":"bf16","has_out_grad":true,"has_residual_out_grad":true,"hidden":384,"num_sms":28,"num_tokens":512,"out_scale":0.3,"row_padding":16,"use_weight":true,"weight_grad_fmt":"fp32"}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"accumulate":true,"eps":1e-06,"fmt":"bf16","has_out_grad":true,"has_residual_out_grad":true,"hidden":4096,"num_sms":28,"num_tokens":8001,"out_scale":0.3,"row_padding":16,"use_weight":true,"weight_grad_fmt":"bf16"}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"accumulate":true,"eps":1e-06,"fmt":"fp32","has_out_grad":true,"has_residual_out_grad":true,"hidden":6144,"num_sms":28,"num_tokens":512,"out_scale":0.3,"row_padding":16,"use_weight":true,"weight_grad_fmt":"bf16"}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"accumulate":false,"eps":1e-06,"fmt":"bf16","has_out_grad":true,"has_residual_out_grad":false,"hidden":6144,"num_sms":9,"num_tokens":8001,"out_scale":1.0,"row_padding":0,"use_weight":false,"weight_grad_fmt":null}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"accumulate":false,"eps":1e-06,"fmt":"bf16","has_out_grad":true,"has_residual_out_grad":false,"hidden":7168,"num_sms":9,"num_tokens":512,"out_scale":1.0,"row_padding":0,"use_weight":false,"weight_grad_fmt":null}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"accumulate":false,"eps":1e-06,"fmt":"bf16","has_out_grad":true,"has_residual_out_grad":false,"hidden":768,"num_sms":9,"num_tokens":512,"out_scale":1.0,"row_padding":0,"use_weight":false,"weight_grad_fmt":null}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"accumulate":false,"eps":1e-06,"fmt":"fp32","has_out_grad":true,"has_residual_out_grad":false,"hidden":2048,"num_sms":9,"num_tokens":8001,"out_scale":1.0,"row_padding":0,"use_weight":false,"weight_grad_fmt":null}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"accumulate":false,"eps":1e-06,"fmt":"fp32","has_out_grad":true,"has_residual_out_grad":false,"hidden":384,"num_sms":9,"num_tokens":8001,"out_scale":1.0,"row_padding":0,"use_weight":false,"weight_grad_fmt":null}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"accumulate":false,"eps":1e-06,"fmt":"fp32","has_out_grad":true,"has_residual_out_grad":false,"hidden":4096,"num_sms":9,"num_tokens":512,"out_scale":1.0,"row_padding":0,"use_weight":false,"weight_grad_fmt":null}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"accumulate":true,"eps":1e-06,"fmt":"bf16","has_out_grad":true,"has_residual_out_grad":true,"hidden":3072,"num_sms":28,"num_tokens":512,"out_scale":0.3,"row_padding":16,"use_weight":true,"weight_grad_fmt":"bf16"}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"accumulate":true,"eps":1e-06,"fmt":"fp32","has_out_grad":true,"has_residual_out_grad":true,"hidden":128,"num_sms":28,"num_tokens":8001,"out_scale":0.3,"row_padding":16,"use_weight":true,"weight_grad_fmt":"bf16"}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"accumulate":false,"eps":1e-06,"fmt":"bf16","has_out_grad":true,"has_residual_out_grad":false,"hidden":2560,"num_sms":9,"num_tokens":512,"out_scale":1.0,"row_padding":0,"use_weight":true,"weight_grad_fmt":null}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"accumulate":true,"eps":1e-06,"fmt":"bf16","has_out_grad":true,"has_residual_out_grad":true,"hidden":2560,"num_sms":28,"num_tokens":512,"out_scale":0.3,"row_padding":16,"use_weight":true,"weight_grad_fmt":"bf16"}` | 上游测试参数 | 待核/未命中 |

## quant_per_block_cast

- 实现：`tile_kernels/quant/per_block_cast_asc.py`
- 上游测试：`tests/quant/test_per_block_cast.py`
- 输入合同：输入 dtype=in_dtype，逻辑 shape [num_tokens,hidden]；输出格式 fmt，scale block=block_size。
- 已有情况：库存无对应族
- 注意：上游参数组合候选；具体输入以对应测试构造器为准，合法性和数值正确性尚未在 hidev 逐例验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"block_size":[32,32],"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"block_size":[32,32],"fmt":"e4m3","hidden":768,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"block_size":[32,32],"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_tokens":512,"round_sf":true,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"block_size":[32,32],"fmt":"e4m3","hidden":7168,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"block_size":[32,32],"fmt":"e4m3","hidden":2048,"in_dtype":"fp32","num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"block_size":[32,32],"fmt":"e2m1","hidden":2560,"in_dtype":"bf16","num_tokens":512,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"block_size":[32,32],"fmt":"e2m1","hidden":3072,"in_dtype":"bf16","num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"block_size":[32,32],"fmt":"e2m1","hidden":384,"in_dtype":"fp32","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"block_size":[32,32],"fmt":"e4m3","hidden":4096,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"block_size":[32,32],"fmt":"e2m1","hidden":6144,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"block_size":[32,32],"fmt":"e2m1","hidden":2048,"in_dtype":"bf16","num_tokens":512,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"block_size":[32,32],"fmt":"e2m1","hidden":4096,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"block_size":[32,32],"fmt":"e2m1","hidden":7168,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"block_size":[32,32],"fmt":"e2m1","hidden":768,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"block_size":[32,32],"fmt":"e4m3","hidden":2560,"in_dtype":"fp32","num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"block_size":[32,32],"fmt":"e4m3","hidden":3072,"in_dtype":"fp32","num_tokens":512,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"block_size":[32,32],"fmt":"e4m3","hidden":384,"in_dtype":"bf16","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"block_size":[32,32],"fmt":"e4m3","hidden":6144,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"block_size":[32,32],"fmt":"e4m3","hidden":128,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"block_size":[32,32],"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_tokens":512,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |

## quant_per_block_cast_lossless

- 实现：`tile_kernels/quant/per_block_cast_lossless_asc.py`
- 上游测试：`tests/quant/test_per_block_cast_lossless.py`
- 输入合同：输入逻辑 FP4 e2m1 [num_tokens,hidden]，用 packed INT8 保存；输出 e4m3，scale block 见 case。
- 已有情况：库存无对应族
- 注意：上游参数组合候选；具体输入以对应测试构造器为准，合法性和数值正确性尚未在 hidev 逐例验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hidden":2048,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_tokens":512,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":false,"out_use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"hidden":768,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_tokens":8064,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":true,"out_use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"hidden":768,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_tokens":512,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":false,"out_use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"hidden":7168,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_tokens":8064,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":true,"out_use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"hidden":2304,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_tokens":512,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":true,"out_use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"hidden":2560,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_tokens":512,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":false,"out_use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"hidden":3072,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_tokens":8064,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":false,"out_use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"hidden":4096,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_tokens":512,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":false,"out_use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"hidden":6144,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_tokens":512,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":false,"out_use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"hidden":2048,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_tokens":8064,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":true,"out_use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"hidden":2304,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_tokens":8064,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":false,"out_use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"hidden":2560,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_tokens":8064,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":true,"out_use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"hidden":3072,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_tokens":512,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":true,"out_use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"hidden":4096,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_tokens":8064,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":true,"out_use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"hidden":6144,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_tokens":8064,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":true,"out_use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"hidden":7168,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_tokens":512,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":false,"out_use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"hidden":2048,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_tokens":512,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":true,"out_use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"hidden":2048,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_tokens":8064,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":false,"out_use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"hidden":2048,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_tokens":8064,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":true,"out_use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"hidden":2048,"in_round_sf":true,"in_sf_block":[1,32],"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_tokens":512,"out_round_sf":true,"out_sf_block":[32,32],"out_use_packed_ue8m0":false,"out_use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |

## quant_per_channel_cast

- 实现：`tile_kernels/quant/per_channel_cast_asc.py`
- 上游测试：`tests/quant/test_per_channel_cast.py`
- 输入合同：输入逻辑 shape [num_tokens,hidden]、格式 in_dtype；输出 scale 的布局及粒度见 case。
- 已有情况：库存无对应族
- 注意：上游参数组合候选；具体输入以对应测试构造器为准，合法性和数值正确性尚未在 hidev 逐例验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"hidden":128,"in_dtype":"bf16","in_round_sf":false,"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_per_channels":null,"num_per_tokens":32,"num_tokens":512,"round_sf":false,"use_packed_ue8m0":false}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"hidden":768,"in_dtype":"e4m3","in_round_sf":true,"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"hidden":128,"in_dtype":"bf16","in_round_sf":false,"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_per_channels":null,"num_per_tokens":32,"num_tokens":512,"round_sf":true,"use_packed_ue8m0":true}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"hidden":7168,"in_dtype":"e4m3","in_round_sf":true,"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"hidden":2048,"in_dtype":"e4m3","in_round_sf":true,"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"hidden":2560,"in_dtype":"e4m3","in_round_sf":true,"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_per_channels":32,"num_per_tokens":32,"num_tokens":512,"round_sf":false,"use_packed_ue8m0":false}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"hidden":3072,"in_dtype":"bf16","in_round_sf":false,"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_per_channels":null,"num_per_tokens":32,"num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"hidden":384,"in_dtype":"e4m3","in_round_sf":false,"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_per_channels":32,"num_per_tokens":32,"num_tokens":512,"round_sf":false,"use_packed_ue8m0":false}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"hidden":4096,"in_dtype":"bf16","in_round_sf":false,"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_per_channels":null,"num_per_tokens":32,"num_tokens":512,"round_sf":false,"use_packed_ue8m0":false}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"hidden":6144,"in_dtype":"bf16","in_round_sf":false,"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_per_channels":null,"num_per_tokens":32,"num_tokens":512,"round_sf":false,"use_packed_ue8m0":false}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"hidden":2560,"in_dtype":"bf16","in_round_sf":false,"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_per_channels":null,"num_per_tokens":32,"num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"hidden":3072,"in_dtype":"e4m3","in_round_sf":true,"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_per_channels":32,"num_per_tokens":32,"num_tokens":512,"round_sf":true,"use_packed_ue8m0":true}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"hidden":4096,"in_dtype":"e4m3","in_round_sf":true,"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"hidden":6144,"in_dtype":"e4m3","in_round_sf":true,"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"hidden":7168,"in_dtype":"bf16","in_round_sf":false,"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_per_channels":null,"num_per_tokens":32,"num_tokens":512,"round_sf":false,"use_packed_ue8m0":false}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"hidden":768,"in_dtype":"bf16","in_round_sf":false,"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_per_channels":null,"num_per_tokens":32,"num_tokens":512,"round_sf":false,"use_packed_ue8m0":false}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"hidden":128,"in_dtype":"e4m3","in_round_sf":true,"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"hidden":2048,"in_dtype":"bf16","in_round_sf":false,"in_use_packed_ue8m0":false,"in_use_tma_aligned_col_major_sf":false,"num_per_channels":null,"num_per_tokens":32,"num_tokens":512,"round_sf":true,"use_packed_ue8m0":true}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"hidden":384,"in_dtype":"e4m3","in_round_sf":true,"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_per_channels":32,"num_per_tokens":32,"num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"hidden":2048,"in_dtype":"e4m3","in_round_sf":true,"in_use_packed_ue8m0":true,"in_use_tma_aligned_col_major_sf":true,"num_per_channels":32,"num_per_tokens":32,"num_tokens":512,"round_sf":false,"use_packed_ue8m0":false}` | 上游测试参数 | 待核/未命中 |

## quant_per_token_cast

- 实现：`tile_kernels/quant/per_token_cast_asc.py`
- 上游测试：`tests/quant/test_per_token_cast.py`
- 输入合同：输入逻辑 shape [num_tokens,hidden]、格式 in_dtype；输出格式 fmt，scale 与 block 属性见 case。
- 已有情况：库存无对应族
- 注意：上游参数组合候选；具体输入以对应测试构造器为准，合法性和数值正确性尚未在 hidev 逐例验证。 上游 Ascend 测试明确跳过 stochastic rounding，本清单不含该路径。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"fmt":"e4m3","hidden":768,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"fmt":"e4m3","hidden":7168,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"fmt":"e2m1","hidden":2048,"in_dtype":"e2m1","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":false,"x_block_size":[32,32]}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"fmt":"e4m3","hidden":2560,"in_dtype":"e4m3","num_per_channels":32,"num_tokens":8001,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":[32,32]}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"fmt":"e2m1","hidden":3072,"in_dtype":"e2m1","num_per_channels":32,"num_tokens":8001,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":true,"x_block_size":[32,32]}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"fmt":"e2m1","hidden":384,"in_dtype":"e4m3","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":true,"x_block_size":[32,32]}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"fmt":"e2m1","hidden":4096,"in_dtype":"fp32","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"fmt":"e4m3","hidden":6144,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"fmt":"e4m3","hidden":2048,"in_dtype":"bf16","num_per_channels":32,"num_tokens":8001,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"fmt":"e4m3","hidden":4096,"in_dtype":"e2m1","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"x_block_size":[32,32]}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"fmt":"e2m1","hidden":2560,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"fmt":"e2m1","hidden":6144,"in_dtype":"e2m1","num_per_channels":32,"num_tokens":8001,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":true,"x_block_size":[32,32]}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"fmt":"e2m1","hidden":7168,"in_dtype":"e2m1","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":[32,32]}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"fmt":"e2m1","hidden":768,"in_dtype":"e2m1","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":[32,32]}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"fmt":"e4m3","hidden":128,"in_dtype":"e4m3","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":false,"x_block_size":[32,32]}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"fmt":"e4m3","hidden":3072,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"fmt":"e4m3","hidden":384,"in_dtype":"bf16","num_per_channels":32,"num_tokens":8001,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"fmt":"e2m1","hidden":384,"in_dtype":"e2m1","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":false,"x_block_size":[32,32]}` | 上游测试参数 | 待核/未命中 |

## quant_per_token_cast_and_cast_back

- 实现：`tile_kernels/quant/per_token_cast_and_cast_back_asc.py`
- 上游测试：`tests/quant/test_per_token_cast_and_cast_back.py`
- 输入合同：输入 dtype=in_dtype [num_tokens,hidden]，内部格式 fmt；输出与输入 dtype 相同。
- 已有情况：库存无对应族
- 注意：上游参数组合候选；具体输入以对应测试构造器为准，合法性和数值正确性尚未在 hidev 逐例验证。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_per_channels":16,"num_tokens":512,"round_sf":false,"use_e4m3_sf":true}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"fmt":"e4m3","hidden":768,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_per_channels":16,"num_tokens":8001,"round_sf":false,"use_e4m3_sf":true}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"fmt":"e4m3","hidden":7168,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"fmt":"e2m1","hidden":2048,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"fmt":"e4m3","hidden":2560,"in_dtype":"fp32","num_per_channels":16,"num_tokens":512,"round_sf":false,"use_e4m3_sf":true}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"fmt":"e2m1","hidden":3072,"in_dtype":"fp32","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"fmt":"e4m3","hidden":384,"in_dtype":"bf16","num_per_channels":16,"num_tokens":512,"round_sf":false,"use_e4m3_sf":true}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"fmt":"e2m1","hidden":4096,"in_dtype":"bf16","num_per_channels":16,"num_tokens":512,"round_sf":false,"use_e4m3_sf":true}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"fmt":"e2m1","hidden":6144,"in_dtype":"bf16","num_per_channels":16,"num_tokens":512,"round_sf":false,"use_e4m3_sf":true}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"fmt":"e2m1","hidden":2560,"in_dtype":"bf16","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"fmt":"e2m1","hidden":384,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"fmt":"e2m1","hidden":7168,"in_dtype":"bf16","num_per_channels":16,"num_tokens":512,"round_sf":false,"use_e4m3_sf":true}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"fmt":"e2m1","hidden":768,"in_dtype":"bf16","num_per_channels":16,"num_tokens":512,"round_sf":false,"use_e4m3_sf":true}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"fmt":"e4m3","hidden":2048,"in_dtype":"fp32","num_per_channels":16,"num_tokens":8001,"round_sf":false,"use_e4m3_sf":true}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"fmt":"e4m3","hidden":4096,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"fmt":"e4m3","hidden":6144,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"fmt":"e4m3","hidden":128,"in_dtype":"fp32","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"fmt":"e4m3","hidden":3072,"in_dtype":"bf16","num_per_channels":16,"num_tokens":8001,"round_sf":false,"use_e4m3_sf":true}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"fmt":"e2m1","hidden":3072,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false}` | 上游测试参数 | 待核/未命中 |

## quant_swiglu_forward

- 实现：`tile_kernels/quant/swiglu_forward_asc.py`
- 上游测试：`tests/quant/test_swiglu_forward.py`
- 输入合同：x BF16 [num_tokens,2*hidden]；输出格式 fmt；可选 topk_weights FP32 [num_tokens]；num_experts=4 时 prefix INT32 为 [N/4,N/2,3N/4,N]，N=num_tokens。
- 已有情况：SwiGLU 已有 19 个 case
- 注意：为固定真实输入 shape，按公开 API 构造明确的 token 数和等分 expert 前缀；全部标为扩展，尚未设备验证。该组不等同于上游随机路由数据；BF16/FP32/FP8 路径分别核对正确性。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"alignment":1,"clamp_value":0.5,"fmt":"bf16","hidden":128,"num_experts":0,"num_per_channels":null,"num_tokens":128,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 02 | `{"alignment":256,"clamp_value":null,"fmt":"fp32","hidden":768,"num_experts":4,"num_per_channels":null,"num_tokens":8192,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 03 | `{"alignment":1,"clamp_value":0.5,"fmt":"bf16","hidden":128,"num_experts":0,"num_per_channels":null,"num_tokens":1024,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 04 | `{"alignment":256,"clamp_value":null,"fmt":"fp32","hidden":3584,"num_experts":4,"num_per_channels":null,"num_tokens":8192,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 05 | `{"alignment":1,"clamp_value":0.5,"fmt":"bf16","hidden":128,"num_experts":0,"num_per_channels":null,"num_tokens":1024,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 06 | `{"alignment":256,"clamp_value":null,"fmt":"fp32","hidden":768,"num_experts":4,"num_per_channels":null,"num_tokens":8192,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 07 | `{"alignment":1,"clamp_value":null,"fmt":"e4m3","hidden":2048,"num_experts":0,"num_per_channels":32,"num_tokens":4096,"round_sf":true,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 08 | `{"alignment":256,"clamp_value":0.5,"fmt":"e4m3","hidden":128,"num_experts":4,"num_per_channels":32,"num_tokens":4096,"round_sf":true,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 09 | `{"alignment":1,"clamp_value":0.5,"fmt":"fp32","hidden":2048,"num_experts":0,"num_per_channels":null,"num_tokens":512,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 10 | `{"alignment":1,"clamp_value":0.5,"fmt":"e4m3","hidden":3584,"num_experts":0,"num_per_channels":32,"num_tokens":512,"round_sf":true,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 11 | `{"alignment":1,"clamp_value":0.5,"fmt":"e4m3","hidden":768,"num_experts":0,"num_per_channels":32,"num_tokens":128,"round_sf":true,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 12 | `{"alignment":256,"clamp_value":null,"fmt":"bf16","hidden":2048,"num_experts":4,"num_per_channels":null,"num_tokens":1024,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 13 | `{"alignment":1,"clamp_value":0.5,"fmt":"e4m3","hidden":128,"num_experts":0,"num_per_channels":32,"num_tokens":8192,"round_sf":true,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 14 | `{"alignment":1,"clamp_value":0.5,"fmt":"bf16","hidden":3584,"num_experts":0,"num_per_channels":null,"num_tokens":4096,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 15 | `{"alignment":1,"clamp_value":0.5,"fmt":"e4m3","hidden":3584,"num_experts":0,"num_per_channels":32,"num_tokens":1024,"round_sf":true,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 16 | `{"alignment":1,"clamp_value":null,"fmt":"bf16","hidden":128,"num_experts":0,"num_per_channels":null,"num_tokens":512,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 17 | `{"alignment":1,"clamp_value":null,"fmt":"fp32","hidden":128,"num_experts":0,"num_per_channels":null,"num_tokens":128,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 18 | `{"alignment":1,"clamp_value":0.5,"fmt":"bf16","hidden":2048,"num_experts":0,"num_per_channels":null,"num_tokens":8192,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 19 | `{"alignment":1,"clamp_value":0.5,"fmt":"bf16","hidden":768,"num_experts":0,"num_per_channels":null,"num_tokens":1024,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 20 | `{"alignment":1,"clamp_value":0.5,"fmt":"fp32","hidden":768,"num_experts":0,"num_per_channels":null,"num_tokens":4096,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |

## quant_swiglu_backward

- 实现：`tile_kernels/quant/swiglu_backward_asc.py`
- 上游测试：`tests/quant/test_swiglu_backward.py`
- 输入合同：x 逻辑 shape [num_tokens,2*hidden]，梯度 [num_tokens,hidden]；fmt=e4m3 时 x 为 FP8，其余情况 x dtype=fmt；可选 topk_weights FP32 [num_tokens]；num_experts=4 时 prefix INT32 为 [N/4,N/2,3N/4,N]，N=num_tokens。
- 已有情况：库存无对应族
- 注意：为固定真实输入 shape，按公开 API 构造明确的 token 数和等分 expert 前缀；全部标为扩展，尚未设备验证。该组不等同于上游随机路由数据；BF16/FP32/FP8 路径分别核对正确性。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"alignment":1,"clamp_value":0.5,"do_recompute":false,"fmt":"bf16","hidden":128,"num_experts":0,"num_per_channels":null,"num_tokens":128,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 02 | `{"alignment":256,"clamp_value":null,"do_recompute":true,"fmt":"fp32","hidden":768,"num_experts":4,"num_per_channels":null,"num_tokens":8192,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 03 | `{"alignment":1,"clamp_value":0.5,"do_recompute":false,"fmt":"bf16","hidden":128,"num_experts":0,"num_per_channels":null,"num_tokens":1024,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 04 | `{"alignment":256,"clamp_value":null,"do_recompute":true,"fmt":"fp32","hidden":3584,"num_experts":4,"num_per_channels":null,"num_tokens":8192,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 05 | `{"alignment":1,"clamp_value":0.5,"do_recompute":false,"fmt":"bf16","hidden":128,"num_experts":0,"num_per_channels":null,"num_tokens":4096,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 06 | `{"alignment":256,"clamp_value":null,"do_recompute":true,"fmt":"fp32","hidden":768,"num_experts":4,"num_per_channels":null,"num_tokens":4096,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 07 | `{"alignment":1,"clamp_value":0.5,"do_recompute":true,"fmt":"e4m3","hidden":2048,"num_experts":0,"num_per_channels":32,"num_tokens":512,"round_sf":true,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 08 | `{"alignment":256,"clamp_value":null,"do_recompute":false,"fmt":"e4m3","hidden":128,"num_experts":4,"num_per_channels":32,"num_tokens":8192,"round_sf":true,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 09 | `{"alignment":1,"clamp_value":null,"do_recompute":false,"fmt":"fp32","hidden":2048,"num_experts":0,"num_per_channels":null,"num_tokens":512,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 10 | `{"alignment":256,"clamp_value":0.5,"do_recompute":true,"fmt":"bf16","hidden":2048,"num_experts":4,"num_per_channels":null,"num_tokens":1024,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 11 | `{"alignment":1,"clamp_value":0.5,"do_recompute":false,"fmt":"e4m3","hidden":3584,"num_experts":0,"num_per_channels":32,"num_tokens":1024,"round_sf":true,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 12 | `{"alignment":1,"clamp_value":0.5,"do_recompute":false,"fmt":"e4m3","hidden":768,"num_experts":0,"num_per_channels":32,"num_tokens":128,"round_sf":true,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 13 | `{"alignment":1,"clamp_value":0.5,"do_recompute":true,"fmt":"fp32","hidden":128,"num_experts":0,"num_per_channels":null,"num_tokens":128,"round_sf":false,"routed_scaling_factor":2.5,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":true}` | 扩展 | 待核/未命中 |
| 14 | `{"alignment":1,"clamp_value":0.5,"do_recompute":false,"fmt":"bf16","hidden":2048,"num_experts":0,"num_per_channels":null,"num_tokens":8192,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 15 | `{"alignment":1,"clamp_value":0.5,"do_recompute":false,"fmt":"e4m3","hidden":2048,"num_experts":0,"num_per_channels":32,"num_tokens":4096,"round_sf":true,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 16 | `{"alignment":1,"clamp_value":null,"do_recompute":false,"fmt":"bf16","hidden":3584,"num_experts":0,"num_per_channels":null,"num_tokens":128,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 17 | `{"alignment":1,"clamp_value":0.5,"do_recompute":false,"fmt":"bf16","hidden":768,"num_experts":0,"num_per_channels":null,"num_tokens":512,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 18 | `{"alignment":1,"clamp_value":null,"do_recompute":false,"fmt":"fp32","hidden":768,"num_experts":0,"num_per_channels":null,"num_tokens":1024,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 19 | `{"alignment":1,"clamp_value":0.5,"do_recompute":false,"fmt":"bf16","hidden":128,"num_experts":0,"num_per_channels":null,"num_tokens":512,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |
| 20 | `{"alignment":1,"clamp_value":0.5,"do_recompute":false,"fmt":"bf16","hidden":2048,"num_experts":0,"num_per_channels":null,"num_tokens":128,"round_sf":false,"routed_scaling_factor":null,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"with_weights":false}` | 扩展 | 待核/未命中 |

## quant_per_token_cast_with_sf_only

- 实现：`tile_kernels/quant/per_token_cast_asc.py`
- 上游测试：`tests/quant/test_per_token_cast.py`
- 输入合同：x dtype=in_dtype [num_tokens,hidden]；fmt 和 scale 粒度见参数。该入口只计算 scale。
- 已有情况：库存无对应族
- 注意：上游正确性测试包含该模式；必须单独圈定其设备 kernel，不能把同一测试中其它调用混入。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"fmt":"e4m3","hidden":768,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"fmt":"e4m3","hidden":7168,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"fmt":"e2m1","hidden":2048,"in_dtype":"bf16","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"fmt":"e4m3","hidden":2560,"in_dtype":"fp32","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"fmt":"e2m1","hidden":3072,"in_dtype":"fp32","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"fmt":"e4m3","hidden":384,"in_dtype":"bf16","num_per_channels":32,"num_tokens":8001,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"fmt":"e2m1","hidden":4096,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"fmt":"e2m1","hidden":6144,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"fmt":"e2m1","hidden":2560,"in_dtype":"bf16","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"fmt":"e2m1","hidden":384,"in_dtype":"fp32","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"fmt":"e2m1","hidden":7168,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"fmt":"e2m1","hidden":768,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"fmt":"e4m3","hidden":2048,"in_dtype":"fp32","num_per_channels":32,"num_tokens":512,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"fmt":"e4m3","hidden":4096,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"fmt":"e4m3","hidden":6144,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"fmt":"e4m3","hidden":128,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"fmt":"e4m3","hidden":3072,"in_dtype":"bf16","num_per_channels":32,"num_tokens":8001,"round_sf":false,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":true,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"fmt":"e2m1","hidden":3072,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |

## quant_per_token_cast_with_precomputed_sf

- 实现：`tile_kernels/quant/per_token_cast_asc.py`
- 上游测试：`tests/quant/test_per_token_cast.py`
- 输入合同：x dtype=in_dtype [num_tokens,hidden]；fmt 和 scale 粒度见参数。该入口额外接收上游算出的 scale，且要求非 TMA、非 packed 布局。
- 已有情况：库存无对应族
- 注意：上游正确性测试包含该模式；必须单独圈定其设备 kernel，不能把同一测试中其它调用混入。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"fmt":"e4m3","hidden":768,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"fmt":"e4m3","hidden":7168,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"fmt":"e2m1","hidden":2048,"in_dtype":"fp32","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"fmt":"e4m3","hidden":2560,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"fmt":"e2m1","hidden":3072,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"fmt":"e2m1","hidden":384,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"fmt":"e2m1","hidden":4096,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"fmt":"e2m1","hidden":6144,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"fmt":"e2m1","hidden":2560,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"fmt":"e2m1","hidden":7168,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"fmt":"e2m1","hidden":768,"in_dtype":"bf16","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"fmt":"e4m3","hidden":2048,"in_dtype":"bf16","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"fmt":"e4m3","hidden":3072,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"fmt":"e4m3","hidden":384,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"fmt":"e4m3","hidden":4096,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"fmt":"e4m3","hidden":6144,"in_dtype":"fp32","num_per_channels":32,"num_tokens":8001,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"fmt":"e4m3","hidden":128,"in_dtype":"fp32","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"fmt":"e2m1","hidden":128,"in_dtype":"fp32","num_per_channels":32,"num_tokens":512,"round_sf":true,"use_e4m3_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false,"x_block_size":null}` | 上游测试参数 | 待核/未命中 |

## quant_per_block_cast_with_sf_only

- 实现：`tile_kernels/quant/per_block_cast_asc.py`
- 上游测试：`tests/quant/test_per_block_cast.py`
- 输入合同：x dtype=in_dtype [num_tokens,hidden]；fmt 和 scale 粒度见参数。该入口只计算 scale。
- 已有情况：库存无对应族
- 注意：上游正确性测试包含该模式；必须单独圈定其设备 kernel，不能把同一测试中其它调用混入。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"block_size":[32,32],"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"block_size":[32,32],"fmt":"e4m3","hidden":768,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"block_size":[32,32],"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_tokens":512,"round_sf":true,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"block_size":[32,32],"fmt":"e4m3","hidden":7168,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"block_size":[32,32],"fmt":"e4m3","hidden":2048,"in_dtype":"fp32","num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"block_size":[32,32],"fmt":"e2m1","hidden":2560,"in_dtype":"bf16","num_tokens":512,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"block_size":[32,32],"fmt":"e2m1","hidden":3072,"in_dtype":"bf16","num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"block_size":[32,32],"fmt":"e2m1","hidden":384,"in_dtype":"fp32","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"block_size":[32,32],"fmt":"e4m3","hidden":4096,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"block_size":[32,32],"fmt":"e2m1","hidden":6144,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"block_size":[32,32],"fmt":"e2m1","hidden":2048,"in_dtype":"bf16","num_tokens":512,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"block_size":[32,32],"fmt":"e2m1","hidden":4096,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"block_size":[32,32],"fmt":"e2m1","hidden":7168,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"block_size":[32,32],"fmt":"e2m1","hidden":768,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"block_size":[32,32],"fmt":"e4m3","hidden":2560,"in_dtype":"fp32","num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"block_size":[32,32],"fmt":"e4m3","hidden":3072,"in_dtype":"fp32","num_tokens":512,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"block_size":[32,32],"fmt":"e4m3","hidden":384,"in_dtype":"bf16","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"block_size":[32,32],"fmt":"e4m3","hidden":6144,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"block_size":[32,32],"fmt":"e4m3","hidden":128,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"block_size":[32,32],"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_tokens":512,"round_sf":true,"use_packed_ue8m0":true,"use_tma_aligned_col_major_sf":true}` | 上游测试参数 | 待核/未命中 |

## quant_per_block_cast_with_precomputed_sf

- 实现：`tile_kernels/quant/per_block_cast_asc.py`
- 上游测试：`tests/quant/test_per_block_cast.py`
- 输入合同：x dtype=in_dtype [num_tokens,hidden]；fmt 和 scale 粒度见参数。该入口额外接收上游算出的 scale，且要求非 TMA、非 packed 布局。
- 已有情况：库存无对应族
- 注意：上游正确性测试包含该模式；必须单独圈定其设备 kernel，不能把同一测试中其它调用混入。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"block_size":[32,32],"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"block_size":[32,32],"fmt":"e4m3","hidden":768,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"block_size":[32,32],"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_tokens":512,"round_sf":true,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"block_size":[32,32],"fmt":"e4m3","hidden":7168,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"block_size":[32,32],"fmt":"e2m1","hidden":2048,"in_dtype":"fp32","num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"block_size":[32,32],"fmt":"e4m3","hidden":2560,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"block_size":[32,32],"fmt":"e2m1","hidden":3072,"in_dtype":"bf16","num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"block_size":[32,32],"fmt":"e2m1","hidden":384,"in_dtype":"fp32","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"block_size":[32,32],"fmt":"e2m1","hidden":4096,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"block_size":[32,32],"fmt":"e2m1","hidden":6144,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"block_size":[32,32],"fmt":"e2m1","hidden":2560,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"block_size":[32,32],"fmt":"e2m1","hidden":7168,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"block_size":[32,32],"fmt":"e2m1","hidden":768,"in_dtype":"bf16","num_tokens":512,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"block_size":[32,32],"fmt":"e4m3","hidden":2048,"in_dtype":"bf16","num_tokens":512,"round_sf":true,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"block_size":[32,32],"fmt":"e4m3","hidden":3072,"in_dtype":"fp32","num_tokens":512,"round_sf":true,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"block_size":[32,32],"fmt":"e4m3","hidden":384,"in_dtype":"bf16","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"block_size":[32,32],"fmt":"e4m3","hidden":4096,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"block_size":[32,32],"fmt":"e4m3","hidden":6144,"in_dtype":"fp32","num_tokens":8064,"round_sf":true,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"block_size":[32,32],"fmt":"e4m3","hidden":128,"in_dtype":"fp32","num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"block_size":[32,32],"fmt":"e2m1","hidden":128,"in_dtype":"bf16","num_tokens":8064,"round_sf":false,"use_packed_ue8m0":false,"use_tma_aligned_col_major_sf":false}` | 上游测试参数 | 待核/未命中 |

## quant_batched_transpose_weight_sf

- 实现：`tile_kernels/quant/batched_transpose_weight_sf_asc.py`
- 上游测试：`tests/quant/test_batched_transpose_weight_sf.py`
- 输入合同：输入为每个 (n,k,num_groups,transpose_sf1) 配置生成的 FP32 scale，shape 为 [n/32,k/32] 或 [num_groups,n/32,k/32]。
- 已有情况：库存无对应族
- 注意：原上游 case 是 7 个权重一起运行；扩展 case 每次是新的单权重调用。block=128 在 Ascend 不支持。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"block_size":32,"weight_configs":[[128,128,2,false]]}` | 扩展 | 待核/未命中 |
| 02 | `{"block_size":32,"weight_configs":[[128,128,2,true]]}` | 扩展 | 待核/未命中 |
| 03 | `{"block_size":32,"weight_configs":[[128,128,null,false],[384,512,2,true],[768,1152,3,false],[640,1280,1,true],[2048,2560,2,false],[384,384,null,true],[6144,4096,null,false]]}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"block_size":32,"weight_configs":[[128,128,null,false]]}` | 扩展 | 待核/未命中 |
| 05 | `{"block_size":32,"weight_configs":[[128,128,null,true]]}` | 扩展 | 待核/未命中 |
| 06 | `{"block_size":32,"weight_configs":[[2048,2560,2,false]]}` | 扩展 | 待核/未命中 |
| 07 | `{"block_size":32,"weight_configs":[[2048,2560,2,true]]}` | 扩展 | 待核/未命中 |
| 08 | `{"block_size":32,"weight_configs":[[2048,2560,null,false]]}` | 扩展 | 待核/未命中 |
| 09 | `{"block_size":32,"weight_configs":[[2048,2560,null,true]]}` | 扩展 | 待核/未命中 |
| 10 | `{"block_size":32,"weight_configs":[[384,1152,2,false]]}` | 扩展 | 待核/未命中 |
| 11 | `{"block_size":32,"weight_configs":[[384,1152,2,true]]}` | 扩展 | 待核/未命中 |
| 12 | `{"block_size":32,"weight_configs":[[384,1152,null,false]]}` | 扩展 | 待核/未命中 |
| 13 | `{"block_size":32,"weight_configs":[[384,1152,null,true]]}` | 扩展 | 待核/未命中 |
| 14 | `{"block_size":32,"weight_configs":[[512,768,2,false]]}` | 扩展 | 待核/未命中 |
| 15 | `{"block_size":32,"weight_configs":[[512,768,2,true]]}` | 扩展 | 待核/未命中 |
| 16 | `{"block_size":32,"weight_configs":[[512,768,null,false]]}` | 扩展 | 待核/未命中 |
| 17 | `{"block_size":32,"weight_configs":[[512,768,null,true]]}` | 扩展 | 待核/未命中 |
| 18 | `{"block_size":32,"weight_configs":[[6144,4096,2,false]]}` | 扩展 | 待核/未命中 |
| 19 | `{"block_size":32,"weight_configs":[[6144,4096,2,true]]}` | 扩展 | 待核/未命中 |
| 20 | `{"block_size":32,"weight_configs":[[6144,4096,null,false]]}` | 扩展 | 待核/未命中 |

## randn

- 实现：`tile_kernels/rand/randn_asc.py`
- 上游测试：`tests/rand/test_randn.py`
- 输入合同：输出 shape 和 dtype 见 case；seed=42。
- 已有情况：库存无对应族
- 注意：扩展项补充小尺寸，分布检查与固定种子可重复性都需验证；上游另有超大 shape，不在本批。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"dtype":"bf16","shape":[1]}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"dtype":"fp32","shape":[16385]}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"dtype":"bf16","shape":[1024,1024]}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"dtype":"bf16","shape":[1024]}` | 扩展 | 待核/未命中 |
| 05 | `{"dtype":"bf16","shape":[127,129]}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"dtype":"bf16","shape":[128]}` | 扩展 | 待核/未命中 |
| 07 | `{"dtype":"bf16","shape":[16383]}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"dtype":"bf16","shape":[16384]}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"dtype":"bf16","shape":[4096,4096]}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"dtype":"bf16","shape":[64]}` | 扩展 | 待核/未命中 |
| 11 | `{"dtype":"bf16","shape":[7,11,13]}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"dtype":"bf16","shape":[16385]}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"dtype":"fp32","shape":[1024,1024]}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"dtype":"fp32","shape":[1024]}` | 扩展 | 待核/未命中 |
| 15 | `{"dtype":"fp32","shape":[127,129]}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"dtype":"fp32","shape":[128]}` | 扩展 | 待核/未命中 |
| 17 | `{"dtype":"fp32","shape":[16383]}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"dtype":"fp32","shape":[16384]}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"dtype":"fp32","shape":[1]}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"dtype":"fp32","shape":[4096,4096]}` | 上游测试参数 | 待核/未命中 |

## rotary_embedding

- 实现：`tile_kernels/transform/rope_asc.py`
- 上游测试：`tests/transform/test_rope.py`
- 输入合同：query/key 各 [seqlen,nheads,dim]、dtype=dtype；cos_sin FP32 [seqlen_total,dim]，positions INT32 [seqlen]。
- 已有情况：已有 20 个 case（Q/K 分别采集）
- 注意：本批还需记录 head_split 对实际 stride 的影响；此处列上游 3D 测试组合，旧库存部分为 4D。

| 编号 | 具体 case 参数 | 来源 | 历史主输入可能重合 |
|---:|---|---|---|
| 01 | `{"conjugate":false,"dim":128,"dtype":"bf16","head_split":false,"interleaved":false,"nheads":1,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 02 | `{"conjugate":true,"dim":64,"dtype":"fp32","head_split":true,"interleaved":true,"nheads":128,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 03 | `{"conjugate":false,"dim":128,"dtype":"bf16","head_split":true,"interleaved":true,"nheads":32,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 04 | `{"conjugate":false,"dim":64,"dtype":"fp32","head_split":false,"interleaved":false,"nheads":5,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 05 | `{"conjugate":true,"dim":128,"dtype":"bf16","head_split":false,"interleaved":false,"nheads":128,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 06 | `{"conjugate":true,"dim":128,"dtype":"bf16","head_split":false,"interleaved":true,"nheads":5,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 07 | `{"conjugate":true,"dim":128,"dtype":"fp32","head_split":false,"interleaved":false,"nheads":32,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 08 | `{"conjugate":true,"dim":64,"dtype":"bf16","head_split":true,"interleaved":false,"nheads":1,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 09 | `{"conjugate":false,"dim":128,"dtype":"fp32","head_split":false,"interleaved":true,"nheads":1,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 10 | `{"conjugate":false,"dim":128,"dtype":"bf16","head_split":false,"interleaved":false,"nheads":128,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 11 | `{"conjugate":false,"dim":128,"dtype":"bf16","head_split":true,"interleaved":false,"nheads":5,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 12 | `{"conjugate":false,"dim":64,"dtype":"bf16","head_split":false,"interleaved":false,"nheads":32,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 13 | `{"conjugate":false,"dim":128,"dtype":"bf16","head_split":false,"interleaved":false,"nheads":32,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 14 | `{"conjugate":false,"dim":128,"dtype":"bf16","head_split":false,"interleaved":false,"nheads":5,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 15 | `{"conjugate":false,"dim":128,"dtype":"bf16","head_split":false,"interleaved":true,"nheads":1,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 16 | `{"conjugate":false,"dim":128,"dtype":"bf16","head_split":false,"interleaved":true,"nheads":128,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 17 | `{"conjugate":false,"dim":128,"dtype":"bf16","head_split":false,"interleaved":true,"nheads":32,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 18 | `{"conjugate":false,"dim":128,"dtype":"bf16","head_split":false,"interleaved":true,"nheads":5,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 19 | `{"conjugate":false,"dim":128,"dtype":"bf16","head_split":true,"interleaved":false,"nheads":1,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |
| 20 | `{"conjugate":false,"dim":128,"dtype":"bf16","head_split":true,"interleaved":false,"nheads":128,"seqlen":2001,"seqlen_total":8192}` | 上游测试参数 | 待核/未命中 |

## 历史 case 完整索引

以下是旧库存的 99 个登记 ID，对应 97 个不同任务定义。这里列出完整 shape/dtype/attrs，用于逐项对照；旧 Sinkhorn 等历史口径不能直接当成本次正式同口径结果。

| 历史 ID | 族 | 完整任务定义 | 已登记采集口径 |
|---|---|---|---|
| `castback-n1-h128-bf16` | `quant_cast_back` | `{"attrs":{"hidden":128,"output_dtype":"bfloat16","tokens":1},"input_dtypes":["float8_e4m3fn","float32"],"input_shapes":[[1,128],[1,4]],"output_dtypes":["bfloat16"],"output_shapes":[[1,128]],"task":"quant_cast_back"}` | warmup5_single_kernel |
| `castback-n512-h2048-bf16` | `quant_cast_back` | `{"attrs":{"hidden":2048,"output_dtype":"bfloat16","tokens":512},"input_dtypes":["float8_e4m3fn","float32"],"input_shapes":[[512,2048],[512,64]],"output_dtypes":["bfloat16"],"output_shapes":[[512,2048]],"task":"quant_cast_back"}` | warmup5_single_kernel |
| `castback-n512-h2048-fp32` | `quant_cast_back` | `{"attrs":{"hidden":2048,"output_dtype":"float32","tokens":512},"input_dtypes":["float8_e4m3fn","float32"],"input_shapes":[[512,2048],[512,64]],"output_dtypes":["float32"],"output_shapes":[[512,2048]],"task":"quant_cast_back"}` | warmup5_single_kernel |
| `castback-n8001-h2048-fp32` | `quant_cast_back` | `{"attrs":{"hidden":2048,"output_dtype":"float32","tokens":8001},"input_dtypes":["float8_e4m3fn","float32"],"input_shapes":[[8001,2048],[8001,64]],"output_dtypes":["float32"],"output_shapes":[[8001,2048]],"task":"quant_cast_back"}` | warmup5_single_kernel |
| `fused-h2048` | `engram_fused_weight` | `{"attrs":{"hidden":2048},"input_dtypes":["bfloat16","bfloat16"],"input_shapes":[[4,2048],[4,2048]],"output_dtypes":["float32"],"output_shapes":[[4,2048]],"task":"engram_fused_weight"}` | warmup5_single_kernel |
| `fused-h3584` | `engram_fused_weight` | `{"attrs":{"hidden":3584},"input_dtypes":["bfloat16","bfloat16"],"input_shapes":[[4,3584],[4,3584]],"output_dtypes":["float32"],"output_shapes":[[4,3584]],"task":"engram_fused_weight"}` | warmup5_single_kernel |
| `fused-h4096` | `engram_fused_weight` | `{"attrs":{"hidden":4096},"input_dtypes":["bfloat16","bfloat16"],"input_shapes":[[4,4096],[4,4096]],"output_dtypes":["float32"],"output_shapes":[[4,4096]],"task":"engram_fused_weight"}` | warmup5_single_kernel |
| `fused-h7168` | `engram_fused_weight` | `{"attrs":{"hidden":7168},"input_dtypes":["bfloat16","bfloat16"],"input_shapes":[[4,7168],[4,7168]],"output_dtypes":["float32"],"output_shapes":[[4,7168]],"task":"engram_fused_weight"}` | warmup5_single_kernel |
| `fused-h768` | `engram_fused_weight` | `{"attrs":{"hidden":768},"input_dtypes":["bfloat16","bfloat16"],"input_shapes":[[4,768],[4,768]],"output_dtypes":["float32"],"output_shapes":[[4,768]],"task":"engram_fused_weight"}` | warmup5_single_kernel |
| `hash-n1-g3` | `engram_hash` | `{"attrs":{"mask":false,"ngram":3,"tokens":1},"input_dtypes":["int32","int64","int32","int32",null],"input_shapes":[[1,3],[2,3],[2,2,8],[2,16],null],"output_dtypes":["int32"],"output_shapes":[[2,1,16]],"task":"engram_hash"}` | warmup5_single_kernel |
| `hash-n512-g3` | `engram_hash` | `{"attrs":{"mask":false,"ngram":3,"tokens":512},"input_dtypes":["int32","int64","int32","int32",null],"input_shapes":[[512,3],[2,3],[2,2,8],[2,16],null],"output_dtypes":["int32"],"output_shapes":[[2,512,16]],"task":"engram_hash"}` | warmup5_single_kernel |
| `hash-n512-g4-mask` | `engram_hash` | `{"attrs":{"mask":true,"ngram":4,"tokens":512},"input_dtypes":["int32","int64","int32","int32","bool"],"input_shapes":[[512,4],[2,4],[2,3,8],[2,24],[512]],"output_dtypes":["int32"],"output_shapes":[[2,512,24]],"task":"engram_hash"}` | warmup5_single_kernel |
| `hash-n8001-g4` | `engram_hash` | `{"attrs":{"mask":false,"ngram":4,"tokens":8001},"input_dtypes":["int32","int64","int32","int32",null],"input_shapes":[[8001,4],[2,4],[2,3,8],[2,24],null],"output_dtypes":["int32"],"output_shapes":[[2,8001,24]],"task":"engram_hash"}` | warmup5_single_kernel |
| `head-fp32-1001` | `mhc_head` | `{"attrs":{"mhc_pre_eps":0.01},"input_dtypes":["float32","float32","float32"],"input_shapes":[[1001,4],[1],[4]],"output_dtypes":["float32"],"output_shapes":[[1001,4]],"task":"mhc_head"}` | warmup5_single_kernel |
| `head-fp32-1024` | `mhc_head` | `{"attrs":{"mhc_pre_eps":0.01},"input_dtypes":["float32","float32","float32"],"input_shapes":[[1024,4],[1],[4]],"output_dtypes":["float32"],"output_shapes":[[1024,4]],"task":"mhc_head"}` | warmup5_single_kernel |
| `mhc-expand-fwd-bf16-n512-h4096-m4` | `mhc_expand_fwd` | `{"attrs":{"h_blk":2048,"mhc_mult":4,"num_stages":7},"input_dtypes":["bfloat16"],"input_shapes":[[512,4096]],"output_dtypes":["bfloat16"],"output_shapes":[[512,4,4096]],"task":"mhc_expand_fwd"}` | warmup5_single_kernel |
| `mhc_post_bwd-cann-2` | `mhc_post_bwd` | `{"attrs":{},"input_dtypes":["bfloat16","bfloat16","float32","bfloat16","float32"],"input_shapes":[[1,1024,4,5120],[1,1024,4,5120],[1,1024,4,4],[1,1024,5120],[1,1024,4]],"output_dtypes":["bfloat16","float32","bfloat16","float32"],"output_shapes":[[1,1024,4,5120],[1,1024,4,4],[1,1024,5120],[1,1024,4]],"task":"mhc_post_bwd"}` | warmup0_reference |
| `mhc_post_bwd-cann-4` | `mhc_post_bwd` | `{"attrs":{},"input_dtypes":["bfloat16","bfloat16","float32","bfloat16","float32"],"input_shapes":[[1,2048,4,2560],[1,2048,4,2560],[1,2048,4,4],[1,2048,2560],[1,2048,4]],"output_dtypes":["bfloat16","float32","bfloat16","float32"],"output_shapes":[[1,2048,4,2560],[1,2048,4,4],[1,2048,2560],[1,2048,4]],"task":"mhc_post_bwd"}` | warmup0_reference |
| `mhc_post_bwd-cann-6` | `mhc_post_bwd` | `{"attrs":{},"input_dtypes":["bfloat16","bfloat16","float32","bfloat16","float32"],"input_shapes":[[1,64,4,384],[1,64,4,384],[1,64,4,4],[1,64,384],[1,64,4]],"output_dtypes":["bfloat16","float32","bfloat16","float32"],"output_shapes":[[1,64,4,384],[1,64,4,4],[1,64,384],[1,64,4]],"task":"mhc_post_bwd"}` | warmup0_reference |
| `mhc_post_bwd-supp-01` | `mhc_post_bwd` | `{"attrs":{},"input_dtypes":["bfloat16","bfloat16","float32","bfloat16","float32"],"input_shapes":[[1,1,4,64],[1,1,4,64],[1,1,4,4],[1,1,64],[1,1,4]],"output_dtypes":["bfloat16","float32","bfloat16","float32"],"output_shapes":[[1,1,4,64],[1,1,4,4],[1,1,64],[1,1,4]],"task":"mhc_post_bwd"}` | warmup0_reference |
| `mhc_post_bwd-supp-04` | `mhc_post_bwd` | `{"attrs":{},"input_dtypes":["bfloat16","bfloat16","float32","bfloat16","float32"],"input_shapes":[[1,128,4,512],[1,128,4,512],[1,128,4,4],[1,128,512],[1,128,4]],"output_dtypes":["bfloat16","float32","bfloat16","float32"],"output_shapes":[[1,128,4,512],[1,128,4,4],[1,128,512],[1,128,4]],"task":"mhc_post_bwd"}` | warmup0_reference |
| `mhc_post_bwd-supp-07` | `mhc_post_bwd` | `{"attrs":{},"input_dtypes":["bfloat16","bfloat16","float32","bfloat16","float32"],"input_shapes":[[1,4096,4,64],[1,4096,4,64],[1,4096,4,4],[1,4096,64],[1,4096,4]],"output_dtypes":["bfloat16","float32","bfloat16","float32"],"output_shapes":[[1,4096,4,64],[1,4096,4,4],[1,4096,64],[1,4096,4]],"task":"mhc_post_bwd"}` | warmup0_reference |
| `mhc_post_bwd-supp-10` | `mhc_post_bwd` | `{"attrs":{},"input_dtypes":["bfloat16","bfloat16","float32","bfloat16","float32"],"input_shapes":[[1,65,4,512],[1,65,4,512],[1,65,4,4],[1,65,512],[1,65,4]],"output_dtypes":["bfloat16","float32","bfloat16","float32"],"output_shapes":[[1,65,4,512],[1,65,4,4],[1,65,512],[1,65,4]],"task":"mhc_post_bwd"}` | warmup0_reference |
| `normalize-n1-k8` | `moe_normalize_weight` | `{"attrs":{"tokens":1,"topk":8},"input_dtypes":["float32"],"input_shapes":[[1,8]],"output_dtypes":["float32","float32"],"output_shapes":[[1],[1,8]],"task":"moe_normalize_weight"}` | warmup5_single_kernel |
| `normalize-n4001-k6` | `moe_normalize_weight` | `{"attrs":{"tokens":4001,"topk":6},"input_dtypes":["float32"],"input_shapes":[[4001,6]],"output_dtypes":["float32","float32"],"output_shapes":[[4001],[4001,6]],"task":"moe_normalize_weight"}` | warmup5_single_kernel |
| `normalize-n4001-k9` | `moe_normalize_weight` | `{"attrs":{"tokens":4001,"topk":9},"input_dtypes":["float32"],"input_shapes":[[4001,9]],"output_dtypes":["float32","float32"],"output_shapes":[[4001],[4001,9]],"task":"moe_normalize_weight"}` | warmup5_single_kernel |
| `normalize-n512-k8` | `moe_normalize_weight` | `{"attrs":{"tokens":512,"topk":8},"input_dtypes":["float32"],"input_shapes":[[512,8]],"output_dtypes":["float32","float32"],"output_shapes":[[512],[512,8]],"task":"moe_normalize_weight"}` | warmup5_single_kernel |
| `rmsnorm-cann-18` | `rmsnorm` | `{"attrs":{"epsilon":1e-06},"input_dtypes":["bfloat16","bfloat16"],"input_shapes":[[2,511,8192],[8192]],"output_dtypes":["bfloat16"],"output_shapes":[[2,511,8192]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rmsnorm-cann-2` | `rmsnorm` | `{"attrs":{"epsilon":1e-06},"input_dtypes":["float32","float32"],"input_shapes":[[32,128,1024],[1024]],"output_dtypes":["float32"],"output_shapes":[[32,128,1024]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rmsnorm-cann-3` | `rmsnorm` | `{"attrs":{"epsilon":1e-06},"input_dtypes":["bfloat16","bfloat16"],"input_shapes":[[32,128,2048],[2048]],"output_dtypes":["bfloat16"],"output_shapes":[[32,128,2048]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rmsnorm-cann-5` | `rmsnorm` | `{"attrs":{"epsilon":1e-06},"input_dtypes":["float32","float32"],"input_shapes":[[8,512,8192],[8192]],"output_dtypes":["float32"],"output_shapes":[[8,512,8192]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rmsnorm-supp-01` | `rmsnorm` | `{"attrs":{"epsilon":1e-06},"input_dtypes":["bfloat16","bfloat16"],"input_shapes":[[1,64],[64]],"output_dtypes":["bfloat16"],"output_shapes":[[1,64]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rmsnorm-supp-02` | `rmsnorm` | `{"attrs":{"epsilon":1e-05},"input_dtypes":["float32","float32"],"input_shapes":[[7,128],[128]],"output_dtypes":["float32"],"output_shapes":[[7,128]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rmsnorm-supp-03` | `rmsnorm` | `{"attrs":{"epsilon":0.0001},"input_dtypes":["bfloat16","bfloat16"],"input_shapes":[[31,256],[256]],"output_dtypes":["bfloat16"],"output_shapes":[[31,256]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rmsnorm-supp-04` | `rmsnorm` | `{"attrs":{"epsilon":1e-06},"input_dtypes":["float32","float32"],"input_shapes":[[128,512],[512]],"output_dtypes":["float32"],"output_shapes":[[128,512]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rmsnorm-supp-05` | `rmsnorm` | `{"attrs":{"epsilon":1e-05},"input_dtypes":["bfloat16","bfloat16"],"input_shapes":[[511,1024],[1024]],"output_dtypes":["bfloat16"],"output_shapes":[[511,1024]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rmsnorm-supp-06` | `rmsnorm` | `{"attrs":{"epsilon":0.0001},"input_dtypes":["float32","float32"],"input_shapes":[[1024,2048],[2048]],"output_dtypes":["float32"],"output_shapes":[[1024,2048]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rmsnorm-supp-07` | `rmsnorm` | `{"attrs":{"epsilon":1e-06},"input_dtypes":["bfloat16","bfloat16"],"input_shapes":[[4096,4096],[4096]],"output_dtypes":["bfloat16"],"output_shapes":[[4096,4096]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rmsnorm-supp-08` | `rmsnorm` | `{"attrs":{"epsilon":1e-05},"input_dtypes":["float32","float32"],"input_shapes":[[16384,7168],[7168]],"output_dtypes":["float32"],"output_shapes":[[16384,7168]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rmsnorm-supp-09` | `rmsnorm` | `{"attrs":{"epsilon":0.0001},"input_dtypes":["bfloat16","bfloat16"],"input_shapes":[[3,96],[96]],"output_dtypes":["bfloat16"],"output_shapes":[[3,96]],"task":"rmsnorm"}` | warmup5_single_kernel |
| `rope-cann-11` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"half"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[19,1023,19,64],[19,1023,19,64],[1023,32],[1023,32]],"output_dtypes":["float32","float32"],"output_shapes":[[19,1023,19,64],[19,1023,19,64]],"task":"rope"}` | warmup5_QK_range |
| `rope-cann-14` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"half"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[3,13,17,128],[3,13,17,128],[13,64],[13,64]],"output_dtypes":["float32","float32"],"output_shapes":[[3,13,17,128],[3,13,17,128]],"task":"rope"}` | warmup5_QK_range |
| `rope-cann-2` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"half"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[7,1021,31,64],[7,1021,31,64],[1021,32],[1021,32]],"output_dtypes":["float32","float32"],"output_shapes":[[7,1021,31,64],[7,1021,31,64]],"task":"rope"}` | warmup5_QK_range |
| `rope-cann-20` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"interleaved"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[7,2047,7,128],[7,2047,7,128],[2047,64],[2047,64]],"output_dtypes":["float32","float32"],"output_shapes":[[7,2047,7,128],[7,2047,7,128]],"task":"rope"}` | warmup5_QK_range |
| `rope-cann-5` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"interleaved"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[8,2048,16,128],[8,2048,16,128],[2048,64],[2048,64]],"output_dtypes":["float32","float32"],"output_shapes":[[8,2048,16,128],[8,2048,16,128]],"task":"rope"}` | warmup5_QK_range |
| `rope-cann-8` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"half"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[7,1009,7,128],[7,1009,7,128],[1009,64],[1009,64]],"output_dtypes":["float32","float32"],"output_shapes":[[7,1009,7,128],[7,1009,7,128]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-01` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"half"},"input_dtypes":["bfloat16","bfloat16","float32","float32"],"input_shapes":[[1,1,1,64],[1,1,1,64],[1,32],[1,32]],"output_dtypes":["bfloat16","bfloat16"],"output_shapes":[[1,1,1,64],[1,1,1,64]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-02` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"half"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[2,7,4,128],[2,7,4,128],[7,64],[7,64]],"output_dtypes":["float32","float32"],"output_shapes":[[2,7,4,128],[2,7,4,128]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-03` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"interleaved"},"input_dtypes":["bfloat16","bfloat16","float32","float32"],"input_shapes":[[3,31,8,64],[3,31,8,64],[31,32],[31,32]],"output_dtypes":["bfloat16","bfloat16"],"output_shapes":[[3,31,8,64],[3,31,8,64]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-04` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"interleaved"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[1,128,1,128],[1,128,1,128],[128,64],[128,64]],"output_dtypes":["float32","float32"],"output_shapes":[[1,128,1,128],[1,128,1,128]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-05` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"half"},"input_dtypes":["bfloat16","bfloat16","float32","float32"],"input_shapes":[[2,511,4,64],[2,511,4,64],[511,32],[511,32]],"output_dtypes":["bfloat16","bfloat16"],"output_shapes":[[2,511,4,64],[2,511,4,64]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-06` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"half"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[3,1024,8,128],[3,1024,8,128],[1024,64],[1024,64]],"output_dtypes":["float32","float32"],"output_shapes":[[3,1024,8,128],[3,1024,8,128]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-07` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"interleaved"},"input_dtypes":["bfloat16","bfloat16","float32","float32"],"input_shapes":[[1,2048,1,64],[1,2048,1,64],[2048,32],[2048,32]],"output_dtypes":["bfloat16","bfloat16"],"output_shapes":[[1,2048,1,64],[1,2048,1,64]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-08` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"interleaved"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[2,1,4,128],[2,1,4,128],[1,64],[1,64]],"output_dtypes":["float32","float32"],"output_shapes":[[2,1,4,128],[2,1,4,128]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-09` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"half"},"input_dtypes":["bfloat16","bfloat16","float32","float32"],"input_shapes":[[3,7,8,64],[3,7,8,64],[7,32],[7,32]],"output_dtypes":["bfloat16","bfloat16"],"output_shapes":[[3,7,8,64],[3,7,8,64]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-10` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"half"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[1,31,1,128],[1,31,1,128],[31,64],[31,64]],"output_dtypes":["float32","float32"],"output_shapes":[[1,31,1,128],[1,31,1,128]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-11` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"interleaved"},"input_dtypes":["bfloat16","bfloat16","float32","float32"],"input_shapes":[[2,128,4,64],[2,128,4,64],[128,32],[128,32]],"output_dtypes":["bfloat16","bfloat16"],"output_shapes":[[2,128,4,64],[2,128,4,64]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-12` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"interleaved"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[3,511,8,128],[3,511,8,128],[511,64],[511,64]],"output_dtypes":["float32","float32"],"output_shapes":[[3,511,8,128],[3,511,8,128]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-13` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"half"},"input_dtypes":["bfloat16","bfloat16","float32","float32"],"input_shapes":[[1,1024,1,64],[1,1024,1,64],[1024,32],[1024,32]],"output_dtypes":["bfloat16","bfloat16"],"output_shapes":[[1,1024,1,64],[1,1024,1,64]],"task":"rope"}` | warmup5_QK_range |
| `rope-supp-14` | `rope` | `{"attrs":{"layout":0,"rotaryMode":"half"},"input_dtypes":["float32","float32","float32","float32"],"input_shapes":[[2,2048,4,128],[2,2048,4,128],[2048,64],[2048,64]],"output_dtypes":["float32","float32"],"output_shapes":[[2,2048,4,128],[2,2048,4,128]],"task":"rope"}` | warmup5_QK_range |
| `sinkhorn-cann-1` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":20},"input_dtypes":["float32"],"input_shapes":[[1,4,4]],"output_dtypes":["float32"],"output_shapes":[[1,4,4]],"task":"sinkhorn"}` | warmup0_reference, warmup5_single_kernel |
| `sinkhorn-cann-13` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":1},"input_dtypes":["float32"],"input_shapes":[[1024,4,4]],"output_dtypes":["float32"],"output_shapes":[[1024,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-cann-14` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":5},"input_dtypes":["float32"],"input_shapes":[[1024,4,4]],"output_dtypes":["float32"],"output_shapes":[[1024,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-cann-15` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":40},"input_dtypes":["float32"],"input_shapes":[[1024,4,4]],"output_dtypes":["float32"],"output_shapes":[[1024,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-cann-16` | `sinkhorn` | `{"attrs":{"eps":1e-08,"iter_step":20},"input_dtypes":["float32"],"input_shapes":[[1024,4,4]],"output_dtypes":["float32"],"output_shapes":[[1024,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-cann-17` | `sinkhorn` | `{"attrs":{"eps":1e-07,"iter_step":20},"input_dtypes":["float32"],"input_shapes":[[1024,4,4]],"output_dtypes":["float32"],"output_shapes":[[1024,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-cann-19` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":20},"input_dtypes":["float32"],"input_shapes":[[1024,4,4]],"output_dtypes":["float32"],"output_shapes":[[1024,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-cann-2` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":20},"input_dtypes":["float32"],"input_shapes":[[64,4,4]],"output_dtypes":["float32"],"output_shapes":[[64,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-cann-20` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":20},"input_dtypes":["float32"],"input_shapes":[[1024,4,4]],"output_dtypes":["float32"],"output_shapes":[[1024,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-cann-3` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":20},"input_dtypes":["float32"],"input_shapes":[[512,4,4]],"output_dtypes":["float32"],"output_shapes":[[512,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-cann-4` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":20},"input_dtypes":["float32"],"input_shapes":[[1024,4,4]],"output_dtypes":["float32"],"output_shapes":[[1024,4,4]],"task":"sinkhorn"}` | warmup0_reference, warmup5_single_kernel |
| `sinkhorn-cann-5` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":20},"input_dtypes":["float32"],"input_shapes":[[4096,4,4]],"output_dtypes":["float32"],"output_shapes":[[4096,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-cann-6` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":20},"input_dtypes":["float32"],"input_shapes":[[16384,4,4]],"output_dtypes":["float32"],"output_shapes":[[16384,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-supp-01` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":1},"input_dtypes":["float32"],"input_shapes":[[1,4,4]],"output_dtypes":["float32"],"output_shapes":[[1,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-supp-02` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":2},"input_dtypes":["float32"],"input_shapes":[[7,4,4]],"output_dtypes":["float32"],"output_shapes":[[7,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-supp-03` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":5},"input_dtypes":["float32"],"input_shapes":[[31,4,4]],"output_dtypes":["float32"],"output_shapes":[[31,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-supp-04` | `sinkhorn` | `{"attrs":{"eps":1e-05,"iter_step":10},"input_dtypes":["float32"],"input_shapes":[[128,4,4]],"output_dtypes":["float32"],"output_shapes":[[128,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-supp-05` | `sinkhorn` | `{"attrs":{"eps":1e-05,"iter_step":20},"input_dtypes":["float32"],"input_shapes":[[511,4,4]],"output_dtypes":["float32"],"output_shapes":[[511,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-supp-06` | `sinkhorn` | `{"attrs":{"eps":1e-05,"iter_step":40},"input_dtypes":["float32"],"input_shapes":[[1024,4,4]],"output_dtypes":["float32"],"output_shapes":[[1024,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `sinkhorn-supp-07` | `sinkhorn` | `{"attrs":{"eps":1e-06,"iter_step":1},"input_dtypes":["float32"],"input_shapes":[[4096,4,4]],"output_dtypes":["float32"],"output_shapes":[[4096,4,4]],"task":"sinkhorn"}` | warmup0_reference |
| `swiglu-cann-15` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["float32"],"input_shapes":[[512,4096]],"output_dtypes":["float32"],"output_shapes":[[512,2048]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-cann-2` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["float32"],"input_shapes":[[2048,4096]],"output_dtypes":["float32"],"output_shapes":[[2048,2048]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-cann-3` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["bfloat16"],"input_shapes":[[4096,8192]],"output_dtypes":["bfloat16"],"output_shapes":[[4096,4096]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-01` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["bfloat16"],"input_shapes":[[1,256]],"output_dtypes":["bfloat16"],"output_shapes":[[1,128]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-02` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["float32"],"input_shapes":[[7,256]],"output_dtypes":["float32"],"output_shapes":[[7,128]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-03` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["bfloat16"],"input_shapes":[[31,512]],"output_dtypes":["bfloat16"],"output_shapes":[[31,256]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-04` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["float32"],"input_shapes":[[128,1024]],"output_dtypes":["float32"],"output_shapes":[[128,512]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-05` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["bfloat16"],"input_shapes":[[511,2048]],"output_dtypes":["bfloat16"],"output_shapes":[[511,1024]],"task":"swiglu"}` | warmup0_reference, warmup5_single_kernel |
| `swiglu-supp-06` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["float32"],"input_shapes":[[1024,4096]],"output_dtypes":["float32"],"output_shapes":[[1024,2048]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-09` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["bfloat16"],"input_shapes":[[3,256]],"output_dtypes":["bfloat16"],"output_shapes":[[3,128]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-10` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["float32"],"input_shapes":[[65,768]],"output_dtypes":["float32"],"output_shapes":[[65,384]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-11` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["bfloat16"],"input_shapes":[[257,1280]],"output_dtypes":["bfloat16"],"output_shapes":[[257,640]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-12` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["float32"],"input_shapes":[[2048,8448]],"output_dtypes":["float32"],"output_shapes":[[2048,4224]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-13` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["bfloat16"],"input_shapes":[[11,1536]],"output_dtypes":["bfloat16"],"output_shapes":[[11,768]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-14` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["float32"],"input_shapes":[[513,3072]],"output_dtypes":["float32"],"output_shapes":[[513,1536]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-15` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["bfloat16"],"input_shapes":[[8192,16384]],"output_dtypes":["bfloat16"],"output_shapes":[[8192,8192]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-16` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["float32"],"input_shapes":[[2,256]],"output_dtypes":["float32"],"output_shapes":[[2,128]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-17` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["bfloat16"],"input_shapes":[[127,4352]],"output_dtypes":["bfloat16"],"output_shapes":[[127,2176]],"task":"swiglu"}` | warmup5_single_kernel |
| `swiglu-supp-18` | `swiglu` | `{"attrs":{"dim":-1},"input_dtypes":["float32"],"input_shapes":[[1009,8448]],"output_dtypes":["float32"],"output_shapes":[[1009,4224]],"task":"swiglu"}` | warmup5_single_kernel |
