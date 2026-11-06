# TODO 3B · A5 真实 Triton 地址记录能力核验

## 结论

**当前仅局部通过。** Ascend C 正控与一个 TileKernels 专家样例已成功留存原始记录，TODO 4 仅准入 B-H 经独立核验的只读输入范围。真实 Triton 端仍未通过。首轮两个真实 Triton 单 AIV kernel 完成了正确性检查并生成 Default 表，但四次 `MemoryDetail` 的解析器都收到零地址记录。Router 的无钩子对照和后续带钩子复采也为零。这两个 Triton 样例无法用本轮数据计算重复率。

## 后续正控与 Router 复核 · 2026-11-06

在原物理卡 6、CANN 9.2.0、`msprof op` 26.2.0 / `884ac969…` 上，使用既有 Ascend C `resource_probe_kernel<1>` 的单 block 测试。该 kernel 每次从相同输入地址搬运两次、每次 256 字节，并有两次输出写入；全部 64 个 FP32 输出逐位通过参考检查，输入与输出保护区保持正确。无留存钩子采集得到 `receivedPacket=1`、`processedRecord=4`、`output num=4`；目标二进制 SHA256 为 `ef2f063caf4c6831c37da3b5e30719c6eecd4462df6c44e1ee7a6c386fc59743`。这证明此正控样例可以产生记录，不证明其他 kernel 可以。

相同二进制的带钩子复采保留了 `MemoryChart.bin`。按固定工具源码的 56 字节 `MemRecord` 格式独立解码，4 条记录与解析器数量一致：两条为输入地址上的 GM→UB 256 字节，另两条为 UB→GM 8 和 256 字节，block/subblock 均为 0/0；256 字节输出地址与同次程序记录一致。工具留下两份内容相同的文件，均保留，SHA256 `e4f0334c4d19699651195f521a4680097e3d808785d271f9bdb850356c1bd108`。这只验证该单 block 正控的生产、留存和所列访问，不证明其他输入、kernel 或丢失情况。

随后按原尺寸重采 Router：目标 `_router_topk_kernel`、32 block；输入 SHA256 `fc41f8f8f8e0d0b5214adaedb56a145cce19312213b99be4ab30e44504673a77` 与采集二进制 SHA256 `6346e1225df0d50dfceeb12daf028bb3159783d502da02ebc68312897ab92702` 均与此前一致，输出比较通过；解析器仍为 0 包、0 记录，未留存 `MemoryChart.bin`。按既定分支停止专家地址批量采集。该对照支持继续排查 Router/Triton 的插桩与传输差异，但不能将失败归因于某个原因，也不代表所有 Triton kernel 都不支持。

新增原始记录位于远端 `/data2/lyuze/expert-rule-todo3b-20261106/control-ascendc-20261106/` 和 `/data2/lyuze/expert-rule-todo3b-20261106/router-after-ascendc-positive-20261106/`；解析结果为前者 `run-02-retain/independent-decode.json`。同批证据已打包回传 [followup-ascendc-router-20261106.tar.gz](followup-ascendc-router-20261106.tar.gz)，两端 SHA256 均为 `927e374f1adcf2503132a5c32e2fa1e083ca406e1f19a506590dad7b6ec1c182`。原失败批及原 `verification.json` 未覆盖。

## Router Python 栈对照与单个专家样例

使用 Router 的 `/home/lyuze/.venv/bin/python`、torch `2.10.0+cpu` 和 torch_npu `2.10.0.post4`，复用前述 Ascend C 正控的 host 二进制、device 二进制、输入合同和卡 6。实际加载库记录表明 `libtorch_npu.so` 来自该 venv，`libascendcl.so`、`libruntime.so`、`libnnopbase.so` 和 `libacl_op_compiler.so` 来自 CANN 9.2.0。该栈的完整输出检查通过，同次留存 1 包、4 条记录；原始记录经独立解码与预期地址及数量一致。这缩小了后续排查范围，不能仅据此断定 Router 零记录的原因。

