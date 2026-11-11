# HiDev 专家算子补采复核

两份本地 Excel 各收录 1,290 个目标，使用原版 TileKernels 和 DeepGEMM-Ascend。`targets.csv` 有全部 1,301 个登记目标。`not-in-workbooks.csv` 列出 11 个表外目标。

- `moe-topk-original-store-20261111.tar.gz` 包含 20 个 MoE TopK 前向在 HiDev 的同输入正确性记录、生成源码、搬出计算和逐核核对。保留原 Default 采集的计时和原始字段。搬出计算使用原二进制和逐核 MTE3 指令数核验。
- `official-precision-reference-20261111.tar.gz` 包含 9 个 mHC pre-apply 后向和 3 个 Normalize 的同输入参考复核。9 个 mHC 的融合乘加参考通过。3 个 Normalize 的分母对照 FP64 参考仍超出官方容差。已核对搬出数据在相邻 `precision-preapply-batch/` 和 `precision-preapply10-smoke/`。
- `official-post04-reference-20261111.tar.gz` 和 `fused-upstream-original-store-20261111.tar.gz` 补足原表两个窗口。mHC post 04 的 NPU 分块参考通过，CPU 参考失败。`fused-h3584` 的原版二进制、生成源码和逐核指令数支持每核 1,024 B 搬出。
- HiDev 的 28 个 Cube 核无法满足固定上游 MegaMoE 的 32 核要求。4 个原版目标和对应的 4 个适配目标均未入表。表内 8 个分页稀疏 MQA REUSE 还缺可绑定历史窗口的搬出量。

`official-followup-20261111.json` 记录在 PC 取数时的本地证据路径。`SHA256.json` 记录此目录文件的 SHA-256。
