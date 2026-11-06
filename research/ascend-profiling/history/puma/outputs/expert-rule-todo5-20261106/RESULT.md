# TODO 5：首批 Default 采集结果

## 结论

已按冻结清单和交错顺序完成 **25 次采集**。其中 **19 次结束时的设备检查没有发现其他进程**；另外 **6 次在结束检查中发现其他进程，标记为可能受干扰**，保留原始数据，后续须单列。采集前后快照不能证明两次快照之间完全没有其他活动。

| case | 计划次数 | 结束时未发现其他进程 | 可能受干扰 |
|---|---:|---:|---|
| B-H | 5 | 3 | r2、r4 |
| B-L | 5 | 4 | r3 |
| D1 | 3 | 1 | r1、r3 |
| D2 | 3 | 2 | r1 |
| D3 | 3 | 3 | 无 |
| D4 | 3 | 3 | 无 |
| D5 | 3 | 3 | 无 |

采集调度进程的最终退出码为 **1**，原因是存在上述六次干扰标记；不是六次 profiler 命令失败。25 次 `msprof op` 命令和对应 prepare 命令退出码均为 0。没有补测、挑选重试或用其他 case 替换。当前没有据此计算规则阈值或声称某种性能结论。

## 准入与身份

七例在正式采集前各做了一次独立单调用：输出预填新鲜哨兵、无应用预热，随后一次调用即检查全部输出、输出前后保护区、D2 行 padding，以及输入和权重是否变化。七例均通过，device/host binary 与 BasicInfo 准入的同例哈希相符。第一次尝试因卡 5 被占用而没有启动任何 case，该记录保留在 `single-check/`；实际通过结果在 `single-check-02/`。

正式采集固定 A5 物理卡 5、PCI `0000:E1:00.0`、Ascend950PR、CANN 9.2.0；实际执行的 `msprof op` 为 26.2.0、构建 `884ac969494a186a9c63ac45c4c39ad7289b3215`，区别于直接运行的 26.1.0 `msopprof`。TileKernels 提交 `c1cf914a82e6901c679445f872051ce44ac2cc63`。每次采用 Default、kernel replay、五次应用预热、五次工具预热、MSTX 目标范围及一次采集。

独立复核确认 25 次顺序及输入、shape、dtype、stride、目标 kernel、生成源码、host/device binary 与准入一致；每次均保留非空 `Memory.csv`、`PipeUtilization.csv`、`OpBasicInfo.csv` 和 profiler 原始文件，并逐文件核对其采集时清单。D1、D2 的逻辑输入和 weight 哈希相同，行 stride 分别为 4096、4112。原预登记和七例 BasicInfo 证据见 [PREREG-DEFAULT.md](PREREG-DEFAULT.md) 与 [GATE.md](GATE.md)。C/H、D6/D7 未进入本批。

## 归档与复核

- 已校验展开的完整证据根目录：[bundle](bundle/)。[逐次核验结果](bundle/default-batch/verification.json)与[逐次执行状态](bundle/default-batch/results.json)在其中；采集命令、时间、日志、原表、二进制和每次文件哈希均在对应采集子目录。
- [压缩归档](evidence-20261106.tar.gz) SHA256：`ba77128ce3ccf399da3d4b00ff7e636a8e4d40c2093859918ddb59d803cce880`，与 A5 原包一致。
- 包外 [逐文件 SHA256 清单](bundle-manifest.sha256)覆盖 1,005 个文件；[展开校验结果](bundle-verification.json)确认归档与展开内容逐字节一致，没有额外或缺失文件。独立核验脚本按展开数据再次核对了 25 次身份和状态，结果见 [verification-recomputed.json](verification-recomputed.json)。
- 采集进程 A5 PID 为 `2692726`，已退出。执行时在等待卡 5 空闲的间隙暂停过该进程，串行完成卡 6 的 3B 正控及 Router 复核后恢复，未并发运行两次 profiler。3B 的结果另见 [TODO 3B](../expert-rule-todo3b-20261106/RESULT.md)。
