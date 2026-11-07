# 150 条重放验收与 13 条 profile 补采

## 结果

1,000 个计划 case 均已采到 Default profile：此前 987 个，加上本次补采的 13 个。**有 profile 与通过精度检查是两件事**：本次 13 个在原 CPU 参考检查下仍全部失败；保留 profile，不把这些失败改为通过。

### 150 个原地 case

170 条 native kernel capture（含 RoPE 的 Q、K）均复测，逐条绑定原输入、源码和 kernel 身份。共核验 2,220 次观察到的恢复，目标数组的完整地址范围均被所观察到的恢复内存块覆盖，抽查字节在恢复后均与初值一致。168 条采集至少一次在恢复前观察到数据变化。

其余 `moe_topk_gate_forward-04` 和 `-09` 的固定路由路径没有在抽样位置观察到变化。随后对各自的目标缓冲区做完整字节检查：分别检查 24,576 和 32,768 字节，所有观察到的恢复前后均与初值一致。其输入、源码和 kernel 与原采集一致；另一条同类固定路由样例 `-02` 已观察到恢复前变化，作为同类对照。

这些是**新的插桩复测**：除上述两个小缓冲区外，内容比较仍是抽样，不是对原始 profile 每轮逐字节的直接观察。插桩产生的 profile 已改变同步、缓存和耗时，不能作为性能数据。原始 profile 和原 `needs_review` 状态不被改写；后续规则研究可使用本次复核结果，并保留这里的证据边界。

### 13 个原精度失败 case

13 个均补采了未插桩的 `msprof op --aic-metrics=Default --replay-mode=kernel` 数据，原始 profile、全部 8 张指标表、命令、日志及二进制均保存。校验了输入 hash、生成源码 hash、kernel 名称、56 个 Vector block 及各文件 SHA256。13 个的原 CPU 参考检查均仍失败。

对相同输入另做 NPU PyTorch 参考比较，使用对应测试的原容差，并检查比较结果均有限：

| Case | NPU 参考下超差元素数 | 说明 |
|---|---:|---|
| normalize-03 | 7 | 分母超差，归一化权重通过 |
| normalize-16 | 11 | 分母超差，归一化权重通过 |
| normalize-20 | 249 | 分母超差，归一化权重通过 |
| mhc_pre_apply_mix_bwd-02 | 8 | `x_grad` 超差，`mix_grad` 通过 |
| mhc_pre_apply_mix_bwd-04 | 11 | 同上 |
| mhc_pre_apply_mix_bwd-06 | 2 | 同上 |
| mhc_pre_apply_mix_bwd-09 | 1 | 同上 |
| mhc_pre_apply_mix_bwd-10 | 2 | 同上 |
| mhc_pre_apply_mix_bwd-11 | 10 | 同上 |
| mhc_pre_apply_mix_bwd-12 | 5 | 同上 |
| mhc_pre_apply_mix_bwd-14 | 4 | 同上 |
| mhc_pre_apply_mix_bwd-18 | 5 | 同上 |
| mhc_post_bwd-04 | 0 | NPU 分块参考通过；原 CPU 参考失败 |

pre-apply 对照保持原 case 的**非零初始梯度**，用 FP32 自动求导并加回初值，再转换为 BF16；上游测试采用零初始梯度，因此不能把本次失败表述为直接运行上游测试失败。post 采用 NPU **分块**参考，上游测试采用整形 NPU 参考，故也不能直接说通过完整上游测试。12 个 NPU 参考超差和 1 个两种参考结果不一致的 case 均不自动列为精度通过的专家样本；如用于研究，应明确保留精度标签。

## 可复验的文件

- `replay-evidence/`：150 个 case 的 170 份原始重放诊断记录和 SHA256 清单；`full-control-evidence/` 是上述两个完整缓冲区对照。
- `replay-assessment.json`：原有 220 个待复核 case 的逐条结论索引，区分 150 个复测支持恢复的 case 与 70 个不适用原地恢复检查的 case；不修改原始采集状态。
- `capture-evidence/`：13 份补采的全部原始 profiler 输出、生成源码、日志、结果和 SHA256 清单。总内容约 4.8 MB，未因体积省略二进制。
- `accuracy-evidence/`：9 个 pre-apply 的 CPU／NPU 分块比较和记录；normalize 与 post 的原始比较在相邻 `20261107-replay-debug/evidence/` 目录。
- `summary.json`：13 个 case 的参数、profile 路径、两种参考检查状态与逐输出超差数量。
- 在仓库根目录运行以下只读核验；第三项检查 Git 索引中的证据文件与原始 SHA256 一致：

  ```powershell
  python -B research/ascend-profiling/reviews/20261107-finalize/verify_replay.py
  python -B research/ascend-profiling/reviews/20261107-finalize/verify_accuracy_and_capture.py
  python -B research/ascend-profiling/reviews/20261107-finalize/verify_git_evidence.py
  ```

本批运行在 hidev Ascend950PR `0000:57:00.0`、TileKernels `c1cf914a82e6901c679445f872051ce44ac2cc63`、msopprof `26.2.0 (884ac969494a186a9c63ac45c4c39ad7289b3215)`。没有修改 TileKernels kernel、输入参数或精度阈值。