独立验证了一个真实 TileKernels 专家样例：mHC expand，输入 BF16 `[512,4096]`，输出 `[512,4,4096]`，56 个 block。输入、生成源码、host/device 二进制与 TODO 5 的 B-H 准入一致；卡 6 上从新鲜哨兵单次调用的全部输出逐位相等，保护区和输入检查通过。MemoryDetail 采集捕获并留存 56 包、2,048 条记录：1,024 条 GM→UB 和 1,024 条 UB→GM；采集二进制 SHA256 `b0f9e076e7441ba6f4d3265d0257ad91614f84abfaae46bd7ab36de6d035ea16`。

对照实际生成源码独立枚举 512 个 token、每个 token 的两个 2,048 元素分块：1,024 次 4,096 字节输入搬运的地址、大小和次数全部匹配。1,024 次输出搬运的起始地址和次数全部匹配。二进制记录本身只包含汇总长度，不包含输出跨行 stride；将其与同次捕获的 2,048 条 debug 事件按执行归属、PC 和源/目的地址逐条关联后，依据 `nBurst=4`、每段 4,096 字节、目的 stride 8,192 字节展开，4,096 个预期输出段地址全部匹配。**工具仍提示超过 108 sub-block 可能丢失；上述检查仅说明此例的这些预期地址与次数未发现缺失，并非所有字段、执行归属映射或其他样例都已验证。**

该专家案例通过不能替代 Triton Router：Router 仍为零记录，整个 3B 的双端地址能力尚未通过。两个成功正控和专家样例的设备日志也出现 `prof_aicpu_grp` 查询及 profiling 初始化错误，因此该错误不是这些成功样例的必然阻碍；它是否影响其他配置仍未知。

新增机器结果位于远端 `control-ascendc-20261106/run-03-router-stack/independent-decode.json` 和 `expert-bh-20261106/run-01/independent-coverage.json`。含源码、运行脚本、编译产物、原始采集与设备日志的[后续证据归档](followup-stack-expert-20261106.tar.gz)已回传，两端 SHA256 均为 `1f75fb086f1395e432a3cc26f536822bbdc5a95b1be5b30dc66244b8f6352d4d`。本轮不重复原尺寸 Router，也不开展专家批量地址采集。

首轮 Triton 试采结束时尚未采专家地址。后续正控与 B-H 补证后，B-H 的固定源读范围已经进入 TODO 4。Triton 地址计量及未经覆盖验证的专家批量采集仍未准入。[独立审核](../../docs/reviews/专家规则体系-BH计量与P05预审-20261106.md)

## 现场环境与源码

- A5_1 `tritondev_1`，CANN `/home/pkg/cann920/cann-9.2.0`，`msopprof 26.2.0` 构建 `884ac969494a186a9c63ac45c4c39ad7289b3215`。客户侧执行采用 `/home/lyuze/.venv/bin/python` 3.11、torch 2.10.0+cpu、torch_npu 2.10.0.post4 和该环境的 Triton。Tensor 布局和地址在每次调用的 JSON 中记录。两种 PyTorch 环境的证据单列。
- 使用物理卡 6，950PR，总线 `0000:81:00.0`。每次采集前 `npu-smi` 显示无设备进程，结束后也无进程。应用预热 5、工具预热 5、kernel replay、skip 5、采集 1 次。各次原始进程日志和 DeviceProf dump 保存在 `evidence/`。
- `msprof op --help` 列出 `MemoryDetail`，未列出导出原始动态地址记录的开关。源码检出与工具构建同一提交。`DataHandlerOf91095::ParseMemoryChartData` 在读取 `dump/MemoryChart.bin` 后调用 `RemoveAll`。`MemoryChartMetrics::PrintMetrics` 可打印解析计数和错误，`Dump` 在记录非空时写文件。源码快照见 `evidence/source-excerpts/`。[官方工具说明](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910/devaids/optool/docs/zh/user_guide/msopprof_user_guide.md)

## 采集和独立对照

