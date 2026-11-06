# TileKernels 专家 profile 盘点

本盘点只包括原已准入的 TileKernels 专家样本，以及用户为 Engram `[4,3584]` 选定的较快 B 版。CANN 库算子、教学 Triton、客户 rounds、人工额外写出、读取/Fixpipe 探针均另列。沿用归档精度状态，不把历史失败样本重判为通过。

当前共有 **11 个算子族、99 个登记 case ID、97 个不同 shape/dtype/attrs 任务定义、140 份选定专家 Default 采集**。一个 Default 内的 PMU 多组重放只算一份。RoPE 同一 case 的 Q、K 分别计 kernel 采集，两者仍只算一个算子 case。Sinkhorn 的 `cann-4/19/20` 同定义，合并为一个。

| 算子族 | 登记 case ID | 不同任务定义 | Default 采集数 |
|---|---:|---:|---:|
| RMSNorm | 13 | 13 | 17 |
| SwiGLU | 19 | 19 | 22 |
| RoPE | 20 | 20 | 40 |
| Sinkhorn | 20 | 18 | 26 |
| mHC post backward | 7 | 7 | 7 |
| Engram fused weight | 5 | 5 | 7 |
| MoE normalize weight | 4 | 4 | 4 |
| FP8 cast back | 4 | 4 | 4 |
| Engram hash | 4 | 4 | 4 |
| mHC expand forward | 1 | 1 | 3 |
| mHC head compute mix | 2 | 2 | 6 |
| 合计 | 99 | 97 | 140 |

139 份来自主归档，另加早期 SwiGLU smoke 的一份 Default，合计 140。该 smoke 的 case 已在表内，因此不增加 case。较慢 Engram A 版还有三份配对采集，保留作对照，未计入选定专家的 140 份。

## 采集口径

- 五次应用预热的单 kernel replay 有 72 份，覆盖 54 个任务定义。
- 五次应用预热的 RoPE Q+K range 有 40 份目标 kernel 采集，覆盖 20 个 case。K 前没有再次清 L2，Q/K 需按角色分开。
- 无应用预热的历史参考有 28 份，包含旧 Sinkhorn/mHC 的 27 份和早期 SwiGLU smoke 一份。
- 74 个任务定义有五次应用预热记录，另 23 个只有历史参考。两块卡的原总线地址 `8B:00.0` 和 `0D:00.0` 分组保留。不能仅凭同工具与频率字段认定所有性能指标直接可比。

所有选定 TileKernels profile 均为 AIV、56 个逻辑 block。当前纯 Cube、混合执行的补充证据来自 CANN 和 Triton，未混入此表。只有同一 SwiGLU case 额外取得过一份上板 PipeTimeline，不增加独立 case；专家库没有广覆盖 InstrTimeline 或 PipeTimeline。

## 字段是否实际可用

已逐项校验 1,120 份 CSV 的内容 SHA256，并核对身份。140/140 份在以下字段中都有完整 56 行数值：主存读、主存写、GM→UB、AIV 总时间/周期、Vector/Scalar/MTE2/MTE3 活动时间、L2 读写 hit rate、I-cache miss rate、Vector/MTE 等待或冲突比例，以及 VF/SFU/SIMT-VF 占比。

`UB_to_GM_datas(KB)` 完整数值为 **0/140**。它的缺失不能用主存写计数填成“等价的 UB→GM 数值”。hit rate 有数值也不代表每份都有充分访问事件，实际使用还需核对计数分母。

[完整 case、采集和文件索引](inventory.json) · [复算入口](recompute.py)

```powershell
python -B outputs/tilekernels-profile-inventory-reset-20261105/recompute.py
```
