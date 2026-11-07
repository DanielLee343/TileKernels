# 13 个 C++ kernel 采集状态

开始：2026-11-07。以现有源码和 profile 为起点，逐项确认实际调用及采集。`待查` 不代表已知可用的全部 dtype 或 layout。

| kernel | 当前状态 | 下一步 |
|---|---|---|
| bf16_gemm_impl | 本批 14，另有先前 6 | 普通、M／K 分组，BF16／FP32 输出 |
| fp8_gemm_impl | 本批 28，另有先前 8 | FP8／FP4，普通、M／K 分组，BF16／FP32 输出 |
| fp8_dequant_gemm_impl | 本批 14，另有先前 4 | FP8×FP4，普通、M／K 分组，BF16／FP32 输出 |
| mega_moe_impl | 原版受 32 核要求阻塞 | 调查可验证的 28 核适配，不能冒充原版 |
| mqa_logits_impl | 10 通过 | FP8/FP4、64／128 通道、形状与有效范围 |
| paged_mqa_logits_impl | 8 通过 | FP8/FP4、页面格式与布局 |
| paged_mqa_logits_metadata_simt_impl | 8 通过 | batch、页面与布局 |
| paged_sparse_mqa_logits_impl | REUSE 8、FIRST 4 通过 | 其中 1 个 FIRST 使用 range replay 单独标记 |
| paged_sparse_mqa_prepare_impl | 8 通过 | FP8/FP4、稀疏块与页面 |
| sleep_impl | 4 通过 | 不同 cycles 与 marker；只检查完成和同步 |
| sparse_mqa_logits_impl | 8 通过 | FP8/FP4、稀疏块与形状 |
| sparse_mqa_logits_metadata | 8 通过 | FP8/FP4、稀疏块与形状 |
| transform_sf | 14 通过 | FP32/int16、major 与粒度 |

首例为固定源码，在 950PR 上使用上游测试检查输出后采集 Default；`sleep_impl` 无数值输出，不能称为精度通过。本目录 136 个不同 case 已通过检查（其中一个使用 range replay 并复采 3 次），另保留 MegaMoE 原版失败和同一个 FP4 FIRST case 的 4 次 kernel replay 失败；`verify.py` 核验了成功样本的 2646 个 raw 文件及 207 个诊断文件的 SHA-256。此前 GEMM 另有 18 个成功 case。

MegaMoE 原始入口的实测失败：`csrc/apis/mega_moe.hpp:159` 要求运行时 Cube 核数等于 `common.hpp` 的固定值 32；本机 950PR 为 28 Cube 核。不能通过设置软件核数绕过，因为该限制还参与 kernel 中的任务分配、同步和 buffer 布局。失败日志在服务器 `campaign-mega-first`。是否存在可证明正确的 28 核适配，另行调查；适配版本须与原版及专家样本严格区分。

新增 FP4 FIRST case `paged-sparse-first-1-q4-k256-h8-b8-p64`：非 profiler 执行通过上游正确性检查；使用 Default kernel replay 时子进程在上游后续复用结果一致性检查中失败。相同输入和二进制的三次复测均重现；预热 0 和 5 次均失败，application replay 有一次子运行失败。普通运行后 metadata 的紧凑 KV 区域有非零写入，而 profiler 运行后该区域全零；后续 REUSE 输出全零。改用 range replay 后，同一输入和二进制的 3 次复采均通过，作为单独口径保留。kernel replay 的失败报表仍不可准入，内部原因尚未确定，详见 `FIRST_REPLAY_ISSUE.md`。

已有 18 case 的 `kernel.json` warning 尚不能视为所有指标均正确；本任务保留 raw 数据，逐字段的研究适用性另行验证。
