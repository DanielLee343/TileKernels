# SwiGLU / RMSNorm / RoPE：60条完整调用冷缓存采集

**60条已全部尝试，59条取得匹配Default；52条数值通过、7条数值失败、1条启动失败。** 本批仅覆盖冻结清单的三个任务各20条，完整shape/dtype/attrs保持不变。[最终合并状态](D:/puma_v2/outputs/reprofile-60-cold-20261101/final_status.json)及[失败摘要](D:/puma_v2/outputs/reprofile-60-cold-20261101/status.json)已落盘。

| 任务 | 数值通过且已采集 | 数值失败但已采集 | 启动失败 |
|---|---:|---:|---:|
| swiglu | 19 | 0 | 1 |
| rmsnorm | 13 | 7 | 0 |
| rope | 20 | 0 | 0 |

`swiglu-supp-08`报告动态共享内存258048 B加kernel静态共享内存超过本配置允许值，未进入Default。RMSNorm的`cann-6/8/9/11/12/14/15`完整数值检查失败，保留Default数据并明确标为数值失败；重复正确性检查均确认实际输出含非有限值，CPU参考全部有限。

6项覆盖、边界、身份、统计、备份和源码保全核验通过，0项未完成、0项放弃。9,475,655 B压缩包及3131个内容文件通过SHA256校验。核验通过表示本批尝试和证据完整，不表示所有kernel通过精度检查。

关于结果接口：[profile_results.json](D:/puma_v2/outputs/reprofile-60-cold-20261101/profile_results.json)保留旧40结构，并新增每case的summary，定义见[SCHEMA.md](D:/puma_v2/outputs/reprofile-60-cold-20261101/SCHEMA.md)。主时间取匹配Default的Task Duration；RoPE取同一range内Q/K配对之和。Vector、MTE2、MTE3等资源取每个kernel的核间max，再对Q+K求和。所有原始CSV、block/sub-block、单位、NA仍保留。Cube等原始NA与依据vector类型派生的0分开记录。

关于冷缓存：主值来自msprof op原生kernel/range replay。成功smoke的实际运行日志记录六次ClearL2Cache；RoPE每次清理后执行完整RI模型，Q和K之间不清。五次RI预热发生在这些清理/计数重放之前。原生MSTX接口绑定真实stream，Q/K导出序号0/1和PID/范围共同核对；重放后全部输出与单次CANN参考一致。普通trace只用于身份、顺序和初始化诊断，不用作冷缓存主时间。

关于轮次，三项分别记录：

1. **5次应用预热**：薄wrapper在目标MSTX范围外调用完整算子5次。
2. **`--warm-up=5`**：profiler自己的预热参数，独立于应用预热。RoPE smoke实际看到5次RI预热执行。
3. **6次PMU重放/清L2**：为不同计数组收集数据；每个native kernel有DeviceProf1..6原始数据。这些不是6个独立Default时延样本，**不对它们计算时延中位数**。summary保存一次Default报告的Task Duration及其原值，RoPE配对求和。不同指标组可以来自不同物理重放，不伪称同一轮同时计数。

关于环境限制：显式aclrtDeviceL2CacheFlush(NULL)虽然在头文件/动态库存在，实际返回207000；首次尝试完整保留。Torch domain MSTX导致空Default导出的一次尝试也已归档，不算成功数据。成功路径使用SDK的mstxRangeStartA/End。安装的msopprof核心为native shared library，未附C++源码；留存的是该版本/二进制hash、导出调用点和完整反汇编、实际runtime清理/RI执行顺序以及输出复原校验，不声称取得完整源码。

关于原始证据：`raw/cases/<case_id>/trace`保留普通trace导出；`raw/cases/<case_id>/default`保留Default原始CSV和小型二进制计数文件；`raw/metadata`含环境、边界判定、版本、实现证据；`raw/smoke-attempts`含失败的采集流程尝试。未改TileLang kernel、编译参数、容差、模型参数、旧40或历史comparison_60.csv。运行脚本及远端原始数据保留在`/workspace/reprofile-60-cold-20261101`。

只把本轮有限生成输入的完整shape检查称为数值检查，不外推为完整CANN benchmark精度契约。最终核验入口为`python -B verify.py`。

关于失败误差统计：原采集wrapper在误差含NaN时使用的`max(0, NaN)`会把最大误差误记为0，allclose失败判定和不匹配元素数不受此影响。原metadata完整保留；规范结果将这类最大误差标为不可用。采集结束后，单独用同shape、同输入、同native设置和同容差复核这些失败，记录非有限值数量及有限元素最大误差；该复核没有新增profiling样本，也不改写原失败判定。