| case 与采集 | 输出精度 | 目标与 block | `MemoryDetail` | Default 的 GM→UB 与 MTE2 指令 |
|---|---|---|---|---|
| 既有 Triton fused softmax `[128,1024]` FP32，MemoryDetail + Default | 全输出通过，最大误差 `7.45e-9` | `_softmax_fused_kernel`，56 | 收到 0，输出 0；提示超过 108 sub-block 可能丢数据 | 519 KiB，440 条 |
| 同 softmax，MemoryDetail 单独采集 | 全输出通过 | 同目标 | 收到 0，输出 0；同样有 sub-block 警告 | 未显式请求 Default；同次 Memory.csv 已生成，519 KiB，440 条 |
| 客户 Router round 2 的 case-13，`[251,256]` BF16、topk 4，MemoryDetail | 两个完整输出通过对应参考检查 | `_router_topk_kernel`，32 | 收到 0，输出 0；未出现超 108 的警告 | 未显式请求 Default；同次 Memory.csv 已生成，133.5 KiB，160 条 |
| 同 Router，MemoryDetail + Default，外部保留钩子关闭 | 两个完整输出通过对应参考检查 | 同目标 | 收到 0，输出 0 | 133.5 KiB，160 条 |

上述 PMU 是工具报告的通路累计量与指令计数，用于证明目标确有可观测搬运。它们与地址事件使用不同口径，不能作为逐条地址完整率的分母。两组 case 均使用固定输入和原尺寸。Router 源码只读复制自客户归档，shape/dtype 保持原 case，输入按固定种子新生成，不能宣称输入与客户历史执行逐位相同。

softmax 的 profile `dump/aicore_binary.o` SHA256 为 `4974dcb3356738fd198a3fdad767a4c42e376191f2d3eb9daf019d3f462a54bd`，与本次 Triton 编译缓存的 `.npubin` 一致。Router 的采集二进制 SHA256 为 `6346e1225df0d50dfceeb12daf028bb3159783d502da02ebc68312897ab92702`。两者属于本次真实执行的目标 kernel。源码、输入哈希、缓存、profile 及逐次输出记录在 `evidence/`。

`droppedRecord=0` 是零个收到记录时的工具字段，不能解释为覆盖完整。实机日志还出现 `prof_aicpu_grp` 查询失败与 profiling 初始化失败，但现有证据不足以确认它就是地址记录为零的原因。不能把 56-block 警告当作全部原因，因为 32-block Router 也收到零记录。进一步应确认该工具构建的实机插桩启动链、Triton 编译产物与采集服务兼容性，再复测原尺寸 case。

## 留存方案与局限

`retain_memorychart.so` 通过进程级 `LD_PRELOAD` 拦截 `unlink`、`unlinkat`、`remove`，仅保留本批输出根下 `dump/MemoryChart.bin`，并记录调用。它不更改工具安装或 kernel 源码。隔离样例对 Python 删除和源码相同的 C++ `std::experimental::filesystem::remove_all` 两条路径均验证了文件保留，非目标文件正常删除。没有抢拷即将删除的文件。

首轮只验证了删除拦截，Triton 实机采集未生成地址文件。后续正控和 B-H 对留存副本做了原始字节、解析日志及独立请求枚举核对，范围限上述成功样例。Router 的无钩子对照同样为零，后续仍需核验实际指令与启动路径。

## 路径与复现

远端目录 `/data2/lyuze/expert-rule-todo3b-20261106/`。完整证据压缩包 SHA256 `69f3b24b5e644b773bd31359741baabe4d7d66fbf2980aa344964bfe08f1d65e`，同一包已校验回传并展开到本目录的 `evidence/`。原始客户路径 `/data2/lyuze/customer-optimization-1104/data/` 只读，源码副本和编译缓存留在实验目录。

复现采集脚本在远端 `run_capture.sh`。例如 `bash run_capture.sh router fresh-router retain`，或用 `control` 关闭钩子。脚本要求新输出名、检查卡 6 空闲，且先由使用者确认当前排队状态。日志中保留完整命令对应的工具选项。之前首次 Triton 启动因 GCC 15 构建的 launcher 载入旧 libstdc++ 缺少符号而失败，已仅在本轮进程前置 `/usr/local/lib64` 修复，原失败日志保留。测试用的删除拦截 payload 已清理，原始采集和失败记录保留。
