# 13 个 DeepGEMM-Ascend C++ kernel 采集

入口清单和状态在 `STATUS.md`。`cases-initial.json`／`collect-initial.py` 对应首轮，`cases-expanded.json`／`collect-expanded.py` 对应 97-case 扩展轮；`cases-next-first.json`／`collect-next-first.py` 对应首次调用试点，`cases-next.json`／`collect.py` 包含下一批大 M、FP32 输出、首次调用和分组布局。每项 case 记录目标 kernel、调用入口、dtype、形状、布局与参数。不同目标可能使用同一算子输入，不能作为不同专家来源。

`cases-last.json`／`collect-last.py` 对应 head_dim=64 的连续 MQA 和 8 组 M-group GEMM；它们已采集。当前 `collect.py` 增加了可选择的 replay 模式和 profiler 子进程错误检查，`cases-last.json`／`collect.py` 对应 3 次 range replay 复采。

FIRST 和分组试点已在 hidev 通过；28 核适配是与原版分开的实验，不自动视为原版专家实现。

各版脚本均读取同目录的 `cases.json`。重跑或运行某批时，应在与 `pilot-bf16` 并列的隔离工作目录中，把该批清单复制为 `cases.json`，并执行同一批的脚本；不要在另一批正在运行时替换其清单或脚本。运行记录中的 SHA-256 可用于检查版本。

脚本调用上游的 GEMM、MQA、稀疏 MQA、layout 测试及其参考，先运行精度或语义检查，再调用 `msprof op --aic-metrics=Default --replay-mode=kernel`；目标 API 前预热 5 次，MSTX 范围与目标 kernel 名称过滤锁定采集对象。GEMM 采用上游 `GemmTestDesc` 参考和 cosine-like 差异 `<1e-5`；MQA 和稀疏 MQA 使用上游自己的判据；scale 转换使用上游的逐元素与步长检查。`sleep_impl` 没有数学输出，只检查可执行和同步，不应当成数值精度测试。

记录中的 `seed=7711` 是进入上游测试之前设置的全局种子。GEMM 的上游 `GemmTestDesc.generate()` 随后调用 `reset_seed()` 并重置为 0；所以 GEMM 输入实际使用的是上游种子 0，输入数据哈希仍以各 case 保存的记录为准。

检查前后目标 API 输入摘要一致、目标二进制与 JIT cache 匹配、7 张 Default 表及原始文件存在，并保存逐文件 SHA-256，才记 `passed`。环境与 `../pilot-quant/runs/quant-environment.json` 相同。执行源码的 `tests/generators.py`、`tests/test_attention.py`、`tests/test_layout.py` 来自固定提交，并非本脚本重写的参考。采集期间 `kernel.json` 警告保留在原始日志中，指标是否适合作为规则依据仍需单独验证。

分页稀疏 MQA 的 metadata 首次调用后会转成复用状态。首轮及 97-case 扩展轮中，应用预热先触发首次调用，因此采到的是复用状态；其旧版脚本保存的是预热前的 API 参数摘要，不能把它描述为采集时 metadata 的字节摘要。新增的 `first` case 使用独立 metadata 预热，并以未使用的 metadata 执行被采样调用，核对实际为 FIRST；对 metadata 本身记录形状及其构造参数，不把未初始化的 buffer 字节作为稳定输入。FIRST 与 REUSE 分开分析。

在 hidev 激活 `/workspace/deepgemm-ascend-20261107/activate.sh`，并将 `ASCEND_HOME_PATH` 和 `BISHENG_HOME` 指向 `/workspace/deepgemm-ascend-20261107/cann-compat-quant` 后运行：

```
python -B campaign-13/collect.py batch --source source --output NEW_OUTPUT --cache-root NEW_CACHE --device 0 --case CASE_ID
```

默认是 kernel replay；需要复现单独的 range replay case 时，追加 `--replay-mode range`。两种结果需按 replay 模式分别使用。

MegaMoE 所要求的 32 Cube 核与本机 28 核不符；不要伪造核数或将修改后的结果误当成原版专家数据。

隔离 28 核适配实验的 4 个 case、采集口径、失败尝试和复现命令见 `MEGAMOE_28_EXPERIMENT.md`。数据独立存放在 `runs/mega-port28-experiment`，以 `python -B campaign-13/verify_mega_port.py` 验证，不并入原版专家数据。
