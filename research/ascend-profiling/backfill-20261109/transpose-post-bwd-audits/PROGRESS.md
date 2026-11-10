# 专家 profiling 缺口补采进度

最新复核 705 个 hidev 采集窗口：697 个解析健康字段无错误、8 个 Hash 待核。TileKernels 主归档 720 个已对账、40 个不适用、260 个待核（含原有 13 精度标签）；DeepGEMM 原版 80 个已对账、66 个不适用、8 个待核。台账 SHA256 `e414c884f002d48208bbbd1c16973095b93a4eb67eaea45bde0518f4d917ca93`。采集仍在串行进行。

`quant_batched_transpose_weight_sf-01` 的两块输出共 2,048 B，`mhc_post_bwd-01` 的四块输出共 6,594,560 B；两例的应用重放、输入／源码、输出地址、向量核搬出请求及 CSV 均已逐项核对，漏记录、重复记录、错误 CSV、非法输出别名等反向测试通过。transpose 另核对每个应用进程的指针表，并通过指针表篡改反向测试；其余同类 case 已排队逐项核对。这里只说明向量核搬出请求字节，不代表物理主存写字节。首例证据包 SHA256 `18811f8aa7c8c44833df8a13430c5a3f5267422bc1b75345151065edc4575fe6`；两个完整批次原始数据在各自队列结束后归档。

`mhc_pre_split_mixes_bwd-01` 解析器报告 33 条丢失和 3 条 memoryCorruption，待核。`mhc_multilayer_recompute-01` 因采集适配脚本提前求值不存在的默认路径而未启动，旧日志保留；同源的三个脚本已在新采集前修正并记录哈希，multilayer 已排新 attempt，尚无重测结论。`presplit-fwd-01` 的旧 metadata 无 case 字段，现改为核对原计划及旧输入／源码，9 个应用进程身份通过；但预期约 48 条搬出记录只看到 5 条，虽解析汇总报告零丢失，仍按记录不完整待核。

mHC fn/normw backward 20/20 已对账，1,516 文件和 160 份 CSV 两端逐项核验；归档 SHA256 `094b2950fc4f8f2e5c9fad1ecb9dbec5c5f10f504353f9c2a03352b38e2ddae3`。最新 702 个 hidev 窗口中 694 个解析健康字段无错误、8 个 Hash 待核；主归档为 717 已对账／40 不适用／263 待核。台账 SHA256 `8ff353b3ec3f9b8869221e9ef417e91a386b22c207e58444ac5f1c4271754469`。transpose 首例采集中，尚未确认身份和字节。

刷新并核对 697 个 hidev 窗口：689 个解析健康字段无错误、8 个 Hash 待核。主归档当前 712 已对账／40 不适用／268 待核（含原有 13 精度标签），mHC fn/normw backward 15/20 已通过；新增原始数据待整批归档。台账 SHA256 `6b38c398b6b8662a943ee6767b7e2f6fedae324904f64ea2e7978bc53731866a`。

已复核 692 个 hidev 窗口与同一索引的解析器检查：684 个无所查错误、8 个 Hash 继续待核。TileKernels 主归档 707 已对账／40 不适用／273 待核（含 13 原精度标签）；mHC fn/normw backward 前 10 例通过，批次仍在运行，原始包待批次结束。台账 SHA256 `c736f5742856152543a984f578f231a337c199431292988ec0662ec9b51280d5`。

mHC fn/normw backward 已完成 7/20 例身份、逐核字节对账；首例反向测试通过，批次继续。RoPE 前 21 窗口已完成，11-K 的监控查询失败已保存，剩余窗口排在其他队列后用 guard v7 续跑。

guard v7 额外完成一次 hidev 实机只读进程查询，识别返回格式并通过；这只是查询验证，不等同于完整 profile 期间上板验证，重新采集仍在队列中。

RoPE 11-K 采集时第 46 次 `npu-smi proc-mem` 查询返回码 0 却输出无法查询；guard v6 按设计终止本任务，原失败 attempt 保留。guard v7 将无效查询视作失败并在原 3 秒时限内最多重试，连续无效／未知 PID／超限仍停止；本地与服务器模拟测试通过，设备试采尚未执行。RoPE 剩余窗口已排在其他独立队列后，11-K 首个新 attempt 通过完整审计才继续。前 21 个通过窗口及失败尝试的 1,627 文件、168 份 CSV 已两端核验并同步 `a3a60617`，部分归档 SHA256 `2ec74f6254b670c8c7a79858ce8216a9fded0275e6f9c91eb84646f914cb6d71`。mHC fn/normw backward 前 2 例已完成审计，批次继续。最新台账 699 已对账／40 不适用／281 待核，SHA256 `bd3ee70dc24f621af71ba2517bdd431ed72b6f64a33a84856bd5fe96d4abce51`。

刷新并核对 677 个 hidev 采集窗口：669 个解析健康字段无错误、8 个 Hash 待核。主归档 692 已对账／40 不适用／288 待核（含 13 原精度标签）；台账 SHA256 `80080c719df6488c155ff8063c4147846319f64bc856d1ad9f34b47cdaec1852`；RoPE 原始包尚待本批结束。

早期 RoPE 试采在上板前发现沿用了旧脚本的冷缓存／共同 MSTX 范围文字；已修正为 application replay 不自动清 L2、Q/K 分别设置范围，未更改 kernel。旧版本尚未运行；校验后的新 harness 已同步 `9c89d584`。

早期 RoPE `rope-supp-01` Q 应用重放试采已排在 Hash 对照后：保留原输入生成器、原始源码、历史 metadata 和原校验，单独标记 Q/K 的 MSTX 范围、每个应用进程的设备参数与源码。试采和身份核对尚未上板，不能计入已对账；原始 range 重放仍分开。字节原样的 9 文件 harness 已归档校验并推送 `5713f665`。

早期 118 个待核条目的 metadata 分布在两种目录结构；全部找到了输入描述及源码摘要，其中 115 条 metadata 包含所有列出输入的 SHA256，另 3 条不能仅靠该文件完成全部输入摘要对比。仅为资料存在性盘点，不认定与主归档同一个 case；见 `early-metadata-inventory.json`。

刷新并独立核对 667 个 hidev 采集窗口：659 个解析健康字段无错误、8 个 Hash 继续待核。RoPE Q02 的旧慢审计 `audit_failed` 与成功复审都在索引中保留。主归档当前 682 已对账／40 不适用／298 待核；台账 SHA256 `c2bd1057705102de137373c80631d6120ce1aad0ec4f50df642d9bf812b77476`；RoPE 原始包待本批结束后归档。

8 个异常 Hash 的设备反汇编各有 1 个 `MOV_UB_TO_OUT` 静态指令，已记录的搬出 PC 与该指令一致；这不能排除同一 PC 的动态重复执行被丢弃，因此仍待核。证据保存在 `hash-isa-coverage.log`。

对台账补充独立解析器门禁复核：带丢记录或缺解析汇总的当前采集路径不能标已对账，并用故意篡改状态的测试确认会拒绝；异常与不同重试路径分别处理。代码与证据已推送 `800b9eb0`。

RoPE Q02 采集完成后，原地址审计对 256,128 个非连续区间做反复线性查找，单核持续运行超过 7 分钟。改用等价二分查找：首例新旧审计输出逐字段相同，随机及边界对照测试通过，Q02 删记录／重复／CSV／非法别名反向测试通过。已有意停止旧慢审计并保留其 `audit_failed`，独立复审 Q02 通过 65,568,768 B 后继续 RoPE 队列；控制进程保留原队列次序。

Hash 丢记录对照试验已排队：使用历史 hash-15 输入与源码，以应用重放观察解析器记录是否仍丢失；逐进程核对身份并保存健康摘要，不自动认定字节对账通过，试验与旧 kernel 重放分开。尚未上板，排在 extra6 重试批之后。

cast-and-back 20 例应用重放已完成，1,516 个文件和 160 份 CSV 副本两端逐项校验后推送公开分支 `d7436ff2`，归档 SHA256 `6ce84373deb89bb615c9e24d3373d8a01fcf9a9038c4e356c18f5c0cec5e5c55`。RoPE 已自动接续。663 个 hidev 窗口的索引与解析器扫描对应：655 无所查错误、8 个 Hash 待核；台账复验后 TileKernels 主归档 678 已对账／40 不适用／302 待核，DeepGEMM 原版 80／66／8。台账 SHA256 `81ddfd454dfe5a072ef4fd7913268e2a82262fe3d24a4a43862fdd54b4715eba`。

Hash 丢记录初查：8 个样本的解析汇总均含 SIMT Load/Store 类型记录，并报告丢记录但没有 overflow 或 memoryCorruption；这只是共同现象，不能证明 SIMT 是根因或证明缺失记录不含向量核搬出。原始解析汇总保存为 `hash-parser-health-summary.log`。

新刷新含 660 个 hidev 捕获窗口，与解析器汇总按索引 SHA256 绑定：652 无所查错误、8 个 Hash 丢记录继续待核、0 缺汇总。台账验证通过，主归档 675 已对账／40 不适用／305 待核，DeepGEMM 原版 80／66／8；新增窗口原始包尚待对应队列完成后归档。刷新脚本现自动运行健康检查，台账构建拒绝与索引不匹配的检查文件。SHA256 `c5fb975f908fd9ca68b14d2ba6599959d7594a31670741a0d329c586d2bd203f`。

进一步检查 DeepGEMM 的 80 个已对账 hidev 窗口及本地留存的 tbe 对账证据 37 个窗口：这 117 个窗口均有解析器汇总且所查健康字段无错误；检查范围和原始状态见各 `*parser-health-sweep.json`。

对 651 个已索引 hidev 对账窗口读取全部解析器健康字段：643 个无已列解析错误，8 个 Hash 窗口有 `droppedRecord`（9–963 条），尽管输出地址覆盖检查通过，也不应直接认定完整。原 Hash 审计未检查该字段，现已在台账按原采集路径退回待核，保留原 audit 和日志。重建并核验台账后，TileKernels 主归档 666 已对账／40 不适用／314 待核；DeepGEMM 原版 80／66／8 未变。扫描是当时的 hidev 索引快照，不覆盖后续新增窗口或全部其他来源。台账 SHA256 `14158d9e752740e1a5bb45bf0f36c544f83f8f0cc9f7fc332906fca959331ec5`。

