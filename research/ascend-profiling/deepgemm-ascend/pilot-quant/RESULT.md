# 低精度 GEMM 采集结果

2026-11-07，hidev 950PR，DeepGEMM-Ascend `3a35326271b069b8b5bf1a754435acd6cc91575b`；输入及采集范围见 `README.md`、`cases.json`。FP8×FP8、FP4×FP4、FP8×FP4 各 4 个形状，共 12 个 case 全部采集成功。按 profiler 的实际分类为 6 个 Cube、6 个 Mix；同一 dtype 对不同形状可能选择不同类型。

每个 case 的准备阶段与采集阶段均通过上游测试采用的 cosine-like 差异 `<1e-5`、有限值检查；输入、参考、输出和目标二进制的哈希前后相同。12 个结果共 228 个 profile 文件重新计算 SHA-256，与采集记录一致。该差异值为 0 不等于每个输出元素完全一致；逐 case 的 `max_abs_error` 也保存在 `prepare.json` 和 `profile.json` 中。

原始数据位于 `runs/quant-fourth-20261107`、`runs/quant-rest-20261107`、`runs/quant-expanded-20261107`。前两批分别使用 `cases-initial.json`，最后一批使用 `cases.json`；各批记录的清单和脚本 SHA-256 已比对。精确编译环境在 `runs/quant-environment.json`；没有修改上游 kernel 源码。三次排障失败及其日志也保留在 `runs/quant-first-20261107` 到 `runs/quant-third-20261107`，不计为成功数据。

这些采集仍会出现缺 `kernel.json` 警告；BF16 对照结果不直接证明低精度字段准确。这里证明的是运行成功、精度判据通过、采集文件完整且二进制身份匹配；各指标是否适合作为规则依据仍要逐字段验证。未测试 grouped、其他 layout、MoE 和 MQA。
