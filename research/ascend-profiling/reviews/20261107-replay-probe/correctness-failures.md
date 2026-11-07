# 13 条采集准备阶段的精度检查失败

这些 case 的算子输出未通过当时的参考值比较，均在准备阶段停止，未取得正式 Default profile。不能据此断定 TileKernels 上游测试会失败或 kernel 一定有缺陷。

## 3 条 MoE normalize

原适配器在 CPU 生成输入，并以 PyTorch 计算每行分母 `sum(weights)` 和归一化权重 `weights / sum(weights)`。两个输出各按最大绝对误差不超过 `2e-6` 检查。三条均是分母超差，权重通过：

| Case | 输入形状 | 分母最大绝对误差 | 权重最大绝对误差 |
|---|---|---:|---:|
| normalize-03 | 127 × 32 | 3.8146973e-6 | 1.4901161e-8 |
| normalize-16 | 128 × 32 | 3.8146973e-6 | 2.2351742e-8 |
| normalize-20 | 4001 × 32 | 5.7220459e-6 | 2.2351742e-8 |

上游测试在目标设备上生成输入并在同一设备计算参考，容差相同。两者输入及参考计算设备并不相同，现有证据不足以确定超差根因。原记录位于 `runs/hidev-20261106-starter/cases/normalize-{03,16,20}/prepare.json`。

## 9 条 mHC pre-apply backward

这些 case 使用 CPU PyTorch 自动求导，按 64 个 token 分块计算梯度参考，再加上非零的原始梯度；其中一次遇到不满足 `atol=1e-2, rtol=1e-3` 的比较即停止。每条报出的第一个失败块各有 1 个元素不满足检查，绝对差均为 `0.015625`；由于遇错即停，这不是整个 case 的失败元素总数。上游测试采用零初始梯度和 NPU 上的 PyTorch 自动求导，与本次检查条件不同。不能仅由这些结果断言上游测试失败或推断具体根因。

对应 case：`mhc_pre_apply_mix_bwd-02,04,06,09,10,11,12,14,18`，原记录位于 `runs/hidev-20261106-unified-extra4/cases/`。

## 1 条 mHC post backward

`mhc_post_bwd-04` 将 kernel 输出与 CPU PyTorch 自动求导产生的参考分块比较；首次失败的输出块有 1 / 1024 个元素不满足 `atol=1e-4, rtol=1e-4`，报告最大绝对误差约 `0.0001173`。这里也不能从首个失败块推断全量错误数量。上游测试使用 NPU 上的 PyTorch 自动求导和完整输入；两种参考计算路径不同，根因尚未确认。原记录位于 `runs/hidev-20261106-unified-extra2/cases/mhc_post_bwd-04/prepare.json`。
