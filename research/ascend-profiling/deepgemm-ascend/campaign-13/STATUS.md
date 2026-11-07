# 13 个 C++ kernel 采集状态

开始：2026-11-07。以现有源码和 profile 为起点，逐项确认实际调用及采集。`待查` 不代表已知可用的全部 dtype 或 layout。

| kernel | 当前状态 | 下一步 |
|---|---|---|
| bf16_gemm_impl | 已有 6 case | 扩展布局、分组和形状 |
| fp8_gemm_impl | 已有 8 case | 扩展布局、分组和形状 |
| fp8_dequant_gemm_impl | 已有 4 case | 扩展布局、形状 |
| mega_moe_impl | 原版受 32 核要求阻塞 | 调查可验证的 28 核适配，不能冒充原版 |
| mqa_logits_impl | 首例通过 | 扩展 FP8/FP4、形状与有效范围 |
| paged_mqa_logits_impl | 首例通过 | 扩展页面格式与布局 |
| paged_mqa_logits_metadata_simt_impl | 首例通过 | 扩展 batch、页面与布局 |
| paged_sparse_mqa_logits_impl | 首例通过 | 扩展 FP8/FP4、稀疏块与页面 |
| paged_sparse_mqa_prepare_impl | 首例通过 | 扩展 FP8/FP4、稀疏块与页面 |
| sleep_impl | 首例通过 | 扩展 cycles 与 marker；只检查完成和同步 |
| sparse_mqa_logits_impl | 首例通过 | 扩展 FP8/FP4、稀疏块与形状 |
| sparse_mqa_logits_metadata | 首例通过 | 扩展 FP8/FP4、稀疏块与形状 |
| transform_sf | 首例通过 | 扩展 dtype、major 与粒度 |

首例为固定源码，在 950PR 上使用上游测试检查输出后采集 Default；`sleep_impl` 无数值输出，不能称为精度通过。附加 97 case 已在 hidev 串行采集。

MegaMoE 原始入口的实测失败：`csrc/apis/mega_moe.hpp:159` 要求运行时 Cube 核数等于 `common.hpp` 的固定值 32；本机 950PR 为 28 Cube 核。不能通过设置软件核数绕过，因为该限制还参与 kernel 中的任务分配、同步和 buffer 布局。失败日志在服务器 `campaign-mega-first`。是否存在可证明正确的 28 核适配，另行调查；适配版本须与原版及专家样本严格区分。

已有 18 case 的 `kernel.json` warning 尚不能视为所有指标均正确；本任务保留 raw 数据，逐字段的研究适用性另行验证。
