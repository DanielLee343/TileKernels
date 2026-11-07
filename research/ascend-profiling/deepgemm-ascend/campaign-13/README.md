# 13 个 DeepGEMM-Ascend C++ kernel 采集

入口清单和状态在 `STATUS.md`。`cases-initial.json`／`collect-initial.py` 对应首轮，`cases.json`／`collect.py` 对应扩展轮；`cases-expanded.json` 是扩展轮规划快照。每项 case 记录目标 kernel、调用入口、dtype、形状、布局与参数。不同目标可能使用同一算子输入，不能作为不同专家来源。

脚本调用上游的 GEMM、MQA、稀疏 MQA、layout 测试及其参考，先运行精度或语义检查，再调用 `msprof op --aic-metrics=Default --replay-mode=kernel`；目标 API 前预热 5 次，MSTX 范围与目标 kernel 名称过滤锁定采集对象。GEMM 采用上游 `GemmTestDesc` 参考和 cosine-like 差异 `<1e-5`；MQA 和稀疏 MQA 使用上游自己的判据；scale 转换使用上游的逐元素与步长检查。`sleep_impl` 没有数学输出，只检查可执行和同步，不应当成数值精度测试。

检查前后目标 API 输入摘要一致、目标二进制与 JIT cache 匹配、7 张 Default 表及原始文件存在，并保存逐文件 SHA-256，才记 `passed`。环境与 `../pilot-quant/runs/quant-environment.json` 相同。执行源码的 `tests/generators.py`、`tests/test_attention.py`、`tests/test_layout.py` 来自固定提交，并非本脚本重写的参考。采集期间 `kernel.json` 警告保留在原始日志中，指标是否适合作为规则依据仍需单独验证。

在 hidev 激活 `/workspace/deepgemm-ascend-20261107/activate.sh`，并将 `ASCEND_HOME_PATH` 和 `BISHENG_HOME` 指向 `/workspace/deepgemm-ascend-20261107/cann-compat-quant` 后运行：

```
python -B campaign-13/collect.py batch --source source --output NEW_OUTPUT --cache-root NEW_CACHE --device 0 --case CASE_ID
```

MegaMoE 所要求的 32 Cube 核与本机 28 核不符；不要伪造核数或将修改后的结果误当成原版专家数据。