已为 7 个 `unified-extra6/post-fwd-*-retry` 准备同样的代表试采、逐核审计和反向测试，安排在 finalize 重试队列后，失败即停；这些代码及 finalize 重试均尚未上板验证。27 个支持文件逐项检查提交版本哈希后推送公开分支 `4fe4adaa1992691391b92d219a50bab9289bf987`。

额外准备 4 个 `unified-extra6/finalize-*-retry` 的应用重放：先尝试 13，再检查逐进程身份、逐核地址和字节，并做删记录／重复记录／篡改 CSV／输入输出别名反向测试；只有全部通过才自动采集余例。代表试采及审计代码目前均未上板验证，队列排在冻结旧 REUSE 试验之后；失败即停，归档监控已排队。

scale 转置布局复核的脚本、日志及刷新台账已推送公开分支 `601fcf387359c78db7e781af8752c00e09276408`，远端 HEAD 已核对；新 cast-and-back 原始窗口尚待该批结束归档。

台账最新刷新并核对：TileKernels 主归档 674 已对账、40 不适用、306 待核（含原有 13 个精度标签）；DeepGEMM 原版仍为 80 已对账、66 不适用、8 待核。cast-and-back 已通过至少 9 例，采集仍在运行；其原始窗口将在本批结束后归档。台账 SHA256 `a61251cc0dd0575ec84f421440bd660a18f216a04844af11016802a7f857c994`。

已将 REUSE 时点／区域对比日志及冻结旧采集器重建试验脚本加入支持快照并推送公开分支，远端提交 `7eb06e041a412f0ab21a29f1a2ee492cf630b180`，1,323 个文件逐项复验。重建试验仍在队列中，旧 REUSE 目标时点的完整状态尚未证明。

重新核对 paged sparse REUSE 身份：首例历史 metadata 哈希与新 FIRST 的预热前完整快照一致，冻结的旧采集脚本在 5 次预热之前记录哈希，不能直接将其当作目标调用时的完整输入。按源码和描述符复核，新 REUSE 的 mapping、ranges、physical 和 28 个活动描述符与该快照一致；与新 FIRST 后状态比较，112 个按描述符计算的有效 data 区域一致。原先把 scale 当连续 token 排列得到 12 处差异的判断有误：源码显示每 16 个 token 转置，重算的 1,184 个有效 scale 字节均一致；先前差异来自填充字节。不能据此声称旧目标的完整输入等价；8 个 REUSE 保持待核。比较脚本和日志均保存在 hidev。

四个 paged sparse FIRST 原始采集窗口（512 文件、32 份 CSV）、momentum 第 02 例原失败及复审（153 文件、16 份 CSV）和 1,309 份支持文件已逐项复验并推送公开分支，远端提交 `2631703622e70f3f682693c93bd887e0814d0cc4`。三例 FIRST 的反向测试日志与索引中 SHA-256 逐份核对一致。

台账刷新并复核：TileKernels 主归档 668 已对账／40 不适用／312 待核；DeepGEMM 原版 80 已对账／66 不适用／8 待核。四个分页 sparse FIRST 均已对账，momentum 第 02 例以复审状态回填并保留原失败记录。

Sinkhorn momentum 第 02 例采集与 9 个进程身份检查通过，原审计因行枚举数量超过 100 万而拒绝。按连续维合并为等价地址区间后复算通过，请求 4,096,004,096 B；小例逐地址等价检查及大例删输出／重复记录／篡改 CSV／非法别名反向测试均通过。保留原 `audit_failed`，单列复审记录，余例已按新审计排队。

Sinkhorn step 20 个 case 的原始窗口已在两端复验（1,516 个文件、160 份 CSV 副本）并推送公开分支，远端提交 `35b1002c61fac9739f40e0553933cd892cdf6d7b`；应用重放与历史 Default 分开保存。

Sinkhorn step 20 例全部通过对账，后台归档；已自动接续 momentum。刷新台账并复核 1,301 行：TileKernels 主归档 665 已对账／40 不适用／315 待核，DeepGEMM 原版 77 已对账／66 不适用／11 待核。

追加支持快照至公开分支提交 `90c1da64727d5cc8a2f6909046c7b9b670c1a9f4`，1,280 份文件逐项复验；其中 mHC big-fuse／multilayer／pre-apply 仍是尚未运行的代表试采。mHC pre-apply 原计划有 9 个 case 的历史 default.json 缺失，保持原精度标签，不强行与新 profile 配对。

已将 batched transpose、mHC post backward 与 pre-split backward 待试采适配器及身份检查脚本加入支持快照并推送公开分支，远端提交 `748dc29a52d9eeb8becc7dd0632db95b3b540261`，1,252 个文件逐项复验。这些新代表例尚未上板。

已推送新增 mHC fn/normw 反向适配器和批次自动归档监视脚本的支持快照，远端提交 `2cdbae1657bfeb206b8b0390d3e17fe4873889a5`，1,224 个文件逐项复验。mHC 仍处于排队状态，适配器和候选审计尚未板上验证。

已将 8 个代表／失败采集单元、1,210 份服务器支持文件及当时台账推送公开分支，远端提交 `7c66e0db5a5fe2172d9b4bec1319c7d09082287e`；原始包 624 个文件、72 份 CSV 副本和支持包均逐项复验。台账中 step 首例之后新增 case 的原始窗口需下一批归档。

新一轮台账复核通过：TileKernels 主归档 650 已对账／40 不适用／330 待核，DeepGEMM 原版 77 已对账／66 不适用／11 待核。新增数据包括正在运行的 Sinkhorn step 批次的已完成项；除已打包的代表例，其余原始窗口尚待下一批归档。

分页 sparse FIRST 首例及 Sinkhorn step 首例已回填，1,301 行台账复核通过：TileKernels 主归档 643 已对账／40 不适用／337 待核；DeepGEMM 原版 77 已对账／66 不适用／11 待核。FIRST 的工作区和输出分别为 236,544 B 和 1,024 B，漏记录、重复、CSV 篡改及非法别名反向测试通过。Normalize 第二种尺寸仍有 1 条解析丢记录，不计通过。

Sinkhorn momentum、RoPE Q 和原地量化再转换首例已完成地址对账及反向测试并验收；主台账等待下次刷新。同类其余 case 与三个不同 FIRST 配置均已串行排队，逐组异常即停；代表采集及失败记录的原始包正在准备。

Sinkhorn step 首例在 9 个应用重放进程上完成身份检查，三个输出区域及逐核请求字节对账通过（57,352 B）；删去任一输出记录、重复记录、篡改 CSV 和输入输出别名的反向测试均被拒绝。已验收该例，并在现有试采之后排入余下 19 例，异常即停；主台账尚待下一次刷新。

Engram 梯度 20 个 case 的原始包、更新后的台账和索引已推送公开分支，远端提交 `eb7a5ca0d322182944dd8468c78dbef2697826b6`。两端逐项复验 1,516 个文件及 160 份 CSV 副本；应用重放采集窗口不与历史 kernel 重放混同。

Engram 梯度 20 个 case 均已完成逐地址和逐核请求字节对账，自动原始归档进行中。刷新后主归档为 642 已对账、40 不适用、338 待核（含 13 个原精度标签）；1,301 行台账复核通过。该统计为阶段快照。

已将修正后的 Sinkhorn 等待脚本和检查器、RoPE 与原地量化再转换适配器作为新支持快照推送公开分支，远端提交 `90a6a65929c5558a4d986ee3f1038f5bfdd196c6`；1,179 个文件逐项复验。README 明确标识旧 v7 的两个 Sinkhorn 目标分组有误，保留历史并提示使用 v2。新试采尚未完成。

检查后发现等待中的 Sinkhorn step／momentum 目标分组误写为 `unified-extra`，实际为 `unified-extra5`；采集尚未开始。已按 PID 和命令确认后仅取消本任务的等待器，保留旧目录，并使用正确分组重建串行等待队列；梯度采集中断为零。逐一核对了 step、momentum、RoPE 和原地量化再转换的目标与历史元数据。

Engram 梯度前 11 个 case 已对账；刷新后 TileKernels 主归档为 633 已对账、40 不适用、347 待核（含 13 个原精度标签），1,301 行台账校验通过。RoPE 原地更新首例应用重放试采已排在既有队列之后，采集、身份及地址对账均尚未发生。

已按用户选择继续同步至公开仓库；新增服务器支持快照包含 1,157 份脚本／适配器／历史绑定文件，经逐文件哈希复验，远端分支提交 `bc1e4594cb99082b647b22be31cde6c55df0e934`。该定点快照包含 Engram 梯度、Sinkhorn step／momentum 及 paged sparse 应用重放适配器，不包含运行时和后续产生的原始采集窗口。Engram 梯度队列已确认前 9 个 case，继续采集。

Engram 梯度队列已完成 5 个 case，对应应用重放窗口已入台账；刷新并复核后，TileKernels 主归档为 627 已对账、40 不适用、353 待核（含 13 个原精度标签）。该批新原始窗口待队列结束后归档上传。

已追加本地 948 份审计／采集脚本与阶段文档快照，逐文件校验后推送公开分支，远端提交 `b63556ae6a433d49e087fcf463f89ed6a03e38a5`。它是定点快照，后续新增脚本仍需另行同步；依赖的 profile 数据与服务器运行时分别保存。

`moe_normalize_weight/01` 通过正确性与源码身份检查，但地址解析器报告 `droppedRecord=4`、`memoryCorruption=1`，未通过完整性验收，保持待核。Engram 梯度采用应用重放逐进程验证，首例两个原地输出覆盖和反向测试通过，20 个 case 的队列正在执行；Sinkhorn 与分页 sparse FIRST 的应用重放代表例已在队列后等待。

