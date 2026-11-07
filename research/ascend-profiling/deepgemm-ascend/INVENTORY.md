# DeepGEMM-Ascend 代码入口与 kernel 清点

清点对象：`3a35326271b069b8b5bf1a754435acd6cc91575b`。这些数字是不同口径，不能相加称作“算子总数”。

- `csrc/apis/gemm.hpp` 有 15 个直接定义的 GEMM Python 接口，以及 6 个别名。接口包含 BF16、FP8/FP4 和分组、不同转置布局；多个接口可以调用同一实现。
- `deep_gemm/include` 下按 C++ `__global__` 入口名统计，有 13 个不同名字，包含辅助 kernel 和测试用 `sleep_impl`；其中 `paged_mqa_logits_metadata_simt_impl` 有两个源码声明。另有一个 TileLang JIT 定义 `tf32_hc_prenorm_gemm_kernel`。这个统计不代表 14 个独立算子，也不是运行时二进制总数。
  13 个名字分别是 `bf16_gemm_impl`、`fp8_gemm_impl`、`fp8_dequant_gemm_impl`、`mega_moe_impl`、`mqa_logits_impl`、`paged_mqa_logits_impl`、`paged_mqa_logits_metadata_simt_impl`、`paged_sparse_mqa_logits_impl`、`paged_sparse_mqa_prepare_impl`、`sleep_impl`、`sparse_mqa_logits_impl`、`sparse_mqa_logits_metadata`、`transform_sf`。
- GEMM 主体包含 `bf16_gemm_impl`、`fp8_gemm_impl`、`fp8_dequant_gemm_impl`。FP8×FP8 和 FP4×FP4 使用 `fp8_gemm_impl` 的不同特化；FP8×FP4 使用 `fp8_dequant_gemm_impl`。形状、dtype、layout 等会产生多个 JIT 特化。
- 代码还包括 `mega_moe_impl`、MQA logits、稀疏 MQA logits 和分页版本，以及 scale 转换、元数据等辅助 kernel。运行时具体是 Cube 还是混合执行，以每个实际 profile 的 Op Type 和指标为准。

最初六个 BF16 输入 case 均属于 `bf16_gemm_impl` 的不同特化，其中 4 个 BF16 输出、2 个 FP32 输出，并不覆盖这些其他实现。`pilot-quant` 补充低精度主 GEMM 的小批可重复测试，未覆盖所有接口、layout、grouped 或其他模型算子。
