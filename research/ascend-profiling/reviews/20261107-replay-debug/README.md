# hidev 重放与精度复核

## 目标和边界

对先前标记的 150 个原地 case（170 个 kernel capture，RoPE Q/K 分开）检查 profiler 重放时的数据恢复。原始 profile 不变；实验产生的 profile 因为插桩和主机读回改变了同步、缓存和耗时，**不能用于性能分析**。当前不把未复核或部分抽样自动等同于全量验证。

环境：hidev Ascend950PR `0000:57:00.0`，TileKernels `c1cf914a82e6901c679445f872051ce44ac2cc63`，msopprof `26.2.0 (884ac969494a186a9c63ac45c4c39ad7289b3215)`，其报告的 msopscommon 依赖是 `892c3ca76b71c3167804977c12db9000abf0b9df`。原始采集参数是 Default、kernel replay、warm-up=5、应用层另有 5 次预热。

同版本依赖的 [ProfDataCollect.cpp](https://github.com/Ascend/msopcom/blob/892c3ca76b71c3167804977c12db9000abf0b9df/csrc/runtime/inject_helpers/ProfDataCollect.cpp) 中 `ReplayOnce` 通过 `MemoryContext::Restore` 在计数重放前恢复内存；实际安装二进制反汇编也观察到恢复调用。非普通重放路径如 MC2、LCCL 等不在本批结论内。

## 实验方法

`make_plan.py` 从既有逐项审计与原结果中生成 170 次 capture 计划。`trace_adapter.py` 在原 adapter 的目标标记前登记实际读写的数组；`restore_watch.c` 在实际安装的 profiler 的恢复函数周围插桩，对每个目标数组的起始、中间、末尾最多各 4096 字节做恢复前后比对，并登记 profiler 恢复的内存块。`controller.py` 串行运行；验证全部目标数组的地址范围包含在恢复块内、每次被记录的样本恢复后均与初值一致，并核对原采集与复测的输入、生成源码、kernel 名称。日志中还保存恢复前是否发生变化，用作反向对照。

这些检查结合实际二进制和同版本源码提供机制证据，但内容比较是**抽样**，不是对整个数组逐字节验证；而且插桩可能改变运行过程，不能说直接观察到了原先无插桩采集的每一轮。原记录状态不自动改写。

首个 Engram 梯度累加例：两个目标数组，13 次观察到恢复；可变数据在恢复前发生变化，恢复后抽样均和初值一致，并在每次恢复中观察到覆盖整个目标数组地址范围的内存块。独立全数组对照见 `evidence/watch.log`：第 2 至第 13 次恢复前有 15289 / 16384 字节不同，恢复后为 0。

加强版选择 9 个不同算子类别各一个 case，9 个均通过：每次恢复覆盖目标数组的地址范围，抽样恢复后的值一致，且均观察到了恢复前的变化。具体逐次证据见 `pilot-evidence/`。随后全部 170 个 capture 的复测及两个完整缓冲区补充对照已经完成，见[完整验收结果](../20261107-finalize/README.md)。

在仓库根目录运行 `python -B research/ascend-profiling/reviews/20261107-replay-debug/verify_pilots.py`，可独立检查 9 条试点的原始输入、源码、恢复范围、抽样值及反向对照。

## 精度对照：未调整阈值

- `normalize-03/16/20`：复现输入 SHA256 与原记录相同。以相同 NPU 输入计算参考并使用上游 `atol=2e-6, rtol=0`，三个 case 的分母分别有 7、11、249 个元素超差；归一化权重均通过。CPU 参考下的分母超差数量分别为 8、16、308。见 `evidence/normalize-comparison.json`。
- `mhc_pre_apply_mix_bwd-10`：原源码和所有输入 SHA256 匹配；采用原非零梯度初值，完整输入分块计算 CPU 与 NPU 参考，两者均有 2 个 `x_grad` 元素超出上游测试所用的 `atol=1e-2, rtol=1e-3`；`mix_grad` 通过。该非零初值与上游测试的零初值不同。见 `evidence/preapply-comparison.json` 和 `evidence/preapply-record.json`。
- `mhc_post_bwd-04`：原源码和所有输入 SHA256 匹配；CPU 分块参考有 1 个 `grad_comb_res_mix` 元素超差，NPU 分块参考四个输出均通过原容差。上游使用整形 NPU 参考，故这里不声称直接运行了完全相同的上游测试。见 `evidence/post-comparison.json` 和 `evidence/post-record.json`。

三组诊断重跑时分别检查了用于比较的 kernel 输出和参考输出均有限。其余 8 个 mHC pre-apply 的同输入 NPU 参考复测、13 条 profile 补采及精度状态见[完整验收结果](../20261107-finalize/README.md)。
