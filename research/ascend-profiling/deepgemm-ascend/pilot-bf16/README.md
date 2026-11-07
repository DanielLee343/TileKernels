# DeepGEMM-Ascend BF16 普通 GEMM 小批试采

固定官方源码 `3a35326271b069b8b5bf1a754435acd6cc91575b`。`cases.json` 的 6 个形状和输出 dtype 均来自 `tests/generators.py:_enumerate_normal` 的 forward 部分。合同为 BF16 输入、`A[M,K] @ B[N,K].T`、无 bias、无累加，分别覆盖 BF16 和 FP32 输出。该批只有一个专家源码来源，不能将 6 个 case 当作 6 个独立实现或直接生成阈值。

输入使用 case 自带固定 seed 在 CPU 上生成正态随机值并转换为 BF16；与官方 shape 相同，但随机生成设备及数值不宣称与上游测试逐字节相同。参考是 CPU 上将 BF16 输入转为 FP32 计算矩阵乘，再转为输出 dtype；精度指标沿用上游 `tests/utils.py:calc_diff`，finite 检查通过且 diff < 1e-5。输出和输入哈希在普通运行与 profile 运行之间比较。结果在同样的输入上判断，不能推断所有数值范围的正确性。

先 source `/workspace/deepgemm-ascend-20261107/activate.sh`，在 hidev 上运行：

```bash
python -B collect.py batch --source /workspace/deepgemm-ascend-20261107/source --output /absolute/path/to/new-output --device 0
```

每个 case 前检查设备空闲，先执行并校验参考，再用 `msprof op --aic-metrics=Default --replay-mode=kernel --mstx=true --mstx-include=deepgemm_target --launch-count=1 --warm-up=5` 采集；脚本本身也有 5 次预热。脚本要求目标 kernel 唯一、Cube 或 mix 身份、非零 Cube 活动、Default 指标表及原始设备文件存在，且捕获设备二进制与 JIT 缓存对应。检查每个 case 普通执行和 profiler 执行结束时输出，不宣称逐次检查 profiler 内部各次重放。非零退出、精度失败、捕获不完整均记录为失败。

归档完成后运行 `python -B verify.py`，独立核对 case 合同、精度状态、输入输出哈希、kernel 类型和全部原始文件哈希。每次程序实际检查的输出元素数及最大绝对误差保存在 `prepare.json`、`profile.json`；相似度指标为零并不等于逐元素完全相等。

环境使用隔离的 CANN 头文件兼容路径和 Bisheng `-U__cpp_concepts` 参数，详见此前 smoke 的 `outputs/deepgemm-ascend-hidev-20261107/README.md`。profile 的 `kernel.json` 缺失警告需保留；原始计数的精确含义和质量仍需后续核查。本批不会据此发布专家 threshold。