MoE forward 首例两次正确性通过；生成源码仅路径不同，按历史目录名替换后源码哈希完全一致，但二进制哈希不同并分别保留。两次详细采集分别报告 `droppedRecord=3607/3384`、`memoryCorruption=14/9`，所以仍无法认定地址记录完整，case 保持待核。

普通与 pilot GEMM 新窗口、分页 sparse 失败试采和更新的支持包已推送公开分支，远端提交 `d45c862111fd6de39d0477b75757cbee4de1916d`。原始包 290 个文件、48 份 CSV 副本以及支持包 1,089 个文件均完成逐项复验；分页 sparse 失败记录未计为通过。

四个 M=1 pilot GEMM case 均完成输入／输出及 JIT 身份核对、逐核字节与地址对账，以及漏写、错误 CSV 和输入输出别名反向测试。刷新后的 DeepGEMM 原版台账为 76 已对账、66 不适用、12 待核；12 个待核均为分页 sparse MQA。原始窗口和新增支持脚本尚待归档。

大型普通 BF16 GEMM 已通过逐核字节对账及漏写、篡改 CSV、输入输出别名反向测试，DeepGEMM 原版台账刷新为 72 已对账、66 不适用、16 待核。该新窗口尚待归档。四个 M=1 pilot case 已进入补采与身份检查队列。

K-group 4 例、非分页 sparse MQA 8 例与 randn 两次失败试采的原始包已推送公开分支，远端提交 `7aa6122c209469e7e6f08402cf7440a79d4466b7`；原始包 633 个文件、112 份 CSV 副本和支持包 1,034 个文件逐项复验。randn 的丢记录状态没有被改成通过。

分页 sparse MQA 的复用首例通过数值检查，但历史元数据只保存完整缓冲区哈希，本次哈希不同，无法据此证明历史与本次 metadata 等价，保持待核。FIRST 首例按历史 range 重放试采，`msprof op` 明确报 `MemoryDetail` 与 `--replay-mode=range` 不兼容；无完成 profile，保留日志，不改称成功。kernel 重放是否能保持 FIRST 状态尚未证明。

K-group 四种数据类型和非分页 sparse MQA 8 个 case 均已完成对账并登记，台账复核通过。DeepGEMM 原版现为 71 已对账、66 不适用、17 待核；K-group 其余三种类型各通过漏写、篡改 CSV 和输入输出别名反向测试，sparse 首例还测试了 metadata 篡改。原始数据需后续归档。

MoE backward 20 个 case 的阶段原始包和支持文件快照已推送公开分支，远端提交 `7c556e25ab7744e5e293728eab1785e69966abfc`；原始包 1,017 个文件、160 份 CSV 副本及支持包 977 个文件逐项复验。K-group BF16 已入台账，原始窗口需下一次归档。

K-group BF16 首例通过实际分组输出的逐核对账及漏写、篡改 CSV、输入输出别名反向测试。台账已刷新并复核，DeepGEMM 原版为 60 已对账、66 不适用、28 待核。非分页 sparse MQA 首例身份与 metadata 驱动的输出范围对账通过，校验批次已排队，尚未写入台账。

MoE backward 20 个 case 均已通过逐核字节与地址对账。台账刷新并通过复核：TileKernels 主归档 622 已对账、40 不适用、358 待核（含 13 个原精度标签）；DeepGEMM 原版仍为 59 已对账、66 不适用、29 待核。第二例保留原失败和复审依据，原始数据包正在准备。

MoE backward 第 2 例初次审计错误地把单序列 token 数作为总行数，保留原 `audit_failed`。上游测试源码明确总行数为 `num_seqs × (num_tokens + num_padded_tokens)`；据此更新审计后原始记录重算通过，并对第 1、2 例分别执行漏写、错误 CSV 和输入输出别名反向测试。已记录独立复审状态，其余 case 使用修正后的审计继续采集。

普通与 Paged MQA 18 个 case 的原始目录和新的支持文件阶段包已推送公开分支，远端提交 `a0922132722fd324f668346a931200840b5495c3`；原始包 921 个文件、160 份 CSV 副本及支持包 907 个文件均逐项复验。MoE backward 首例通过对账和反向测试，其余 case 已进入串行队列。

Paged MQA 8 个 case 已按实际上下文长度完成地址覆盖、逐核计数与正确性对账，覆盖 FP8／FP4、两种页布局与不同尺寸；漏写、篡改计数／长度和输入输出别名反向测试通过。刷新并校验台账后，DeepGEMM 原版为 59 已对账、66 不适用、29 待核；新增原始窗口及新适配器仍待归档。[索引](deepgemm-paged-mqa-index.json)

Norm backward 全部 20 个 case 的阶段原始包及刷新后的台账已推送公开分支，远端提交 `b4477e26a1e2e558ef15119d4ae7ee4da14c642a`。包内 1,210 个文件和 160 份 CSV 副本已在两端复验；部分其他新索引对应的原始窗口仍需后续归档。

`randn-04` 试采的结果正确性及种子重复性通过，但地址记录解析统计显示处理 9 条、丢弃 26 条，故不能证明向量核搬出请求量完整；该 case 保持待核，原始 profile 和日志保留。不能仅因 2,048 B 输出覆盖看似完整就忽略丢失记录。Paged MQA 首例身份检查通过，按源码需要保存每行实际上下文长度才能核对输出范围，已安排独立复采。

Norm 累加 9 个 case 已用独立应用重放完成地址及逐核字节对账，刷新台账并通过 1,301 行清单复核。主归档当前 TileKernels 602 已对账、40 不适用、378 待核（包括 13 个原精度标签）；DeepGEMM 原版 51 已对账、66 不适用、37 待核。新增原始窗口仍需后续归档上传。

已推送后续支持文件阶段包，共 864 份脚本／适配器／清单，包含累加应用重放、随机数与 paged MQA 适配器，逐文件校验通过。公开分支远端提交 `e8d9eab30864b8ab5bdc023049125f0989a62143`；它不包含 CANN／Python 完整运行时，也不等同于后续新增原始 profile 已归档。

Engram 正反向 40 个 case 的阶段原始包已按 2,007 个文件及 320 份 CSV 副本复验并推送公开分支，远端提交 `8bd3ae0bc0494f20e2d51a32e6c8ce215ea219a1`；包含实际 mask 证据。Norm 累加独立应用重放队列仍在执行，已完成的 case 通过对账；新采集数据和脚本需后续更新台账并归档。

DeepGEMM MQA 10 个 case 按各行 `end - start` 的实际输出范围完成对账；范围输入的原始字节与历史输入哈希逐例绑定，漏记录、篡改范围／计数和伪造别名的反向测试通过。[索引](deepgemm-mqa-index.json) 最新台账：DeepGEMM 原版 51 个已对账、66 个该字段不适用、37 个待核；TileKernels 主归档仍为 594／40／386。

最新台账：TileKernels 主归档 594 个已对账、40 个字段不适用、386 个待核（含 13 个原精度标签）；DeepGEMM 原版仍为 41 个已对账、66 个不适用、47 个待核。带 mask 的 Engram 正向已全部按实际 mask 对账；Norm 累加首例采用独立应用重放，9 个进程的初始输入哈希和正确性通过、字节对账及反向测试通过，该窗口与历史 kernel 重放 Default 分别标记。逐项台账复核通过。

已上传包含 797 份实际采集脚本、适配器、输入清单和历史身份材料的阶段支持包，远端提交 `ab75a7bd1850a943d66e393b4aec682f13da009d`；包内各文件已按清单复核。它不是完整 CANN／Python 运行时，且新添加的脚本仍需后续快照。

带 mask 的 Engram 正向首例按实际输入 mask 的哈希及非屏蔽行计算应写范围：512 行中 206 行被屏蔽，5 类输出地址及逐核计数对账通过，删各类输出、改计数／mask、伪造别名等反向测试通过；其余带 mask case 已排队。MQA 首例输出是按每行动态范围写入，不能用完整张量大小推断；已安排在不改 kernel 的前提下保存并哈希核对原始范围输入，再做逐行地址对账。

追加上传 `extra-proxy-runs` 下 `unified-extra`、`unified-extra3`、`unified-extra4` 的阶段快照及更新后的台账与索引；公开分支远端提交 `31dcad453fac18f250ee7de37e6c22c1f460051f`。三个包分别含 997／2,512／985 个文件，均完成两端逐文件校验；不包含其后新增或尚未采集的目标。

最新台账：TileKernels 主归档 563 个已对账、40 个字段不适用、417 个待核（含 13 个原精度标签）；DeepGEMM 原版 41 个已对账、66 个不适用、47 个待核。SwiGLU 反向 20 例、无 mask Engram 正向 10 例、非累加 Norm 反向 11 例以及 FP8/FP4 分组 GEMM 3 例已对账，DeepGEMM 新增原始文件逐份哈希已回填。[索引](deepgemm-dequant-mgroup-index.json)

已将实际运行脚本的固定版本及其哈希、与采集 case 的对应说明追加推送公开分支，远端提交 `a3d960cdb3afa53455857eab3fc613d0cf997ef4`；压缩包及其中 5 个脚本的哈希已复核。

追加上传 `deepgemm-runs` 与 `extra-proxy-runs/unified-extra2` 阶段快照，公开分支远端提交 `151f7bb268a48c1c4e9562dc98ea1f911ad0ad7c`。两个包分别含 1,769／3,835 个文件及 312／616 份 CSV 副本，两端逐文件校验通过；快照之后继续产生的文件不在这次包中。

追加上传 `fused-runs`、`topk-runs`、`hash-runs`、`classic-runs`、`mega28-runs`、`unified-quant-runs` 的阶段归档，远端提交 `7ba84ae1d52b71172215533a1f429d7a03b8954f`。均先扫描、在采集端逐文件验包、传输后在本机再次逐文件校验；失败／不完整尝试原样保留。其中 `hash-runs` 快照仅有 18 个目录，MegaMoE 适配试验仍不代表总量对账通过。

已追加上传 `mhc-runs` 的 second／third／fifth 三组采集目录及全部尝试，远端分支提交 `9bc2105dadbafb6e0073a81f3ecc15798bcdaa1e`。快照的 2,421 个文件、400 份 CSV 副本在远端和本地均按清单逐份校验；该快照不代表所有计划中的 mHC case 都已采集。

