# 2026-11-07 profile 待复核清单

本目录记录对既有 `needs_review` 的只读审计：**220 个原计划 case 对应 240 条 native kernel capture**。20 个 RoPE case 各有 Q、K 两条 capture；JSON 将二者放在同一个原计划 case 的 `captures` 数组中。

当前 70 个 case、70 条 capture 的指定目标 kernel 没有对同一输入缓冲区进行原地读写，因此原有的“原地恢复未验证”理由不适用。其余 150 个 case、170 条 capture 确实有输入缓冲区的读写或累加，保留这项复核。**这是针对原地恢复理由的审计结论，不会修改原始状态，也不表示 profile 的所有语义或性能指标已经达标。**

| 类别 | 原计划 case | capture | 判断 |
| --- | ---: | ---: | --- |
| Engram gate fwd，save=True、inplace=False | 20 | 20 | 独立输出 |
| Engram gate bwd | 20 | 20 | 独立输出 |
| MoE gate bwd | 20 | 20 | 独立输出 |
| MoE gate fwd，fix_routing=False | 10 | 10 | unmapped 索引只写 |
| MoE gate fwd，fix_routing=True | 10 | 10 | unmapped 索引读写 |
| Engram grad_w_reduce | 20 | 20 | 梯度累加读写 |
| Engram Sinkhorn momentum | 20 | 20 | momentum 读写 |
| Engram Sinkhorn step | 20 | 20 | row_scale 读写 |
| mHC fn/normw merge bwd | 20 | 20 | 两个梯度累加读写 |
| mHC pre-apply mix bwd | 11 | 11 | 梯度累加读写 |
| Quant norm bwd | 9 | 9 | weight_grad 累加读写 |
| Quant per-token cast and cast-back | 20 | 20 | x 原地读写 |
| RoPE | 20 | 40 | Q、K 分别原地读写 |

## 逐条证据与复算

- `case-review.json` 包含每个原计划 case 的参数、分类和源码位置；每条 capture 包含 Q/K 角色、原始结果状态、prepare/default/result 路径及 SHA256、kernel 名称、生成源码哈希和全部 8 张原始 CSV 的路径及 SHA256。
- 每条记录的 `checks` 来自 `recompute.py` 的实际检查。脚本绑定原计划、manifest、实际命令里的 base64 参数、采集环境和 adapter 哈希；核对 prepare/default 的状态、输入、源码哈希和 kernel 名称；检查前后空闲记录、采集命令、原始 CSV 哈希，以及全部 56 个 vector block 的表行。
- 在 `TileKernels-private` 仓库根目录运行：

  ```powershell
  python -B research/ascend-profiling/reviews/20261107-review/recompute.py --check
  ```

  `--check` 重新读取证据并与 `case-review.json` 逐字节比较；`--write` 重新生成本目录的 JSON。检查不调用 NPU、profiler 或 Git，不改动原始证据和状态。证据文件变化或数量不符会失败。

## 口径和限制

- 两阶段测试通过只说明记录中的上游正确性检查通过。对于读写同一缓冲区的 kernel，它不能单独证明 msprof 每次内部重放前都恢复了原值。
- `--warm-up=5` 是 profiler 命令中的设置；部分 adapter 还有单独的 5 次应用层预热。记录的命令和输出检查不能单独证明每次 profiler 内部重放的输入值、重放次数或缓存状态。
- Forward 的计划未指定 save/inplace；这里的 20 条只对应 `save_for_backward=True, inplace=False`。图像 mask 对应的 saved statistics 按上游测试口径不做检查。
- MoE forward 的非固定路由有 10 条，其中 06、16 有实际命中的 force-random token；其余 8 条未命中。固定路由的测试 fixture 将 force-random mask 置为全 False，不能把配置开关存在当作随机路径已覆盖。每条 `route_counts` 保留在 JSON 中。随机行为的 profiler 内部重放细节仍未单独验证。
- 该清单记录的是既有采集的核对结果，没有补跑设备、证明硬件性能上限或改变任何原始 case 的 `needs_review` 状态。
