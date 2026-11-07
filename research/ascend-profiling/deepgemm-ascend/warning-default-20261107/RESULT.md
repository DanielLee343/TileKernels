# `kernel.json` 警告对 Default 采集的对照结果

以 `PLAN.md` 中预先固定的方法，在 950PR、CANN 9.2.1、相同采集器上比较两种条件：A 没有 JSON，B 在同一 ELF 旁显式提供与缺失时相同的 `RT_DEV_BINARY_MAGIC_ELF`。两个 BF16 case 分别是纯 Cube 和混合执行，按 ABBAAB 各重复 6 次。每次的输入、参考、输出与 kernel 二进制均通过身份和精度检查；A 出现警告，B 不出现。12 次的 228 个原始 profile 文件已核对 SHA-256。

所有 7 张 Default 指标表的列、核和子核键、字段是否可用均一致。所查两例中，Cube 搬运指令计数以及 `read_main_memory_datas(KB)`、`write_main_memory_datas(KB)`、`GM_to_L1_datas(KB)` 的逐角色平均值在 A、B 各次一致；混合执行的向量核 MTE2/MTE3 指令计数也一致。详见 `comparison.json`，这些计数的一致不是对真实物理量正确性的独立标定。

时间、速率和比例等可变指标不能一概声称无影响。例如混合 case 的 `vector1/aiv_scalar_ratio` 按核平均：A 为 0.08884、0.09466、0.09417，B 为 0.08304、0.09327、0.08339；组间中位数差异超过每组内部的数值范围。每组仅三次，并伴随其他时间/速率变化，不能确定这是文件缺失引起还是运行波动。需根据具体规则使用的字段做重复性和必要的进一步对照。

**适用边界：**本次对照只比较了缺 JSON 与显式写入 profiler 所用的同一个默认 magic；它不能证明默认 magic 本身对于每种 kernel 均正确，也不能推广到 FP8/FP4、其他工具版本或 MemoryDetail。所测两个 BF16 case 的上述计数未见 JSON 缺失带来的差异；其他字段保留不确定性。12 个对照结果不是 12 个独立专家样本，不能用于规则阈值训练。
