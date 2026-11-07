# FP4 分页稀疏 FIRST：profile 后复用检查失败

case：`paged-sparse-first-1-q4-k256-h8-b8-p64`，同一源码、输入及目标二进制 SHA-256 `44eb4fbc082f63f2c924946ec8e6ec69ed77623f707d9625b08c849fee7fd9a2`。首次采集和三次同条件复测中，普通执行均通过上游检查；Default kernel replay 后，上游比较首次结果与后续 REUSE 结果时均失败。四次准备阶段的目标输入摘要一致。即使 msprof 退出码为 0 并生成报表，也不能将子进程失败当成成功。

诊断时保留上游断言，在 `torch.equal` 失败时记录差异：kernel replay 的 profiler 预热分别设为 5 和 0，均有 512 个有效值中的 511 个不一致，最大绝对差为 93，平均绝对差约 16.11。更换为 application replay 后，日志中仍有一次子进程同样失败；虽然其他子运行通过、最终 `profile.json` 存在且工具返回 0，也不能据此将该轮判为通过。二进制哈希均与原始失败一致。

目前证据表明带 profiler 执行与普通执行的后续复用行为不同；尚未证明具体是哪个重放、缓存或数据恢复环节导致。该 case 的上述报表保留为失败诊断证据，不进入有效 profile 集。其他 shape 的 FP4 FIRST 通过不证明本 case 通过。原始日志、数据和校验清单位于 `runs/campaign-next-rest`、`runs/campaign-first-retry-*`、`runs/campaign-first-diagnostics` 及 `diagnostic-file-hashes.json`。

额外对照：在 FIRST 返回后直接读取 metadata。普通运行和 profiler 运行的 metadata 前 86,016 B 一致；紧凑 KV 区域在普通运行含 23,999 个非零字节，在 kernel replay 运行后全零。该探针在返回后同步并读取 metadata，既未改 kernel 也未取消上游检查；其结果解释了后续 REUSE 输出全零，但尚未定位 profiler 内部原因。

同一输入和二进制使用 Default 的 **range replay**，首次诊断及常规采集脚本的 3 次复采均通过上游检查，7 张指标表生成，目标 ELF SHA-256 相同，输入摘要一致。3 次是同一个 case 的复采，不是 3 个独立样本。range replay 与 kernel replay 是不同采集口径，必须单独标记，不能直接与 kernel replay 样本混同。正式复采在 `runs/campaign-range-repeat-1` 至 `-3`。
