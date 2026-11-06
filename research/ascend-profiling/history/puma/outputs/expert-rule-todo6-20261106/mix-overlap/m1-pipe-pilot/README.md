# M1 PipeTimeline 可辨识性试采

当前结论：**可准备一次受监督的 M1 PipeTimeline 试采，实际支持、角色覆盖和跨角色时间对齐尚未验证。** 该次采集用于决定混合执行时间线是否具备进一步研究的条件。即使采到 Cube 和 Vector 两类事件，也先只报告各通道记录和原始区间，不计算跨通道重叠或客户 threshold。

## 本地依据

- 已验收 M1 是 950PR 卡 6、CANN 9.2.0 的单次原生混合开发对照。普通 trace 识别一个 `quant_group_matmul_custom` 的 MIX_AIC 计算任务、8 AIC / 16 AIV。Default 的 `OpBasicInfo.csv` 为 `mix`，且 Memory 和 Pipe 表中有 24 个角色键。普通 trace、Default 和本试采各属不同调用，不能按时间戳拼接。
- 原现场 `collect_site.py` 的 Default 入口使用 `--replay-mode=kernel --mstx=true --mstx-include=cold_call --launch-count=1 --warm-up=5`。`PACK_STAGE=default` 使已审原生程序先进行 5 次应用预热，再对 `cold_call` 范围执行目标调用。此前的完整输出、guard 和设备身份用于定位与准备，不自动代表新采集通过。
- 原 host 程序 `grouped_matmul_after` SHA256 `a51bceeb7fb26469a6d1b02def3d8bcc1bae9c1563992f35a52e97ceabe7cfb8`，对应源 `grouped_matmul_custom.asc` SHA256 `7971c9d871e9c8c1a85cb199c320c591a37f1ab3f08c419d8276cac0dc9e983f`。已验收 Default 中 `dump/aicore_binary.o` SHA256 `050083670df2761eca6e41cefa697c9a4a172a6d2bef18cd3df0946db3c4ae93`。具体目标、输入和完整性证据见 [M1 现场](../../../expert-rule-todo5-20261106/m1-native-profile-site-20261106/RESULT.md) 及其现场归档的 `expected-hashes.log`、`run-cases/b2/result.json`。
- 固定本地 `msopprof` 源码提交 `a41d46ad6ec5233d352e91495963e036aba8193e` 在 `arg_checker.cpp:73` 列出 950 对 PipeTimeline 的支持，`:384–385` 明确 950 的 range replay 不支持 PipeTimeline。其用户指南“Pipe流水图”说明该功能基于采样，最多展示 6 个核的数据。这里的源码与 A5 采集器 build `884ac969…` 并非已证逐字节对应；实际本次是否可采，以目标机日志和产物为准。该项限制适用于通算融合类型，不应把本例 `MIX_AIC` 仅凭名称等同通算融合。
- 同一固定源码 `biu_timeline.h:26–30,55–65,90–91,106–110` 定义 18 个通道、2 MiB 数据块和三类标签。`biu_timeline.cpp:118–145` 按 `coreId×3+coreType` 分通道累加 cycles，`:25–51` 用频率把每通道的累计值写为 `ts`/`dur`。这里没有发现跨通道共同起点校正，但不排除原始数据或其他层提供同步信息。因此相同频率与同一个 trace 文件还不能证明 AIC/AIV 的时间坐标已经对齐。
- 现有 SwiGLU 单 AIV 真实样本的 218 个 JSON 事件、12 个通道和原始 `timeline.bin.0` 12 个通道可由本目录脚本列出。该样本支持格式检查，不证明本次 M1 的角色覆盖、各通道同步、完整性或最终解析器与本地源一致。

## 一次试采合同

由指定的「评测体系 (2)」线程在独立新目录、现有项目锁及核验过的卡 6/81 映射下操作。准备工作复制已验收的 host 二进制和五个 `input/*.bin`，逐项核验上面 host 哈希与已冻结 `expected-hashes.log`。程序以当前工作目录读取 `input/` 并写 `output/`，故需要预先建立新 `output/` 并复制已验收的 `golden.bin`。输入、黄金输出、二进制和实际加载库身份均须保存哈希；不能覆盖旧目录。按原项目准入要求先做等身份完整输出/guard 检查，配置目标工具版本、卡映射和竞争监督。

