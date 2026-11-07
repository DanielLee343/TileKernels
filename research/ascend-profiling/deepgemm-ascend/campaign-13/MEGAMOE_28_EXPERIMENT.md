# MegaMoE 28 核适配：独立探索

原始实现固定 `kNumAICores = 32`，并在 `csrc/apis/mega_moe.hpp:159` 检查设备核数。hidev 的 950PR 为 28 Cube 核；对原版单设备调用的实测失败日志在 `runs/campaign-mega-first`。这个约束参与调度、同步、内存布局，不是单纯的启动参数。

## 拟验证的改动和边界

在与原源码和原安装隔离的副本中，将 `deep_gemm/common.hpp` 的 `kNumAICores` 从 32 改成 28，并重新编译 host 扩展与 JIT kernel；保留完整 diff、源码哈希和二进制哈希。先检查代码中所有依赖该常数的调度和等待逻辑，确认无明确的 32 核对齐前提。其间若发现必须更改算法，明确列出改动与原因。不得通过声称设备有 32 核来绕过检查，不覆盖或修改现有官方源码与现有环境。

先运行小输入并限制进程等待时间；若发生设备卡死等异常，停止适配实验并保留日志，不继续发起更多适配 kernel。正确性从已知零输入、expert 路由计数开始，并与独立拼装的单卡参考比较非零输入：原版 FP8×FP4 GEMM、上游 TileLang SwiGLU/量化、第二次 GEMM 和按路由相加。按上游 MegaMoE 测试的全局及逐 token 差异阈值检查，同时测试多个 shape 与 route。参考代码 `mega_reference.py` 需要在实际硬件上先完成验证。

只有能通过上述非零精度、重复性和数据完整性检查，才可将结果标为“28 核适配实验 profile”。即便通过，它也不是原版或已确认最优的专家 profile；规则研究能否使用需另作判断。无论结果如何，都保留原版失败证据。

## 实测结果

在隔离源码和安装中，仅将 `kNumAICores` 由 32 改为 28。`runs/mega-port28-experiment/source.patch`、`build-result.json`、编译日志与 host 扩展记录精确改动和哈希；原源码未修改。

单设备 FP8×FP4 的 4 个不同 case 已通过：`(hidden, intermediate, experts, topk, tokens)` 分别为 `(256,512,4,2,16)`、`(256,512,4,2,64)`、`(512,512,8,2,32)` 和 `(512,1024,8,4,64)`。每次验证零输入、路由计数、非零输入与非融合参考结果，检查输出有限且非全零，检查采集前后输入和输出摘要一致，并保存 Default 原始文件和 JIT 二进制。第一个 case 独立复采一次；两次样本不是两个独立 case。

采集方式为 `msprof op --aic-metrics=Default --replay-mode=range --warm-up=0`，应用自身仍先预热 5 次；采集结果为混合核。kernel replay 在 profiler 下输出非有限值；range replay 的 profiler 预热 5 次发生超时，预热 0 次可通过。另一次复采未载入隔离扩展，程序在设备执行前主动拒绝；补齐 `PYTHONPATH` 后通过。所有尝试保留日志。原因尚不能归结为 profiler 或适配代码的特定内部缺陷。

激活已有环境后，需额外设置 `PYTHONPATH=/workspace/deepgemm-ascend-20261107/mega-port28-experiment/packages:$PYTHONPATH`、`ASCEND_HOME_PATH=/workspace/deepgemm-ascend-20261107/cann-compat-quant`、`BISHENG_HOME=$ASCEND_HOME_PATH`，再运行 `mega_port_run.py --case CASE_ID --source /workspace/deepgemm-ascend-20261107/mega-port28-experiment/source --output NEW_OUTPUT --replay-mode range --profiler-warmup 0 --profiler-timeout 90`。`verify_mega_port.py` 在已归档数据上离线检查哈希、非零输出和复采一致性。
