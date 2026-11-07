# 低精度 GEMM 采集试点

`cases.json` 固定 FP8×FP8、FP4×FP4、FP8×FP4 的 NT GEMM 输入；每种四个形状、BF16 输出，不带 bias、accumulation。第一次试点使用的 6 项清单保存在 `cases-initial.json`。使用上游 `tests/generators.py` 的生成器和固定种子生成量化输入与 scale，参考结果由该生成器在 NPU 上用反量化的 FP32 矩阵乘得到，再转 BF16；使用上游 `calc_diff` 同一公式、`<1e-5` 判据。这是精度检查，不是性能参考实现。

在既有 hidev 环境中激活 `/workspace/deepgemm-ascend-20261107/activate.sh`，将 `ASCEND_HOME_PATH` 和 `BISHENG_HOME` 指向隔离的 `cann-compat-quant`；后者在原有兼容编译器参数基础上，显式引入 CANN 的 `utils/debug/asc_assert.h`，解决低精度 scale 转换源码缺少声明的问题。具体内容及 SHA-256 参见记录。运行：

```
python -B pilot-quant/collect.py batch --source source --output OUTPUT --cache-root CACHE --device 0
```

每个 case 有独立 JIT cache，应用预热 5 次，再以 `msprof op --aic-metrics=Default --replay-mode=kernel --warm-up=5` 采集。MSTX 范围与目标 kernel 的名称通配符一起过滤，避免把 scale 的辅助 kernel 当成目标 GEMM；以采集到的 ELF 哈希与目标缓存 ELF 比对确认身份。采集前后校验输入、参考结果、输出、目标 ELF 哈希，保存 raw 文件和判据；两阶段均通过、数据完整才记成功。该试点不声称覆盖全部辅助 kernel 或适用于其他平台。
