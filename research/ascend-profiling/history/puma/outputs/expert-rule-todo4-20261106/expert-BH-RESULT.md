# TODO4：TileKernels mHC B-H 实机源请求

## 结果与范围

A5_1 的 950PR device 6 上，一次捕获的 TileKernels `expand_to_mhc_fwd_asc_kernel`，输入 BF16 `[512,4096]`，输出 `[512,4,4096]`：1024 条有效 GM→UB 源记录各 4096 B。`B_req=4,194,304 B`，`B_uniq=4,194,304 B`，`B_rep=0 B`，重复率 `0%`。这些源区间在整个调用内两两不重叠，恰好覆盖 4 MiB 输入。

每个记录按原始 `(blockId, subBlockID)` 分入 56 个 raw owner 组，组内结果见 `expert-bh/result.json`。原始标签到逻辑任务或物理核的对应关系尚未独立确认，所以不把这些组称为已验证的物理核工作集。由于全调用的 1024 个区间本身两两不重叠，任何归属划分下每组重复量均为零，故上述总结果不依赖该映射；并没有将不同 owner 的重叠范围合并。

## 来源和独立校验

- 原始 chart 为 114,688 B（2048 × 56 B），SHA256 `cda38f6beb3b498c5f731b46782b4c7f1bf2fbb6b894928c64ef013b5d365909`。同次远端 dump 和 device 目录的两份 chart 哈希相同；只复制并计算前者，不把同一份数据重复计数。ABI 来自固定版本 msopprof 的 `dbi_defs.h`，pack(4) `MemRecord`，类型 GM=6、UB=4。
- 同次 `OpBasicInfo.csv` 为目标 kernel、56 block、device 6；生成源码 SHA256 `e97ce3d82e2304d05b1298cb742856d979aeb5343b5932232bf0e5f455483c60`；采集二进制及同次应用 JSON 对应 SHA256 `b0f9e076e7441ba6f4d3265d0257ad91614f84abfaae46bd7ab36de6d035ea16`。工具固定 `884ac969494a186a9c63ac45c4c39ad7289b3215`，kernel replay、warm-up 5、skip 5、目标采集 1 次。应用内同次输出通过 8,388,608 元素逐位检查、输入未改变、guard 正常。输入内容 hash `a71adb836103afdfa06e00d457209745dc2369d0734dfb9001811d67377769b6`。
- 同次输入 tensor 地址 `19792499048576`。实际 wrapper 在 BF16 guarded allocation 的 64 元素偏移处建立 tensor，所以 allocation 基址为地址减 128 B。源码只从 x 读取，检查报告 input unchanged；目标调用内按同一只读版本计量。输出分配另立，不并入源范围。
- 生成源码中对有效 block 的判断为 `((w*56+block_idx)/512)<2`，每个有效项从 2048 个 BF16 元素构成的满块进行 4096 B 拷贝；此 shape 正好有 1024 块，无读取尾块或被屏蔽 lane。独立比对原始记录，1024 个源地址恰为 `input_address + i*4096 (i=0..1023)`，每个恰一次，全部落在输入范围内。日志为 56 packets、processed/output 2048、dropped 0，且源码预期和记录逐地址一致；这支持该 case 的覆盖，不证明工具对其他模式全面无损。工具仍给出 sub-block 数限制警告。
- 另外 1024 条是 UB→GM 输出记录，各报告 16,384 B，单独保留，未纳入输入源统计。该路径存在跨距；原始 MemRecord 的单条地址与大小不能单独证明其连续覆盖；此处不根据它推算输出范围并集。

原始 chart、同次应用信息、日志、捕获二进制、源码、collector 的 `independent-coverage.json` 和 `verify_bh.py` 均保存在 `expert-bh/`。运行 `python -B outputs/expert-rule-todo4-20261106/expert-bh/verify_bh.py` 会核验固定证据并生成 `input.json` 与 `result.json`。脚本针对这一已核实样例，不是通用 ABI 解析器。

## TODO4 准入边界

这个具体专家样例已可进入 TODO4 的只读源请求计量和后续条件化比较，提供一个完整输入且零重复的专家观察。它还不是一般专家阈值或 P04 规则：仍需独立的专家任务、不同容量、生命周期和访问形态，尤其需要覆盖**合理存在重复**的案例，才能研究何时重复可以接受、何时可比较。原始 owner 到逻辑任务的映射亦需另证。

本结果不代表先前真实 Triton/Router 样例通过采集，不等同于 HBM 字节、可省字节或性能收益；一次固定 case 无法建立阈值或诊断准确率。本次仅通过 SSH 只读取得和核对文件，未使用 NPU、未远端写入，未修改主 TODO。