已将 20 个 hidev reduce case 的完整采集目录追加推送公开分支，远端提交 `7264c20c31cc3c53a1f24409b14f2e8045d9061c`。压缩包包含 908 个原始文件和 160 份 CSV 副本；远端生成后及本地传输后均按清单逐文件校验通过，公开内容扫描未发现私钥或 GitHub token 标记。其余家族尚待归档上传。

最新台账：TileKernels 主归档 529 个已对账、40 个字段不适用、451 个待核（含 13 个原精度标签）；DeepGEMM 原版 38 个已对账、66 个不适用、50 个待核。cast 20 例和 BF16 分组 GEMM 3 例全部通过；DeepGEMM 原始文件逐份 SHA-256 已回填。[索引](deepgemm-bf16-mgroup-index.json)

复核采集包时发现部分派生脚本随包复制了原通用脚本：已有 cast、Norm 反向和 SwiGLU 反向采集的实际专用脚本已在远端 `runner-version-evidence/` 固定副本并记录 SHA-256，包内版本与实际脚本的差异是目标组／case 过滤条件；原始 profiler 命令和数据保留。待运行的专用脚本已修正为复制自身，cast 正在运行的旧版本不覆盖，统一在归档中保留固定脚本与映射。

SwiGLU 反向 5 个代表 case 的原输入、生成源码和输出地址覆盖初核通过；针对其中同时有 5 个输出的量化样本，分别删除每类输出的搬出记录、修改计数、制造输入输出重叠和篡改 scale 形状均被拒绝。其余 case 已排队逐项验收。随机舍入 cast 首例及反向测试通过，余例按输入大小采集；BF16 分组 GEMM 首例通过同类对账，余两例已排队。非累加 Norm 反向首例通过对账；累加场景的重放状态仍待核实。

SwiGLU 正向 20 个 case 全部完成对账。最近一次台账：TileKernels 主归档 502 个已对账、40 个字段不适用、478 个待核（含 13 个原精度标签）；SwiGLU 反向及其他代表 case 按顺序试采。逐项核对脚本通过。

Norm 正向 20 个 case 全部完成地址和逐核计数对账。随后刷新台账：TileKernels 主归档 490 个已对账、40 个字段不适用、490 个待核（含 13 个原精度标签）；SwiGLU 正向队列继续，索引为采集过程中的快照。逐项核对脚本通过。

首批公开快照已推送 `DanielLee343/TileKernels` 的 `expert-profile-backfill-20261109` 分支，远端提交 `ed3b3aa68c8e4bf370de992906cfdc50025ff196` 已核对。包含 5 个 hidev 原始采集窗口及当时的逐项台账；217 个压缩包文件均按内容哈希复核。后续原始数据尚未上传，完整归档任务继续。

最近一次完整台账核对：TileKernels 主归档 479 个已对账、40 个字段不适用、501 个待核（含 13 个原精度标签）；DeepGEMM 原版 35 个已对账、66 个不适用、53 个待核。台账包含采集时刻前已验收的结果，队列继续执行；逐项核对脚本通过。

Norm 正向队列已恢复：第 04 例第一次对账将输出地址表达式中的 `rstd_base` 误认为 `rstd` 输出而停止；修正对目标指针的匹配，并核对 packed scale 的 `out_sf_words` 别名后，6 个已有代表样本的删记录、篡改计数和别名等反向测试再次通过，第 04 例原始采集通过对账。失败日志保留，队列继续。SwiGLU 正向 01、02、07、08 的源码身份、正确性和地址覆盖初核通过，反向测试进行中，尚未全部回填。

DeepGEMM M-group 6 个 case 全部完成输出地址及逐核计数对账，逐份哈希已回填。DeepGEMM 原版现为 35 个已对账、53 个待核、66 个该字段不适用。[索引](deepgemm-mgroup-index.json)

分块反量化 20 个 case 已全部完成对账。最近一次台账：TileKernels 主归档 463 个已对账、40 个不适用、517 个待核（含 13 个原精度标签）。

DeepGEMM 分组 GEMM 首例完整输出地址及逐向量核计数对账通过，并通过删记录／改 CSV 反向测试；其余 5 个 case 已排队。DeepGEMM 原版现为 30 个已对账、58 个待核、66 个该字段不适用。[对账](deepgemm-mgroup-audit.json) · [反向测试](dg-mgroup-negative-test.txt)

反量化早期入口的 3 个 case 均已使用原输入生成方式完成对账；分块反量化队列继续，Norm 正向首例也通过两个输出地址及输入输出不重叠检查。最近一次台账：TileKernels 主归档 453 个已对账、40 个不适用、527 个待核（含 13 个原精度标签）。

DeepGEMM paged MQA metadata 8 个 case 已全部完成原输入／源码身份、输出地址和计数对账，逐份哈希已回填。DeepGEMM 原版现为 29 个已对账、59 个待核、66 个该字段不适用。[索引](deepgemm-paged-meta-index.json)

DeepGEMM paged MQA metadata 首例通过对账及删记录／改 CSV 反向测试：该输入的实际搬出请求为 232 B，工具按 32 B 粒度记录为 256 B，两者不混用。DeepGEMM 原版现为 22 个已对账、66 个待核、66 个该字段不适用。[对账](deepgemm-paged-meta-audit.json) · [反向测试](dg-paged-meta-negative-test.txt)

反量化新入口 17 个 case 已全部通过对账；另 3 个原入口 case 待试采。最近一次台账：TileKernels 主归档 439 个已对账、40 个不适用、541 个待核（含 13 个原精度标签）。

无损分块量化 20 个 case 全部通过对账，反量化队列已接续。最近一次台账：TileKernels 主归档 425 个已对账、40 个不适用、555 个待核（含 13 个原精度标签）。

又核实 3 个历史 FP8/FP4 试点使用 Cube 直接搬出，向量核搬运为 UB→L1；固定源码、模板和原二进制已对照。DeepGEMM 原版现为 21 个已对账、67 个待核、66 个该字段不适用（含 34 个纯 Cube）。[逐例审计](deepgemm-pilot-direct-static-audit.json)

无损量化首例首次身份检查因生成源码哈希不一致停止。定位到唯一差异是断言信息中历史目录 `TileKernels` 改为当前 `TileKernels-private`；旧运行日志证明历史路径，精确替换后整份源码哈希一致，输入、二进制和正确性检查也通过。原失败日志保留；地址对账及删记录／改 CSV 反向测试通过。[源码与记录](lossless-smoke-evidence/) · [反向测试](lossless-negative-test.txt)

每通道量化 20 个 case 全部完成对账；无损量化 6 个和反量化首例已回填，无损量化其余 case 队列运行中，反量化 17 个新入口 case 随后继续。反量化另外 3 个计划 case 来自早期采集入口，仍待单独处理。最近一次台账：TileKernels 主归档 409 个已对账、40 个不适用、571 个待核（含 13 个原精度标签）。

对剩余主归档的 614 个目标扫描历史二进制，发现 20 个 mHC head 反向 case 不含 UB→GM 指令。固定源码、各 case 精度记录及二进制逐一核实：它们使用 SIMT 直接写 GM，不能记作没有主存写入。这 20 个目标该字段标为不适用。最近一次台账：386 个已对账、40 个不适用、594 个待核（含 13 个原精度标签）。[逐例审计](head-bwd-static-audit.json)

8 个 DeepGEMM 稀疏 metadata case 的原始 AIV 二进制没有 UB→GM 指令；其中间接调用已逐一定位到二进制内的调试函数，实际存在 SIMT／标量主存访问。DeepGEMM 原版现为 21 个已对账、70 个待核、63 个该字段不适用（含 34 个纯 Cube）。[逐例审计](deepgemm-sparse-meta-static-audit.json)

每通道量化首例及删记录／改 CSV 反向测试通过；该组已有 4 个 case 回填，剩余队列运行中。TileKernels 主归档最近一次台账为 386 个已对账、20 个字段不适用、614 个待核（含 13 个原精度标签）。

非直接搬出的大形状 FP8/FP4 混合 GEMM 已通过历史输入和生成源码绑定、输出地址与逐向量核计数对账，以及删记录／改 CSV 反向测试；请求搬出 4,718,592 B。DeepGEMM 原版现为 21 个已对账、78 个待核、55 个该字段不适用。[对账](deepgemm-dequant-audit.json) · [反向测试](dg-dequant-negative-test.txt)

预计算 scale 的分块量化 20 个 case 全部完成逐地址及逐核计数对账。最近一次台账：TileKernels 主归档 382 个目标已对账、20 个该字段不适用、618 个待核（含 13 个原精度标签）。

下一批已安排为串行执行：分块量化预计算 scale 的队列结束后，先采每通道量化首例并核对身份，再试采一个非直接搬出的 FP8/FP4 混合 GEMM；两者地址完整性及反向测试仍须逐项验收。队列使用同一设备锁，失败不会标通过。

9 个 DeepGEMM FP8/FP4 GEMM 使用 Cube 直接搬出结果；向量核将解量化数据从 UB 搬到 L1，不使用 UB→GM。已核对原二进制、模板参数和固定源码，该字段对这 9 个目标不适用；不能据此说算子没有输出搬运。DeepGEMM 原版现有 20 个已对账、79 个待核、55 个该字段不适用（含 34 个纯 Cube）。[逐例审计](deepgemm-dequant-direct-static-audit.json)

分块量化仅计算 scale 的 20 个 case 全部通过对账；使用预计算 scale 的分块量化首例及删记录／改 CSV 反向测试通过，其余 case 队列正在运行。最近一次台账：TileKernels 主归档 365 个已对账、20 个字段不适用、635 个待核（含 13 个原精度标签）。

另有 8 个 DeepGEMM `paged_sparse_mqa_prepare_impl` 历史 case：原二进制和固定源码均显示没有 UB→GM 搬出指令，但存在 SIMT 直接写 GM，因此该字段标为不适用，不能说它们没有写主存。DeepGEMM 原版台账现为 20 个已对账、88 个待核、46 个该字段不适用（含 34 个纯 Cube）。[逐例审计](deepgemm-paged-prepare-static-audit.json)

