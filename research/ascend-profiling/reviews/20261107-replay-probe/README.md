# 原地累加算子的重放复查：一个实测例子

在 hidev 上使用原始的 `engram_grad_w_reduce-01`、原 TileKernels 源码、同一输入和原采集选项重新运行。此算子会将结果累加到两个已有梯度数组中。`record.json` 中的源码及五个调用前输入的 SHA256 均与原始 `prepare.json` 一致。

目标调用位于 MSTX 标记范围内，原生应用侧预热使用独立的缓冲区；`msprof op --aic-metrics=Default --replay-mode=kernel --mstx=true --mstx-include=quant_target --kernel-name=engram_grad_w_reduce_kernel_asc_kernel --launch-count=1 --warm-up=5`。profile 后，将两个目标输出分别与从同样初值开始、未被 profile 的一次调用和两次连续调用比较。后两者在 MSTX 范围外，仅用作结果对照。

| 比较 | 梯度数组一 | 梯度数组二 |
|---|---:|---:|
| profile 后与一次调用不同的元素数 | 0 / 4096 | 0 / 4096 |
| 一次调用与两次调用不同的元素数 | 4096 / 4096 | 4096 / 4096 |

`comparison.json` 保存逐数组 hash 和数量；`record.json` 保存输入 hash 与原测试结果；`profile.log` 保存采集日志。profile 完成，原始上游正确性测试通过。

结论仅限此例的**最终输出**。它不能直接证明 profiler 中各指标采集轮次的输入状态，也不能证明其他原地算子的情况。原记录状态没有被修改。
