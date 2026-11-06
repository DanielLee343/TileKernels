# TODO4 离线计量：合同和验证

## 输入合同

此程序只接受**已经独立确认**的有效 GM→UB 只读源字节区间。根对象含 `coverage: "complete"`、`read_only: true` 和 `records` 数组。complete 是对所声明分析范围内事件完整覆盖的调用方断言，并非程序验证；遗漏事件、采样、未知范围或部分覆盖不得填 complete。没有完整覆盖证据时不得运行并报告结果。

每条记录含非空且已知的字符串 `call`, `owner`, `route`, `object`, `version`，及整数 `start`, `end`。route 为 `GM->UB` 或 `GM->UB:<已知子通路>`；其他路径不在此工具范围。范围是同一 allocation/object 内的对象相对字节偏移 `[start,end)`，要求 `0 <= start < end`。碎片化有效字节须拆成多个不重叠片段，并确保每个片段仅表示一次有效请求；填充、无效 lane 或未知字节不可计入。身份字符串必须在输入范围内稳定且无碰撞：call 唯一区分调用，owner 区分执行归属，object 区分 allocation/object，version 区分同一对象的不可变版本。调用方负责核实映射与只读约束；若不能确定，不得提供该输入。不得用默认值替代未知身份。

同一五元组内分别求请求字节总和与区间并集，再跨组相加。输出 `record_count` 是输入区间数，不是指令数或事务数。`repeated_bytes = requested_bytes - unique_bytes`，`repeat_rate = repeated_bytes / requested_bytes`；空输入比率为 JSON null（NA）。不得跨组先求地址并集。执行：

```
python -B outputs/expert-rule-todo4-20261106/repeat_metric.py outputs/expert-rule-todo4-20261106/example.json
python -B -m unittest discover -s outputs/expert-rule-todo4-20261106 -v
```

## 手算及结果

- `[0,10), [5,15), [15,20)`：请求 10+10+5=25 B，并集 `[0,20)` 为 20 B，重复 5 B、20%。`example-result.json` 与之相符。
- 六条相同 `[0,10)`，分别改变 call、owner、route、object、version：六组各 10 B，汇总请求和唯一量均 60 B，重复 0 B。
- 两组独立实验都请求 20 B：`[0,10), [10,20)` 唯一 20、重复 0；`[0,10), [0,10)` 唯一 10、重复 10。这说明总请求量不能唯一推出重复量。
- 空输入返回 NA；不完整或未知覆盖、非只读、错误路径、未知身份及无效区间被拒绝。5 项离线单元测试通过。

本工具无法核实输入覆盖声明、有效 lane、事件归属或版本。不能从这些结果推断 HBM 流量、可省字节、性能收益、时序复用距离或不合理重复；也没有专家阈值。真实 Triton trace 仍不满足接入条件；下面另记录随后完成的 Ascend C 正控。

依据：`docs/专家规则体系-TODO1-问题证据定义-20261105.md` P04、`docs/专家规则体系-证据与建模TODO-20261105.md` TODO4，以及 `docs/customer-rounds-1104-development-20261105.md` 的 DSQ 开发案例；后者并不证明该输入已可从原始记录获得。

## Ascend C 单 block 实机正控（2026-11-06）

针对 TODO4 的实机正控：同一目标采集的两个 GM→UB 源请求各 256 B，范围完全相同。因此 `B_req=512 B`、`B_uniq=256 B`、`B_rep=256 B`、重复率 `50%`。这是该正控定义范围的请求重复率，不是 HBM 重复流量、可省字节、加速量或专家阈值。

采集为 A5_1 950PR device 6，单 AIV block、一个 group，目标 `resource_probe_kernel<1>`，一次目标采集，kernel replay、warm-up 5；宿主程序执行六次调用，工具在跳过五个 kernel 后采集目标一次，不能把六次合并计数。源码 `probe.asc` 在初始和一次循环中各执行一次 256 B 的同源 `load_group`；宿主输入 `x[32:96]` 在调用中未写入，并在运行后验证输入不变、输出及 guard 正确。源码 SHA256 `e75b216cdff5d1c3861d7448c5e40febadad614f903a83364aa1209f23ade146`；采集二进制 SHA256 `ef2f063caf4c6831c37da3b5e30719c6eecd4462df6c44e1ee7a6c386fc59743`（来自同次独立解码结果）。

保留的同次 `MemoryChart.bin` 为 224 B、4 条 56 B 记录，SHA256 `e4f0334c4d19699651195f521a4680097e3d808785d271f9bdb850356c1bd108`。远端同次两份文件哈希相同，仅使用其中一份，未重复计数。`dbi_defs.h` 定义 pack(4) 的六个 uint64、两个 uint16 和两个 uint8；类型映射 GM=6、UB=4。独立读取确认两条 GM→UB 记录均为 block 0/subblock 0、源地址 `19792499048576`、源和目标大小 256 B、PC 分别为 1004 和 1160；另外两条是 UB→GM 写入，排除在本指标外。源地址与同次 `profile-output.json` 的 input 地址一致。128-float 输入分配中切片偏移为 128 B，故两个区间均为对象内 `[128,384)`；同一 call、owner、route、allocation 和不可变版本归为一组。工具日志 processedRecord=4、output=4、dropped=0，且源代码独立预期两读两写与记录数一致，支持该特定正控的覆盖；不能将此证明外推到其他 kernel 或一般采样。

已保存一份原始文件、同次日志、输入信息、工具 CSV 和此前独立解码，以及 `control-input.json` / `control-result.json`。本地 `python -B outputs/expert-rule-todo4-20261106/verify_control.py` 重新核对固定哈希、源码、记录、地址、owner、日志和计量，并生成这两个 JSON。该脚本只接受这个固定正控，不是通用原始 ABI 解析器。

3B 的真实 Triton 和 Router 样例仍为零记录；此正控不代表它们或 TileKernels 专家样例采集通过。程序也无法单靠 `coverage` 字段证明覆盖。此次仅对远端执行只读文件获取与哈希核对，没有执行 NPU 任务或远端写入，未修改主 TODO。