下面是**单次采集的参数草案，不是已验收的可直接执行脚本**。`<stage>` 是已检查的新目录，`<capture>` 是该目录下的全新输出路径。单次 PipeTimeline 的目标范围和预热条件沿用已验收 Default，不附加第二个 profiler：

```text
工作目录 <stage>
PACK_STAGE=default msprof op --output=<capture> --aic-metrics=PipeTimeline \
  --replay-mode=kernel --mstx=true --mstx-include=cold_call \
  --launch-count=1 --warm-up=5 <stage>/grouped_matmul_after 0
```

实际执行前核实 `msprof op --version`、固定 host SHA、同合同输入、物理卡映射和 `ASCEND_RT_VISIBLE_DEVICES`，沿用指定线程的锁、连续空闲、过程监督、超时和失败清理。应用中的 `0` 是逻辑设备号，映射以当次证据为准。完成后同时归档实际命令、运行日志、对应进程 maps、每个输出/guard 和精度、全部 `OPPROF` 原始文件、`dump/timeline.bin.*`、`dump/aicore_binary.o`、`trace.json`、`visualize_data.bin`、`OpBasicInfo.csv` 及工具生成的告警或丢弃信息。不同调用的 Default 或普通 trace 不代替该次 PipeTimeline 的身份或时间线。

若 `OpBasicInfo.csv` 的目标、Device、mix 类型、block 数或实际捕获二进制不能绑定本次调用，保留试采状态与文件，并标为目标身份待核。先比对前述已知设备 ELF 哈希，差异须调查原因，不能自行补齐归属。输出精度沿用 M1 上游容差、完整输出有限性、guard 和现场复算；任何异常按原协议停止并留证。该例已有连续工作区复用，仅证明完整分配外 guard，不能把它写成所有内部边界均独立检查。

## 离线检查和后续决定

`inspect_timeline.py <单个 OPPROF 目录>` 列出 OpBasicInfo 原行、trace schema 和角色/pipe 数量、原始 `timeline.bin.*` 分块头中的核心类型和有效长度，以及 JSON 与原始头的通道差异，计算输入文件 SHA256。它对不完整分块、未知 channel 编号及非法长度报错；缺文件报告 `incomplete`。脚本只认已见过的 op schema 和固定源码中的原始块布局，其他格式需重新审计。值很小或 `validLen` 未满缓冲区均不能证明无丢失；原始头的存在也不能证明每一角色有完整事件。

```powershell
python -B outputs/expert-rule-todo6-20261106/mix-overlap/m1-pipe-pilot/inspect_timeline.py <OPPROF目录>
python -B -m unittest discover -s outputs/expert-rule-todo6-20261106/mix-overlap/m1-pipe-pilot -v
```

一次试采的判读按以下顺序进行。

1. **身份。** 检查目标调用、kernel、实际二进制、设备与同次输出。如果未能绑定，产物仅作为工具探索。
2. **角色。** 分别列 `core*.cubecore`、`core*.veccore0`、`core*.veccore1` 的原始头和 JSON 事件数、具体 pipe、缺失通道。比较 8/16 的逻辑角色只用于说明采样范围，不能假定 trace 的 `core` 直接等于原任务的 block。
3. **时间与覆盖。** 保留时间单位、频率来源、各通道 raw 头、validLen、解析警告及结束标记。若没有独立证据证明跨通道起点、事件定义和采样丢失情况，继续只报告每通道的局部事件范围与数量。`displayTimeUnit` 和相同频率不足以证明共同时钟。
4. **决定。** 两侧均有事件且存在可审计的共同起点、同调用归属及足够覆盖时，再单独设计适用于这一采集范围的重叠计算。缺任一项则保留缺口，混合执行继续使用分别可验证的原始活动或其他可辨识观察；不输出重叠比例。

本目录尚未执行 M1 PipeTimeline，不定义新阈值。原始样本复算结果见 [SwiGLU 检查](swiglu-inventory.json)，合成测试只验证检查器的读取与拒绝行为。
