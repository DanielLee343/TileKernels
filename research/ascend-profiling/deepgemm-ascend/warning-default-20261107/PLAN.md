# `kernel.json` 警告：Default 指标影响验证

## 问题与源码线索

DeepGEMM JIT 将 `kernel.o` 交给 `aclrtBinaryLoadFromFile`，未在同目录写 `kernel.json`。msprof op 使用的 msopscommon `892c3ca76b71c3167804977c12db9000abf0b9df` 的文件加载拦截逻辑在读取缺失 JSON 时报告警告，保留初始化的 `RT_DEV_BINARY_MAGIC_ELF`，然后继续建立注册上下文。该提交与上次采集器 `msopprof 884ac969...` 报告的 msopscommon 依赖提交一致。`RT_DEV_BINARY_MAGIC_ELF` 会进入按 ELF kernel 符号区分 AIC/AIV 的路径。

源码可以解释处理分支，但不能单凭此证明所有 Default 指标正确。对照实验只检验缺失 JSON 与显式提供同一个默认 magic 的区别，不检验此 magic 是否适用于所有 kernel 或不同硬件。

## 预登记实验

- 固定两个原有 case：`bf16-m1-n576-k7168`（cube）与 `bf16-m1-n32768-k512`（mix）；使用已有 seed、原始输入生成、精度判断、编译二进制和 Default 采集命令。
- 从已有 JIT 缓存各复制一份到隔离 A/B 目录。A 不添加 JSON；B 在同名 ELF 旁添加诊断用 `kernel.json`，内容仅为 `{"magic":"RT_DEV_BINARY_MAGIC_ELF"}`，与源码中缺失文件时的默认值相同。不能改源码、kernel 二进制、输入、缓存的其他元数据或采集参数。
- 每个 case 按 A、B、B、A、A、B 顺序各采集 3 次；每次检查目标二进制哈希、输入与输出哈希、精度、Op Type、角色键、完整原始文件、告警是否按预期出现/消失。应用预热与 profiler 的重放预热维持各 5 次；记录 L2 状态未独立验证。
- 对所有 Default 表的字段，区分不可用值、可用值、计数与时间/占比。先比较列/角色/有效性模式；计数类比较逐核值及总体变化；时间/占比比较组间差异及组内变化，不预设所有字段逐字节相等。逐项保存比较结果，不由少数指标概括全部指标。
- 只有结构和身份均相符且未见超过重复波动的系统性差异，才可以说“在这两类被测 kernel 和本次 Default 字段范围内，未观察到缺 JSON 额外造成影响”；如存在差异或重复波动无法分辨，则标记相应字段待确认，不能扩大到其他 case、MemoryDetail 或所有版本。
- A/B 仅为诊断对照，**不是新的独立专家样本，也不进入阈值训练**。不因为要让数据一致而修改阈值、实际 kernel 或舍弃反例。