DeepGEMM 的 4 个 `sleep_impl` 原始二进制及固定版本源码均已核查：它们是等待循环，没有向量核 UB→GM 搬出指令。这 4 个目标的该字段标为不适用，不代表设备没有任何访存；DeepGEMM 原版现为 20 个已对账、96 个待核、38 个该字段不适用。[逐例二进制哈希与指令审计](deepgemm-sleep-static-audit.json)

mHC RMSNorm 反向 20 个 case 已全部完成逐地址及逐核计数对账。最新台账复算通过：TileKernels 主归档 342 个目标已对账、20 个该字段不适用、658 个待核（其中 13 个保留原精度标签）；DeepGEMM 原版 20 个已对账、100 个待核、34 个不适用。分块量化仅计算 scale 的首例正在试采。

其余统一采集入口结构盘点：18 个原有适配器、397 个主归档 case 可以用同一种方式添加只读地址及生成源码记录；另外部分适配器结构不同，需另查。已生成隔离副本，尚未运行；逐类正确性、目标身份、状态型 replay 和地址完整性仍须独立验证。[盘点](extra-proxy-survey.json) · [准备脚本](prepare-extra-proxy-harness.py)

mHC RMSNorm 反向的完整分块 `reduce-rms-bwd-01` 和带尾部 `reduce-rms-bwd-04` 均完成对账并通过删记录、改 CSV 的反向测试。后者 8,001 个 token 中，8,000 个走 UB→GM 共 800,000 B，最后 1 个走 SIMT 直接写 GM，未混入该计数；该组其余 case 已开始采集。TileKernels 主归档最近一次索引为 324 个目标已对账、20 个该字段不适用、676 个待核（含 13 个原精度标签）。

`quant_per_token_cast_with_precomputed_sf` 的 20 个 case 全部完成对账并回填。TileKernels 主归档现有 322 个目标已对账、20 个 UB→GM 字段不适用、678 个待核（含 13 个原精度标签）。mHC RMSNorm 反向完整分块首例正在试采。

下一批 mHC RMSNorm 反向的检查已按生成源码分开完整 16-token 分块和尾部：完整分块使用 UB→GM，尾部使用 SIMT 直接写 GM。对账程序与两种形状的首例尚待上板验证；未将尾部直接写入计算为 UB→GM。

预计算 scale 量化第 4 个 case 的第 1 次尝试遇到已知的 `/proc` 读取竞争而中止，并非已确认的算子错误。其入口仍在使用旧 guard；现已将两套量化采集入口升级到已验证的 guard v6，保留原入口及失败日志，队列以第 2 次独立尝试恢复。

对当时已完成的 63 份量化采集，补查解析器完整诊断字段：均未报告解析丢记录、损坏、溢出或包数不一致。这个检查不能单独证明地址完整，仍以逐地址覆盖对账为准。[逐项结果](quant-parser-quality.json)

使用预计算 scale 的 `quant_per_token_cast_with_precomputed_sf/01` 已完成正确性、输出地址和逐核 CSV 对账，请求搬出 32,768 B；删记录与篡改 CSV 的临时副本均被拒绝。该组剩余 case 已启动逐例队列。[反向测试](quant-castonly-negative-test.txt)

6 个普通非累加混合 GEMM case 全部完成对账并回填；DeepGEMM 原版的 120 个含 AIV 目标现有 20 个已对账、100 个待核，另 34 个纯 Cube 目标该字段不适用。已开始使用预计算 scale 的逐 token 量化首例试采。

混合 GEMM 大输入 `gemm-fp8fp8-nt-k-m4096-n576-k7168` 的首次审计将两个向量核请求合计拿去与单个向量行比较，误判失败。该混合核的 `vector0/1` 分别有独立值；改为逐行对账后通过，请求搬出 4,718,592 B。对 `vector1` CSV 修改及删记录的副本均能拒绝；原失败日志保留，队列已恢复。[反向测试](dg-mix-large-negative-test.txt)

普通混合 GEMM 的 `gemm-fp4fp4-nt-mn-m64-n576-k7168` 首例已通过正确性、历史输入和生成源码身份、输出地址覆盖及逐核 CSV 对账，搬出请求为 73,728 B。已启动普通非累加混合 GEMM 的 6 case 队列（包含此前已对账的 2 例）；当前 DeepGEMM 原版含 AIV 的 120 个目标中 16 个已对账、104 个待核。

`quant_per_token_cast_with_sf_only` 20 个 case 全部完成对账并回填。TileKernels 主归档当前 302 个目标已对账、20 个 UB→GM 字段不适用、698 个待核（含 13 个原精度标签）。已启动 DeepGEMM 普通混合 GEMM 的不同布局首例。

已为 6 个普通非累加混合 GEMM 准备独立历史输入、源码及采集入口；分组 GEMM 未混入。通用对账器在已知混合 GEMM 上与原专用审计逐核结果一致，并拒绝删记录和篡改 CSV 的临时副本；不同形状尚未试采，不能提前标为通过。[比对结果](dg-mix-comparison-test.txt) · [反向测试](dg-mix-negative-test.txt)

只输出 scale 的 `quant_per_token_cast_with_sf_only/01` 完成正确性、scale 输出地址覆盖和逐核 CSV 对账，请求搬出 8,192 B；输出量化值的占位缓冲区不计为写入。删记录、改 CSV 的临时副本均被拒绝。已启动该组剩余 case 的逐例队列。

DeepGEMM `transform_sf` 的 14 个 case 已全部完成地址覆盖和逐核 CSV 对账，并回填清单。DeepGEMM 原版的 120 个含 AIV 目标中，15 个已对账、105 个待核；另 34 个纯 Cube 目标的 AIV 字段不适用。接下来正在试采 `quant_per_token_cast_with_sf_only/01`。

更正早期记录核对：17 份旧 Sinkhorn 元数据实际位于 `metadata/default.json`，上一条将其说成缺少元数据是目录识别错误，现已修正脚本。37 份候选窗口都找到了应用元数据，输入哈希与对应主归档均不同；其中 17 份旧 Sinkhorn 按用户决定只作参考，不用于正式验证。所有窗口继续分开。[逐项证据](early-overlap-evidence.json)

早期数据复用核对：对原先按 shape、dtype 和算子名筛出的 25 对候选，逐窗口核查了 37 份早期记录。最初目录识别有误，修正结果见上方记录。[逐项证据](early-overlap-evidence.json)

DeepGEMM `transform-float32-k-g8-mn128-k7168` 的第 2 次尝试正确性、与历史输入及 JIT 源码身份、地址覆盖和逐核 CSV 对账通过，请求搬出 28,672 B。该类 14 个 case 的队列已启动，跳过此前已对账的 case；当前 DeepGEMM 原版含 AIV 的 120 个目标中 3 个已对账、117 个待核。

DeepGEMM 新布局首例第 1 次准备阶段因隔离采集器缺少其依赖的 `pilot-bf16/collect.py` 而退出，未进入 kernel。已从原隔离采集器复制同一文件并核对内容，第 2 次尝试进行中；失败日志保留。

`quant_per_block_cast` 20 个 case 全部完成对账并回填。TileKernels 主归档当前 282 个目标已对账、20 个 UB→GM 字段不适用、718 个待核（含 13 个原精度标签）。已启动 DeepGEMM `transform_sf` 不同布局的首例补采。

DeepGEMM `transform_sf` 已准备 14 个固定输入及历史源码身份。新通用审计器在已知的 `transform-float32-k-g1-mn256-k2048` 上与原专用审计逐核结果一致；删除记录和修改 CSV 的临时副本均被拒绝。其他 shape 和布局仍需实际首例验证，不视作已通过。

`quant_per_block_cast/02` 第一次身份检查因输出 scale 的带类型转换指针写法而失败；保留原始失败状态及日志后，仅扩展该源码识别，地址和逐核 CSV 审计复核通过（请求 6,199,200 B），本组队列继续。

`quant_per_block_cast/01` 正确性、历史输入与生成源码、两个输出地址覆盖及逐核 CSV 对账通过，搬出请求字节 33,024 B。对临时副本删记录、改 CSV 的反向测试均被拒绝；已启动本组剩余 19 项的逐例队列。

`quant_per_token_cast` 20 个 case 全部通过正确性、地址覆盖和逐核请求字节对账，并回填清单。TileKernels 主归档当前 262 个目标已对账、20 个 UB→GM 字段不适用、738 个待核（含 13 个原精度标签）。已启动不同类型 `quant_per_block_cast/01` 的独立首例试采。

归档隔离工作区已准备在 `D:/tk-profile-backfill`，分支 `expert-profile-backfill-20261109` 基于 `bb866a442c59464902dc2e93916ceea82e7471d9`；以 Git 长路径支持检查，初始跟踪文件状态干净。应用管理的工作区创建请求长时间未返回且没有创建结果，已停止等待并用 Git worktree 建立独立工作区；尚未提交或推送。

量化地址审计验证：用首例的临时副本分别删除一条实际搬出记录、修改一项逐核 CSV，审计均拒绝；未改原始采集。临时副本由测试脚本清理，脚本见 [test-unified-quant-audit.sh](test-unified-quant-audit.sh)。

索引包含量化批次前 4 项对账通过的记录，清单复核后：TileKernels 主归档 246 个目标已对账、20 个 UB→GM 字段不适用、754 个待核（含 13 个原精度标签）。量化队列仍在继续，运行状态以远端日志为准。

量化前两个 case 已通过逐地址对账：第 1 个请求搬出 40,960 B，第 2 个 6,336,792 B。第 2 个最初审计只接受打包输出的生成代码写法，遇到另一种合法的输出指针写法而停止；在保留失败日志后扩展该身份检查，地址覆盖和逐核 CSV 判定未放宽，复审通过。其余 `quant_per_token_cast` case 队列已继续，遇异常停止。

