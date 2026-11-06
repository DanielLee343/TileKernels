# Sinkhorn + mHC backward：冻结40 case设备采集

本目录仅覆盖正式manifest的20条sinkhorn、20条mhc_post_bwd。**40条已全部尝试，29条取得普通trace和Default；其中27条数值通过、2条数值失败。另11条原生编译失败。** 没有超时，没有扩跑其他任务。

| 任务 | 已尝试 | 数值与采集通过 | 数值失败但已采集 | 编译失败 |
|---|---:|---:|---:|---:|
| sinkhorn | 20 | 20 | 0 | 0 |
| mhc_post_bwd | 20 | 7 | 2 | 11 |

关于失败：`mhc_post_bwd-cann-9`、`mhc_post_bwd-cann-10`的`d_comb`和`d_post`全元素不满足既有allclose阈值；另外两输出通过。薄入口与冻结adapter的四个输出逐位相同，本轮没有定位或修复数值根因。11条编译失败均由当前bisheng报告VF栈超限：mHC维度6为6432对6144，维度8为15168对6144。各case的原始编译错误、生成源码和日志完整保留，trace与Default阶段标为`skipped_dependency`，没有填造测量值。

关于核验：6项覆盖、身份、字段、备份及源码一致性核验均通过，0项未完成，0项放弃。这表示尝试与证据留存完整，不表示所有原生kernel通过正确性。

关于结果入口：

- [profile_results.json](D:/puma_v2/outputs/sinkhorn-mhc-profile-40cases-20261101/profile_results.json)：case完整定义、阶段状态、失败原因、时间原样本、每个kernel的全部Default原始CSV字段。
- [SCHEMA.md](D:/puma_v2/outputs/sinkhorn-mhc-profile-40cases-20261101/SCHEMA.md)：JSON结构；`cases[].kernels[].default_captures[].metrics.PipeUtilization.rows`为逐block资源时间，`Memory.rows`和`L2Cache.rows`同结构。所有cell为原始字符串。
- [summary.json](D:/puma_v2/outputs/sinkhorn-mhc-profile-40cases-20261101/summary.json)：紧凑状态清单、失败摘要、各资源字段是否有值；不汇总资源时间。
- [selected_cases.json](D:/puma_v2/outputs/sinkhorn-mhc-profile-40cases-20261101/selected_cases.json)：40条冻结定义，完整shape/dtype/attrs及来源。
- `raw/cases/<case_id>/trace/`：普通msprof导出CSV和timeline，含初始化、copy和非目标任务。
- `raw/cases/<case_id>/default/kernel-0/`：Default的OpBasicInfo及7类原始指标CSV。
- `raw/cases/<case_id>/metadata/`、`logs/`：本case每阶段命令、输入hash、kernel源码、数值检查、设备快照与日志。

关于采集条件：每case先在独立prepare进程编译、执行原生kernel，并与冻结adapter输出核对；按token分块调用原CANN CPU参考，检查完整输入shape的全部输出元素。mHC四输出顺序为`d_residual, d_comb, d_x, d_post`，FP64参考未降精度。检查阈值沿用既有交付脚本；这里只是有限生成输入的数值检查，不是完整CANN benchmark精度契约。

普通msprof在另一个进程中调用原生kernel三次，每次有独立MSTX标记；按global symbol对应的实际任务名及3次launch数量精确筛选。Default使用另一个进程，`--aic-metrics=Default --replay-mode=kernel --warm-up=5 --launch-count=1`。没有嵌套`do_bench(msprof)`，没有逐case采PipeTimeline。所有进程的输入hash、源码hash可互查。

关于解释边界：Task Duration是任务窗口，包含设备任务口径开销；逐block活动时长可以重叠。Vector、Cube、MTE1/2/3、Fixpipe等资源不跨资源求和，也不重组group。NA保留为NA。当前原生mHC是Vector实现；Cube和Fixpipe缺失不代表数值0。Default不同metric组可能来自不同重放，不能合成同一次流水图。kernel replay的工具约定清L2，不认定热缓存。

Memory原始字段单位仍为`KB`；本环境解析器公式按1024换算，但本JSON不预先换算或汇总。此前单位核查证据见[解析器公式](D:/puma_v2/outputs/swiglu-profile-smoke-20261101/raw/metadata/parser-formulas.json)。已取得的9条mHC Default均为Vector实现，逐block的Cube、MTE1和Fixpipe字段为NA；不冒充0或改图。

关于完整性：每case保留阶段、命令和日志，失败后继续。PC备份压缩包2,249,821 B及1052个内容文件分别通过SHA256校验；底层设备数据库、大型二进制dump留在hidev独立目录`/workspace/sinkhorn-mhc-profile-40cases-20261101`。可复用源程序也留在该目录；[PC脚本](D:/puma_v2/experiments/hidev-profile-40cases-20261101)供复用。临时传输文件和已结束的编译临时目录均无残留，原始证据保留。

本轮不改TileLang、TileKernels、预测模型、硬件参数或冻结预测CSV。最终核验入口为本目录`python -B verify.py`，验收清单为GATES.md。
