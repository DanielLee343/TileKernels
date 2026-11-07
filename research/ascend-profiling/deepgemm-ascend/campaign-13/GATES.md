# 13 个 C++ kernel 采集验收

源版本：`3a35326271b069b8b5bf1a754435acd6cc91575b`；设备：hidev 950PR。已有 profile 可纳入，但必须保留可核对的 case、精度和 raw 证据。

1. 逐个登记原始清点中的 13 个 kernel，记录上游入口、支持的 dtype/layout、可复现的 case 与状态；不支持的组合记录原因，不伪造覆盖。
2. 每个可执行 kernel 至少有一条明确识别目标二进制、有效性／精度通过、Default raw 完整的 profile；对可变 dtype、shape、layout 扩展多个有代表性的 case。辅助 kernel 的验证方式按其实际输出定义。
3. 每条 profile 记录源码、设备、环境、输入、采集范围和结果；失败保留日志并定位，不将失败或辅助测试算成独立成功样本。
4. 清点检查每个 kernel 与 case 的证据，核对 raw SHA-256；向私仓同步可复现脚本、清单、结果及适合存储的原始数据，并核对远端提交。

在运行中持续更新 `STATUS.md`，不以启动脚本或无数据的 profiler 退出码作为通过。