量化首例第 1 次实际没有进入 kernel：隔离适配器在求默认源码路径时提前抛 `IndexError`，而 `msprof` 仍以 0 退出并打印结束语。尝试及日志保留，不计为采集成功。已只修正适配器读取明确配置的仓库路径，并要求有应用结果、目标 CSV 和缓存后才能继续；第 2 次独立尝试进行中。

`mhc_fn_normw_merge_fwd` 20 个 case 全部完成逐地址对账并回填。当前 TileKernels 主归档 1,020 个目标：242 个已对账、20 个 UB→GM 字段不适用、758 个待核（含 13 个原精度标签）。已开始 `quant_per_token_cast` 首例试采，完成前不启动其余同类 case。

四个 MegaMoE 的工作区地址覆盖已复核：[索引](mega28-dbi-index.json)包括各自逐区检查结果和文件哈希。按其单 rank、无 shared expert、所有 top-k 路由有效的合同，L1 数据与 scale、L2 数据与 scale、合并输入及最终输出均逐字节覆盖应有范围，已观察到的记录无重叠。该检查不能排除遗漏了对已覆盖地址的重复写入，故总流量完整性仍未证明；独立 DBI 轮与失败的其他 PMU 重放不合并。清单状态更新为 `dbi_window_coverage_verified_traffic_unverified`，不标完整对账。

最新索引已回填并经清单校验：TileKernels 主归档 1,020 个目标中，223 个已有逐地址请求字节对账、20 个 UB→GM 字段不适用、777 个待核（其中 13 个保留原精度标签）。四个 28 核适配 MegaMoE 均有独立 DBI 轮并通过正确性与最终输出覆盖检查；仍标为工作区完整性待核。`mhc_fn_normw_merge_fwd/01` 通过试采和逐地址对账，该类型的可恢复队列已启动。

MegaMoE 首例工作区进一步检查：按固定源码布局计算 6 类目标地址，32 条路由的 L1 数据、L1 scale、L2 数据、L2 scale、合并输入和最终输出都能逐字节覆盖预期范围且没有重叠；L1、L2 数据使用相同的 32 个工作区行。检查脚本为 [inspect-mega28-scratch-first.sh](inspect-mega28-scratch-first.sh)。这比只检查最终输出更强，但仍需独立确认指令重复写入等是否会导致遗漏记录，因此暂不把整个采集标为完整通过。第三个形状的独立 DBI 轮已通过原有检查，第四个在运行。

MegaMoE 第三个形状 `mega-h512-i1024-e8-top4-t64` 的首次采集在监控读取 `/proc/<pid>/status` 时，子进程正好退出，触发 `ProcessLookupError`，本次监控中止，原尝试保留；这不是已确认的计算错误。guard v6 仅把该进程消失情形与已有的文件消失情形同样处理，其他读取错误仍向上报告，未知或仍存活的进程仍拒绝；本地测试通过。已用新 attempt 恢复队列，具体采集结果仍待核验。

MegaMoE 适配版目前 2/4 个计划 case 已获得独立 DBI 轮：该轮的输入与历史匹配、正确性通过、最终输出地址完整覆盖，逐 AIV 的 CSV 与记录对账通过；两个 case 的内部工作区搬运完整性均未证明，因此清单标记为 `dbi_window_scratch_unverified`，不算完整对账。剩余 2 个正在队列中。每个原有失败的 PMU 轮与 DBI 轮分别保留。

MegaMoE 28 核首例补充核验：`MemoryDetail + application` 的第 8 轮（PID 325752）单独的正确性、历史输入和输出摘要、JIT 源码及编译产物匹配；144 条 UB→GM 记录的最终输出覆盖完整，按独立 AIV 的工具 CSV 口径也能对上。另两轮 PMU 子运行失败，因此整份多轮组合仍不准入；工作区搬运的完整性也未得到独立证明。该轮标记为 `dbi_window_correct_output_covered_scratch_completeness_unverified`，不误标为完整对账。kernel replay 的独立试验仍出现非有限输出。其余 3 个适配 case 已按相同独立 DBI 窗口方式启动，失败或缺证即停。

MegaMoE 详细采集试验：`MemoryDetail,Default + range` 被 msprof 明确拒绝，命令日志报 replay 组合无效；`MemoryDetail,Default + application` 完成多轮但其中两次子运行输出非有限，整份混合采集不准入，即使最后有 144 条 UB→GM 记录。`MemoryDetail + application` 的一次尝试在前几轮结果通过后被进程监控中止：`npu-smi` 返回了刚退出的本任务重放 PID 316013，现场检查该 PID 已不存在且对应本任务正确性结果。新增 guard v5 只对此前已观测属于本任务、当前 `/proc` 已消失的 PID 识别为过期记录；未知 PID 或仍存活的 PID 仍中止，3 秒监控门槛不变。已覆盖已退出、自身存活、未知和当前子进程的独立测试，新的独立 attempt 继续验证。

Sinkhorn 反向 20 项采集与逐地址对账已完成，待下一次清单索引回填。按新增要求，在该队列结束后启动 28 核适配版 MegaMoE 首例：沿用已验证的 range replay、profiler 预热 0 次、应用预热 5 次，并将目标调用的设备地址单独记录；准备阶段、采集阶段均在 guard 保护下，结果待核。

11 月 10 日 00:09 后：Sinkhorn 前向 20 个 case 全部完成对账并回填；反向首例正在试采。TileKernels 主归档 1,020 个目标中，202 个请求字节已对账、20 个 UB→GM 不适用、798 个待核（含 13 个原精度标签）。最新清单哈希和原始索引核对通过。

MegaMoE 离线准备：hidev 的上游源码和 28 核适配源码均存在；逐个比较上游 Git 跟踪的 98 个普通文件，只有 `deep_gemm/include/deep_gemm/common.hpp` 不同，差异为 `kNumAICores: 32 → 28`；适配 host 扩展及两份头文件的 SHA256 与原实验 `build-result.json` 一致。此检查不代表四个 case 的新 `MemoryDetail` 已采集或对账。

Sinkhorn 前向 `mhc_sinkhorn_fwd` 首例通过逐地址对账，20 个 case 的串行队列已启动，遇异常停止；截至启动，主清单为 182 个请求字节已对账、20 个 UB→GM 不适用、818 个待核。

23:56 后：`mhc_reduce_partials_and_rmsnorm_fwd` 20 个 case 全部完成三份输出的逐地址对账并回填。TileKernels 主归档 1,020 个目标中，182 个请求字节已对账、20 个 UB→GM 不适用、818 个待核（含 13 个原精度标签）。Pre-split 首例记录不完整，尚未启动批次。

`mhc_pre_split_mixes_fwd/01` 首次详细采集正确性和源码身份通过，但 1,001 token、3 份输出按生成源码的分块逻辑应有 48 条向量核搬出记录，日志仅有 13 条；工具解析汇总显示 `droppedRecord=0`、`memoryCorruption=0`，所以不能用这两个字段为零证明采集完整。首例标待核、没有启动该类批次，日志和源码保留，需单独定位。

用户已知晓 `DanielLee343/TileKernels` 为公开仓库，并明确要求继续推送到该仓库；不再修改可见性，不创建新仓库。推送仍安排在本轮数据与索引归档核验之后。

仓库状态补充：hidev 的本地 `origin/main` 引用落后，故显示 ahead 12；经 GitHub API 直接查询，远端 `main` 当前为 `bb866a442c59464902dc2e93916ceea82e7471d9`，与 hidev `HEAD` 一致。推送时仍须再次核对远端，避免覆盖他人的后续提交。

用户同意将 `DanielLee343/TileKernels` 改为私有后，GitHub PATCH 返回 HTTP 422：`Public forks can't be made private`，因此原仓仍公开，没有推送本轮数据。已提出创建独立私有仓 `DanielLee343/TileKernels-private` 并同步历史作为替代，等待用户答复；采集继续。

23:50 后的新增交付要求：用户授权在当前补采后，单独完成 28 核适配版 MegaMoE 四个 case 的补采，并归档、推送本轮数据。原版上游 `3a35326` 与 `kNumAICores=28` 实验版分别记录。已查询 GitHub API：`DanielLee343/TileKernels` 存在，但当前 `private=false`；认证用户为 `DanielLee343`。与用户指定的私仓要求不符，推送动作暂停，已异步请求用户选择可用私仓；采集不因此停止。现有 hidev 私仓本地 `main` 相对其本地 `origin/main` 显示 ahead 12，推送前还要核对真实远端与待提交范围，不能覆盖既有历史。

23:43 后：`mhc_reduce_partials_and_rmsnorm_fwd` 首例采集、三份输出逐地址覆盖及按核对账通过；20 个原始 case 的可恢复串行队列已启动，逐项失败即停止。任务继续运行中，完成情况以最新索引和队列状态为准。

23:38 后：检查 `mhc_head_compute_mix_fwd` 首例发现其 SIMT 计算代码直接写 GM，而不是通过 UB→GM 指令搬出。首例同口径新采集的源码、二进制和日志均支持这一点，且日志观察到指向输出地址的 SIMT `STG`；该记录不能外推为完整输出流量。随后逐项反汇编 20 个历史 case 的原始捕获二进制，并核对源码、目标、输入输出规格及本地/远端文件 SHA256：均无 UB→GM 指令、有 SIMT 写 GM 指令，已在 [历史检查](historical-head-no-ub-gm.json) 和 [targets.csv](targets.csv) 标为 `aiv_ub_to_gm_not_applicable`，这不代表没有主存写入。当前 TileKernels 主归档 1,020 个目标：162 个请求字节已对账、20 个该字段不适用、838 个待核（含原有 13 项精度标签）。

23:29 后：`engram_sinkhorn_finalize` 本轮所选 16 个历史正确性通过的 case 已全部完成逐项对账（另 4 个原精度标签的目标保留原状态）。hidev 共有 139 份新增对账窗口并已记录文件哈希；去重后 TileKernels 主归档 1,020 个目标中 162 已对账、858 待核（含 13 个原精度标签）。DeepGEMM 原版有 2 个含 AIV 目标对账通过、118 个待核。大输入采集新启动时使用包含 512 MiB 日志限制的 guard，保留 3 秒设备监控约束。

