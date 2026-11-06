# P06/P09：混合执行时间线接入检查

结论：本次检查的历史混合、CANN/Cube 记录没有可准入的同次 AIC/AIV 活动或等待区间，**重叠参考不足**。不从 PMU 累计值、比率或不同采集的时间推断重叠，不设阈值。这里只检查列出的样本，不代表所有历史资料或工具没有此能力。

| 证据 | 本次核查 | 可支持的范围 |
|---|---|---|
| 9.2.1 GroupedMatmul b1/b2 补采普通 trace | 各 282 个事件，六个 MIX_AIC 任务；stream 61 的目标 Task ID 11 为一条 kernel 任务区间。历史 MSTX 与 op_summary 的范围核验另见 [scope supplement](../../../experiments/profile-checklist-4-mix-20261105/evidence/scope-supplement.json) | 定位本次普通 trace 的目标任务；无逐 AIC/AIV 流水活动或等待区间。两份 trace 与此前 6 份 Default 是不同采集；不可拼成同一物理调用。历史六次 Default 的实际二进制哈希未在采集前逐次绑定 |
| 9.2.1 CANN MatMul、BMM 普通 trace | 分别可见一条 AI_CORE 目标任务事件 | 任务级区间；不是 Cube 内部流水区间，也不能用于混合协作 |
| 9.2.1 原生 Cube base-r1 普通 trace | 一条 AI_CORE 目标任务事件 | 任务级区间；无同次 AIV 事件 |
| 现有 SwiGLU PipeTimeline | 一个真实 `profilingType=op, schemaVersion=1` 文件，218 个事件，含 MTE2、MTE3、SCALAR、VECTOR；12 个执行行标签 | 是单 AIV SwiGLU 示例，不是 M1。事件标签、显示单位、同步与覆盖不能仅由名称推定，不能嫁接到上述任务或跨执行行直接比较 |
| 混合 Default 表 | PipeUtilization 与 ResourceConflictRatio 给分侧活动累计量及原生等待比；按工具执行行键登记 | PMU 重放汇总，不提供同窗口的开始结束事件；最大值也可能来自不同 block，不能推导交并集或关键路径 |

逐文件路径、SHA256 与只读检查结果见 [trace-inventory.json](trace-inventory.json)。旧证据结果与先前分析一致，但本次没有重新采集，也未将 `MIX_AIC` 的任务区间误称 AIC 活动区间。

## 程序与边界

`overlap(a,b)` 是纯数学函数：将各侧半开区间分别取并集，然后计算交集和并集长度；重叠的同侧区间不会重复计数。它不会验证实际事件来源、时钟、调用或覆盖。空集合交并均为零，非法区间拒绝。它只供已经独立验证的同一物理调用、同一时钟和一致单位的事件使用。

`overlap.py` CLI 只检查上面实际见过的普通 msprof 顶层事件数组和 op v1 PipeTimeline 对象。普通 trace 必须以 task ID、物理 stream、kernel 名唯一匹配；即使匹配也返回 `reference_insufficient`。PipeTimeline 只列出 schema、事件名与执行行，不猜测其语义或计算重叠。未知 schema、缺失和歧义同样拒绝。匹配 Task ID/stream 本身不能证明 MSTX 范围、跨文件关联或活动事件完整。

```powershell
python -B outputs/expert-rule-todo6-20261106/mix-overlap/overlap.py <msprof-trace.json> --task 11 --stream 61 --name <完整kernel名>
python -B -m unittest discover -s outputs/expert-rule-todo6-20261106/mix-overlap -v
```

6 项 CPU 测试覆盖合并区间、交并、空区间、无效数据、目标缺失/重复及真实 pipe schema 的拒绝。实际样本检查是 `trace-inventory.json` 中列出的六份。该程序不是通用 profiler 解码器；没有人工输入声称可用的机制来绕过准入。

## M1 后续最小证据

针对 CANN 9.2.0 M1 的**一次物理目标调用**，先确认工具实际支持，再保留原始记录与导出：

1. 设备及 PCI、实际加载 runtime/collector 版本、源码和实际二进制哈希、单目标调用标识、MSTX 边界、预热和 replay；明确该时间线与目标调用的直接绑定。
2. AIC 与 AIV 各执行归属、资源/pipe 和活动或等待事件的起止时间、单位、事件定义；明确配对的生产消费角色及同步依赖。仅任务时间或 PMU 周期占比不足。
3. 跨侧共同时钟或可审计同步/转换与误差、采样/截断/丢失统计、区间覆盖范围和有效性证明。若工具不能提供上述字段，保留缺口，不把不同 replay 的采集拼接。

之后才能针对清楚的同窗口事件计算交集；进一步解释等待是否可避免或处于关键路径仍需依赖与可重叠机会证据。CANN 9.2.0 尚未获得上述 M1 证据，旧 9.2.1 结果不自动迁移。未使用客户数据、未上板、未修改采集器或主 TODO。
