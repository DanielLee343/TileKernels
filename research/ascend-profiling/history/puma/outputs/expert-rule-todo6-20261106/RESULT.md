# TODO 6/7 候选卡预发布包

本包供审阅和离线试算，**不是 TODO 6/7 完成，也不是客户规则**。10 项登记：9 项默认参考不足，P04 一项固定样例计量；0 项已接入的旧合同判定，0 项新平台客户阈值。P01–P10 的对象、公式与辨识条件以 TODO1 为准。

| 卡 | 观测与依赖 | 当前可用范围和缺口 |
|---|---|---|
| P01 | G；G/Q 须已知合法访问 Q | 参考不足；不能将输入大小视作通用 Q |
| P02 | b=G/N，N=0 为 NA | 参考不足；均值不含请求分布，stride/tail 影响可比性 |
| P03 | A、G、N；b=G/N，τ=A/N，BW=b/τ | 参考不足；三项候选关系未校准；代数量不重复计分 |
| P04 | 同 call/owner/route/object/version：请求区间总长减并集；重复率=重复/请求 | **仅固定 B-H 输入测量**，不作性能阈值；覆盖声明和只读身份依赖独立证据。owner 不映射物理核；此例全范围互不重叠使结果不依赖映射 |
| P05 | W=Σ主存写 KB×1024；R=128×ceil((offset+L)/128)，W/R>1 | 历史实验仅限旧 950PR/0D/CANN 9.2.1 合同；默认 CLI 未接入判定。9.2.0、Cube、混合、客户均无可迁移阈值 |
| P06 | V、A、A3、wait 联合观察 | 参考不足；多次 replay 活动不能算同窗口重叠 |
| P07 | 逐行时间及活动分布 | 参考不足；活动不等于有效工作；旧 Engram 对照反而较快 |
| P08 | 官方读事件命中数/六项总事件；零分母 NA | 参考不足；需工作集和复用机会，不能把事件比当字节命中比 |
| P09 | AIC/AIV 分侧活动及等待 | 参考不足；角色、依赖和同调用时序缺失，不能设 1:1 |
| P10 | 计算构成；有有效工作 Q 才研究 Q/V | 参考不足；活动比例无法识别额外计算 |

## 证据数量和范围

P04：一例 TileKernels B-H、一次目标捕获，1024 条 4096 B 输入请求；请求与唯一量各 4 MiB，重复 0。仅此输入，不包括输出；工具有 sub-block 警告。单例不是专家阈值。TODO4 另有单 block 正控，不能充作独立专家。

P05：冻结后 BF16 GELU 1 个任务、FP32 mHC head 2 个 shape（同一算子族），各 3 次；BF16 和 FP32 额外写各 3 对。复采不是新任务或新机制。阈值 1 是历史实验参考，不是硬件极限。Triton CANN 9.1 尾块是跨合同迁移反例。新 9.2.0 Default 25 次是 7 个任务的开发采集，19 次结束时未标记、6 次可能干扰；不形成新阈值。客户预检 124 份 Default 身份或环境未知，0 份准入；另有 3 份独立 native 9.0.0 不可算入该 124 份。

## 使用与状态

在本目录运行：

```powershell
python -B cards.py fixtures/bh.json
python -B cards.py fixtures/p05.json
python -B -m unittest discover -s . -v
```

P04 固定从相邻 TODO4 原始 `input.json` 读取，核对 SHA256 后复用其区间计量代码；不是通用原始 trace 解析器。P05 fixture 是人工构造的测试数据，三个身份哈希为占位符，绝非采集证据。其他卡返回 `reference_insufficient`；已知合同冲突返回 `not_applicable`；P04 返回 `measurement_only`；P05 始终返回 `reference_insufficient`（已知平台或合同不符时返回 `not_applicable`）。这些结果不表示可节省字节、速度收益或无优化空间。

## 历史 P05 与新卡的接入边界

历史实验的原始归档和 [独立验证脚本](../../experiments/profile-checklist-4-v2-20261105/verify_write.py) 保留了 Memory、OpBasicInfo、trace、合同和文件清单，并核查任务和输出。该脚本对专家样本核对上游源码哈希；当前审查未找到逐次实际采集二进制与 profile 的完整直接绑定。不能用自声明的摘要代替绑定，所以本包不将这些记录自动升级为可判定输入，也不改变历史实验原结论。

P05 默认 CLI 不读取用户声明的行或文件作判定；即使提供格式正确的摘要、伪造绑定或变造文件，仍返回 `reference_insufficient`。`p05_formula` 仅供程序化单测数学：输入为合成行和地址参数，返回 W、R、比值和差额，不产生阈值判定，不验身份，也不作为 CLI 路径。fixture 的哈希是占位符，不是证据。若未来逐份证明实际二进制、采集绑定、原表和完整合同，可另行审核并接入；不推广旧阈值。


## 固定来源 SHA256

- TODO1 定义 `0c3543fe9820585bf00ce17701d0e42e30a94346e884a039eba7fb1900a0817f`。
- 历史卡 RESULT `853075062c14f92609bb3396d5b45ae742616a031add8ad49931cfca8faf3066`。
- P05 冻结定义 `9966913c05aa3202d58afb90e272749722ed503df79c119cafab37ad4cd8ebfe`。
- B-H RESULT `8831bbac112e9932cea6b87c914e5d56ec4e864955cde9a79573d1c19dc02edd`；输入 `cdd36cdd76a08b92b8aab1136461467e41164617b031aa7ef44556fa6b01886b`；原 chart `cda38f6beb3b498c5f731b46782b4c7f1bf2fbb6b894928c64ef013b5d365909`。
- TODO5 分析 RESULT `3d0f7cb4b1c935b7b748d23752ed2a3cecf2262a559068b7ea9bda49e68918f3`。
- 客户预检 `286a75811702d35361a69fa5bb6e815bdb781fade617092061ca620032ef9cef`。

独立审阅、适用条件和真实身份核验、跨平台验证、统计校准、客户验证均未完成。未采新 profile、未调用 NPU、未修改历史卡或主 TODO。