23:23 后：Hash 共 13/20 项完成对账；`02/06/08/10` 地址记录不完整，`12` 工具卡住，`17/18` 同类风险暂缓，共 7 项未完成。新选 `engram_sinkhorn_finalize`：截至本次索引共有 3 个样本通过，继续在 hidev 串行采集；队列遇地址、身份或采集错误会停止。最新索引包含 hidev 126 份已对账的新窗口；去重后主归档 1,020 个目标中 149 已完成、871 待核（含 13 个原精度标签单列）。DeepGEMM 原版 2 个已对账、118 个含 AIV 目标待核。

23:18 后：已将首批 8 个通过的 Hash 窗口回填，hidev 通过的新增窗口总数为 118。去重后 TileKernels 主归档 1,020 个目标中，141 个已有请求字节对账，879 个待核（含 13 个单列原精度标签）。另外已准备 176 个历史 collector 可运行 case 的串行采集清单；其采集和身份核对不能替代后续逐家族地址完整性核验，尚未把它们计入通过。

23:12 后：`engram_hash` 首例及多个较小 case 通过；大 case 中发现 `MemoryDetail` 地址记录不完整。例如 `hash-02` 按源码输出分块应有 64 条搬出记录，实际解析出 61 条，缺少 3 个分块；日志中 `droppedRecord=8779`、`memoryCorruption=2` 是工具解析统计。所查本地 msopprof 源码中，后者对应记录头标识不匹配后停止解析该包，并非已证实硬件内存损坏。该 case 保留采集结果并标待核，不以源码推测填补缺失的观测记录；队列继续采集其他 case，之后对缺失 case 另开 attempt 重试。

`hash-12` 正确性输出已写出，但 profiler 在设备进程已退出后持续等待超过四分钟，期间日志没有继续增长；为避免阻塞其他 case，主动停止本任务的 profiler 进程组，保留首轮日志及远端 `agent-stopped-hang.txt`，按失败留待独立重试。已重启队列并跳过该受阻 attempt；未停止其他人的进程。

大输入 Hash 已多次出现同类地址缺失，暂缓尚未采集的 `hash-17/18`，在确认通用修复前不重复启动同类大 case。为调整后续队列，暂停了本任务的分发父进程，允许正在执行的 `hash-16` 正常结束并手动审计通过，保存了修改前的状态；随后仅终止该已暂停父进程，按新队列继续其余 case。此前 `hash-14` 因进程监控间隔达到三秒而中止；保持原保护门槛，在设备空闲检查后重试通过。

23:08 后：TopK 20 个 case 全部采集并完成请求地址、输出范围、编译产物及 CSV 对账；之前失败的审计按已确认的输出搬运口径重新运行，原失败日志保留。hidev 共 110 份经过核验的新增窗口，索引与各原始文件哈希已回填。去重后 TileKernels 主归档 1,020 个目标中 133 个已有请求字节对账、887 个待核（其中 13 个原精度标签单列），详见 [targets.csv](targets.csv)。下一批 `engram_hash` 20 项已准备，首例正在试采。

2026-11-09 23:04 CST：DeepGEMM 已完成 1 个纯 Vector `transform_sf` 和 1 个混合核 `fp8_gemm_impl` 的正确性、历史真实输入、生成源码、采集二进制、地址及逐组字节对账，详情分别为 [纯 Vector 审计](deepgemm-transform-audit.json) 和 [混合核审计](deepgemm-mix-audit.json)，均为 hidev 的独立窗口。混合核旧、新记录的输出缓冲区摘要不相同：旧采集在预热前记录全零输出，新采集在预热后记录输出；该非累加 GEMM 的真实输入一致、结果正确。DeepGEMM 原版 120 个含 AIV 目标中 2 个已对账，118 个待核；34 个纯 Cube 目标的 AIV 字段不适用。

TopK 已启动补采：前 9 个 case 经复核均通过，其余正在串行采集。历史源码和当前源码的唯一区别是嵌入断言文本的仓库路径，复核严格替换该路径后逐字比较。`UB_to_GM_datas(KB)` 对非 32 字节整倍数搬运请求的数值不等于请求字节；在前 9 个具体 case 中，其数值逐组等于每条单 burst 请求长度按 32 字节向上取整后相加。新审计保留两组数据，只用此经验公式对当前 TopK 输出搬运做交叉检查，不推断它在其他指令或算子上的普适性。前几项第一次审计失败与后续复核日志均保留。

补充源码线索：本地留存的 msopprof 源码 `MovAlignV2RecordSize` 对 UB→GM 的源端字节按 32 字节向上取整，`metric_data_handler.cpp` 中相应统计使用 `record.srcMemSize`。这与 TopK 的观察相符；本地源码和安装二进制的逐提交对应关系未在本步重新验证，因此仍以逐 case 数据对账为准。

2026-11-09 22:37 CST：`reduce` 20 项和 mHC 50 项在 hidev 完成逐项对账，70 份采集及原始文件哈希已写入 [hidev-capture-index.json](hidev-capture-index.json)，设备告警保留在每项记录中。与 tbe 的 13 项重叠去重后，主归档中总计 93 个目标已有对账的请求字节，其中 57 个目前只有 hidev 告警状态数据；其余 927 个目标待补。Engram fused-weight 20 项的首例及串行队列已在 hidev 启动，队列 PID 写在 `fused-queue-hidev-npu0/queue.pid`，首例通过对账后才进入下一项。

22:46 后：Engram fused-weight 20 项也已完成，hidev 合计 90 份采集索引与文件哈希已回填并核验。去重后主归档有 113 个目标已对账（36 个有 tbe 证据，77 个当前只有 hidev 告警状态数据），907 个仍待核。DeepGEMM 纯 Vector 代表例已启动，准备和采集分开监控，地址核验尚未完成。

2026-11-09 22:21 后：用户要求忽略 hidev 的设备告警，先拿旧 case 做同口径对照，接近则继续。`reduce-01` 在同一 hidev 设备、同版本 CANN 与 msopprof、`Default` kernel replay、相同 5 次应用与 profiler 预热、相同输入和源码下重测 3 次；历史为 2.281 µs，新值为 2.254、2.248、1.970 µs，中位数 2.248 µs，较历史低 1.45%。二进制哈希、逐核 MTE2/MTE3 指令数、向量核搬入计数和主存写计数一致；单次较历史低 13.63%，原因未知，不能由此断言设备告警对其他 case 无影响。详细结果见 [hidev-same-mode-comparison.json](hidev-same-mode-comparison.json)。已按用户要求继续，保留健康告警和单独的采集窗口。

对照期间暂停过 mHC 队列，已把 `second/expand-bwd-18` 第 1 次尝试准确标为中断，并从新尝试恢复；此前 13 个 mHC case 已对账通过并自动跳过。其余任务持续采集。

最近一次观察：mHC 50 项中，`expand-bwd` 16 项、`expand-fwd` 15 项、`post-fwd` 4 项，以及 `preapply-fwd` 首项已对账通过，共 36 项；其余还在队列中。Engram fused-weight 的 20 项采集脚本和 2 个 DeepGEMM 试采入口已准备，尚未上板验证。

后续观察：mHC 队列已完成 `expand-bwd` 16 项、`expand-fwd` 15 项、`post-fwd` 4 项和 `preapply-fwd` 4 项，共 39/50 项。用户要求按同模式对照结果继续；所有新结果仍记录采集时的告警和各自原始窗口。

恢复 tbe 连接后核实：先前 tbe 后台队列已经退出，`reduce-02` 至 `reduce-13` 完成，`reduce-14` 留有中断尝试；tbe 卡 3 当前无本任务进程。12 个成功结果已完整下载，归档 SHA256 为 `c312ec771f3c61b8dff40dadb2f5d14c03523bd03da4c353438a627c7200620a`，并从原始日志重新计算对账（本地复算使用设备端保存的反汇编）。已与先前 tbe `reduce-01` 一起登记到 [targets.csv](targets.csv)：TileKernels 主归档现有 23 个旧 tbe 已对账、13 个新 tbe 已对账、984 个仍待核；hidev 告警期间采集另列，未冒充正常设备数据。

2026-11-09 22:07 CST：按用户最新要求改回 hidev。设备当前无进程、健康仍为 `Alarm 8C4BA00C`，结果持续单列设备告警。已重启 `reduce` 可恢复队列：自动跳过已对账的 `reduce-02` 至 `reduce-05`，从先前中断的 `reduce-06` 新尝试继续。tbe SSH 仍拒绝连接，先前持久队列是否存活无法确认，重连后先检查，避免重复任务。

22:09：hidev 队列的 `reduce-06`、`reduce-07`、`reduce-08` 新尝试也已通过正确性、源码及逐核请求字节对账；队列仍运行。设备告警的影响尚未排除，因此这些结果的健康设备准入仍待核。

22:12 后：hidev 的 `reduce-01` 至 `reduce-17` 已完成正确性和逐核请求字节对账；18–20 仍在队列中。50 个 mHC case 的采集器与地址审计器已准备，审计器已在 4 个既有 mHC 族的真实日志上离线复算，并能拒绝被篡改的输出地址；尚未在本次 hidev 告警状态下完成 mHC 新采集。

22:13 后：hidev 的 `reduce-01` 至 `reduce-20` 全部完成正确性和逐核请求字节对账，队列退出码 0。它们均采集于 `Alarm 8C4BA00C` 状态，作为告警期间的数据单列，健康设备准入尚待评估。开始部署 50 个 mHC case。

已启动 mHC 串行队列，首两个 `expand-bwd` case 已通过目标身份、正确性、动态地址、二进制指令和逐核字节对账；其余正在继续。已准备 Engram fused-weight 的 20 个 case 和对应审计脚本，尚需上板首例验证后才可批量采集。

2026-11-09 21:57 CST：用户要求停止 hidev、改用 tbe 卡 3。hidev 队列已停止，设备进程查询为空；`reduce-01` 至 `reduce-05` 完成对账但采集时设备处于 `Alarm 8C4BA00C`，单独保留为待设备状态评估的资料；`reduce-06` 中断。5 份原始结果已打包回传本地，归档 SHA256 为 `07b54a4cd88d4171650ff98ac38118fa3cf9fe42e919bf3e4fda2431d144cf48`。tbe 3 号卡检查时健康、空闲、PCI `0000:8C:00.0`；历史元数据和队列脚本已传输校验，已启动 `reduce-02` 至 `reduce-20` 串行队列，进程 PID 记录于 tbe `~/expert-profile-backfill-20261109/reduce-queue-npu3/queue.pid`。当前在运行，完成及逐项对账状态待复核；每项失败即停。

21:59：tbe 队列报告 `reduce-02` 至 `reduce-06` 均通过逐项对账，队列仍在运行。已另外筛出 50 个沿用原采集器的 mHC 待补 case；7 个采用独立 retry 适配的 `post-fwd` 不混入该 50 项，需另行核对。

22:01 后：最近一次 tbe 状态显示 `reduce-02` 至 `reduce-09` 对账通过、队列运行中。随后 SSH 连接再次被拒；队列采用持久进程启动，但断连期间状态未知，不能声称已完成或仍在运行。50 个 mHC case 的历史输入和源码对账资料及采集/审计程序已上传，但最终校验清单传输未确认，不启动该批。hidev 告警状态下的 5 份采集单列于 [hidev-alarm-observations.csv](hidev-alarm-observations.csv)。

只读网络复核：本地 Windows、WSL，以及从 A5_1 发起的 TCP 22 端口连接均未连通 tbe；这表明问题不只发生在本地某个 SSH 客户端，但不足以区分服务器监听、网络或访问控制原因。未在 A5_1 使用 NPU或启动采集。

2026-11-09 21:46 CST：按用户最新要求切换 hidev。现有 tmux 已连接，NPU 0 当时没有显示进程，CANN 9.2.1，msopprof 构建 `884ac969494a186a9c63ac45c4c39ad7289b3215`；私仓提交 `bb866a442c59464902dc2e93916ceea82e7471d9`。设备 Health=`Alarm`，错误 `8C4BA00C`，描述为驱动软件故障且不可恢复；只读检查 HBM 单/双 bit 错误均为零。保护下的小计算已通过，但不足以证明告警不影响性能或数据，未重置设备。开始独立采集 `reduce-01` 作为故障状态下的对照，原始目录 `/workspace/expert-profile-backfill-20261109-hidev/runs/reduce-01/hidev-npu0/attempt-001/detail/`；结果待核验。本次设备及告警与其他采集窗口分开登记。

21:49 后：hidev `reduce-01` 已完成设备正确性、历史输入和生成源码身份、编译后的搬出指令、4 核日志地址及 CSV 成对合计对账；本次监控共 30 次查询、最大成功查询间隔 0.810 秒。结果只证明这一采集对账通过，设备仍告警，不能据此认定性能正常。已在 tmux 启动同类 `reduce-02` 至 `reduce-20` 的串行可恢复队列，每项采集后独立对账，遇失败暂停；远端任务目录的 `reduce-queue-hidev-console.log` 和各 case 的 `queue-status.json` 记录进度。

21:27 后恢复：用户允许 tbe 卡 3 和 4。3 号卡检查时健康、无进程、PCI `0000:8C:00.0`；选择 3 号卡，使用其专属锁与可见卡映射。新的监控对进程查询超时做短超时重试，连续失败或两次成功查询相隔超过 3 秒仍中止；监控测试覆盖超时恢复、持续失败、未知输出拒绝。已启动 `engram_sinkhorn_step_reduce/01` 详细采集，远端目录 `~/expert-profile-backfill-20261109/runs/reduce-01/tbe-npu3/attempt-001/detail/`；结果待检查。GCM 和制卡继续冻结。

21:29 首例通过：[逐项复算](reduce-01-audit.json)。输出正确，固定输入和生成源码与历史 case 一致，4 个启动 block 分别请求搬出 1,024 B，地址覆盖 4,096 B 输出；日志 PC 与采集二进制的 `MOV_UB_TO_OUT_ALIGN_V2` 一致，2 个 CSV 两核合计均对上。48 次进程查询无失败，成功查询最大间隔 0.967 秒。tbe 卡 3 数据为独立采集窗口，不直接回填历史卡的原始 CSV。开始准备同一 reduce 类型的可恢复批次。

随后准备同类批次时，向 tbe 传文件的 `scp` 返回 `Connection closed`；两次独立 SSH 新连接在 banner 交换前返回 `Connection refused`，Windows 的 22 端口测试也失败。首例原始数据与对账已留本地和远端；队列传输未确认完成，也没有启动。无法据此判断是 SSH 服务、防火墙还是网络路径；恢复连接后应先检查现场，勿假设有后台任务。已将成功的 1 项新采集写入 [targets.csv](targets.csv)，TileKernels 主归档尚有 996 项待核。

2026-11-09 20:43 CST：已读取任务及现有数据盘点，正在建立逐项清单。tbe NPU 4 (`0000:D3:00.0`) 检查时无进程，根文件系统可用约 8.9 TB。其他用户正在使用其他设备，不会停止其任务。采集期间需要持续监控，设备空闲状态可能变化。

基线：TileKernels 主归档 1,020 个 case/目标有 Default，23 个已有逐核字节对账；其余 997 个待核。DeepGEMM 原版 154 个 case 有 Default，其中 120 个含 AIV 目标待核，34 个纯 Cube 的 AIV 字段不适用；原版 4 个 MegaMoE 整份 Default 未采到。早期归档及 28 核适配实验另列；其中 1 个早期 SwiGLU 有字节对账。13 条精度标签保留。统计需以逐项清单复核为准。

逐项初始清单：[targets.csv](targets.csv)，生成器 [build_inventory.py](build_inventory.py)，共 1,301 行。主归档为 1,020 个 TileKernels 目标（23 已对账、997 待核）和 154 个 DeepGEMM 原版目标（120 含 AIV 待核、34 纯 Cube 不适用）。另列 4 个原版缺整份记录的 MegaMoE、99 个早期 case 的 119 个目标、4 个 28 核适配实验 case/目标。经主会话指出，早期 20 个 RoPE case 每个有两次目标调用，已按原始目录 `0/1` 拆成 40 行；只标调用序号，不臆测 Q/K。早期批次可能与主归档重复，尚未完成按输入规格去重；不同批次暂不相加当作独立样本。

首批试测：不同于 mHC 的 `engram_sinkhorn_step_reduce/01` 第 1 次采集因 `npu-smi` 进程查询超时 3 秒由保护程序中止；之后查询显示 NPU 4 无进程。中止前尚无完整 profile，原因暂未确定，失败文件留在 tbe 的 `~/expert-profile-backfill-20261109/runs/reduce-01/attempt-001/`。不改变监控间隔和 3 秒保护界限，复试时写入新的 attempt。DeepGEMM 环境及纯 Vector、混合样本仍待准备。GCM 与规则卡冻结。不同设备和采集窗口不拼接成同一条原始记录。

20:47：第 2 次同样因进程查询超过 3 秒中止，保留 `attempt-002`；不继续盲目重试。主机负载高是同期事实，不能断定它造成超时。已将与历史版本 SHA256 一致的 DeepGEMM 源码归档复制并解压到任务独立目录，原仓提交 `3a35326271b069b8b5bf1a754435acd6cc91575b`，准备隔离构建。

20:51：4 号卡查询发现其他 Python 进程，不能启动采集；保留进程不做更改。DeepGEMM host 扩展构建已尝试，先缺 tree-sitter，隔离安装后继续发现系统缺 `elfutils/libdwfl.h` 开发头文件，正在准备任务独立依赖；未修改系统环境。

20:56：4 号卡一度空闲，连续 30 次设备进程查询通过后重试 `reduce-01`；实际采集期间查询再次超过 3 秒，第 3 次按保护条件中止。三次均无可准入 profile；尝试及路径见 [attempts.csv](attempts.csv)。当前没有通过代表 case，因此不能启动批量或将其他 case 标为采集失败。进程查询是抽样，30 次空闲不能保证后续独占。暂缓所有上板采集，不放宽保护。

DeepGEMM：下载与本机 `libdw`/`libelf` 运行库版本一致的开发文件并解包到任务目录，保留前两次构建失败记录。第 3 次 host 扩展构建及导入通过，扩展 SHA256 为 `f1be84323009acee027a4f599052d273c08c49873aa9b2fe2264904082d95564`。这不是设备 kernel 执行或 profile 成功。源码提交未变，安装与构建均在任务目录。

早期复用：形状、dtype 和同名目标的初筛得到 [25 对候选](early-overlap-candidates.csv)，其中 Sinkhorn 有不同参数可能；未经属性、stride、输入、源码与采集窗口核对，不能作为可复用结果。只对 300 个主归档目标有完整输入输出规格可做此初筛；其余未匹配不能认为一定不同。[统计](early-overlap-summary.json)

清单独立检查：[inventory-verification.json](inventory-verification.json) 核对 1,321 份原始记录、目标名及对应原始 OpBasicInfo/Memory CSV 路径，并确认 20 个早期 RoPE case 各有 2 个不同调用。

三次试采的 39 个现场文件已复制到本地并按文件 SHA256 与 tbe 一致，见 [attempt-evidence-verification.json](attempt-evidence-verification.json)。恢复前提和已准备的脚本见 [RESUME.md](RESUME.md)。截至 20:59 的只读检查，NPU 4 未见进程，我方没有残留的 `msprof` / 采集工作进程；该状态可能随时变化。

复用核验：23 个 mHC 已执行旧的 `verify-final.py`，结果通过；早期 SwiGLU 的原始 CSV 逐核值不通过是已知现象，使用日志地址复算的独立审计通过，输出在 [swiglu-reaudit.json](swiglu-reaudit.json)。**操作记录：**我事前没有注意两个旧核验脚本会写文件，运行它们时分别重写了旧目录的 `tbe-recapture/verification.json` 和 `byte-smoke/tbe/verification.json`；脚本按现有原始数据重新生成结果，原始采集未修改。因未预存两份文件的运行前哈希，不能声称重写前后逐字节相同。之后所有新输出均写在本任务目录。
