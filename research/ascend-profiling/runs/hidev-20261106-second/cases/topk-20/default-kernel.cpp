#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void topk_gate_kernel_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem) {
  vector_bool mask = asc_create_mask_b32(PAT_ALL);
  auto vreg_0 = simd_inst::vdup<int32_t>(0, mask, MODE_ZEROING);
  for (int32_t vchunk = 0; vchunk < 6; ++vchunk) {
    simd_inst::vsts_norm(vreg_0, (__ubuf__ int32_t*)(&(((__ubuf__ int32_t*)buf_dyn_shmem)[((vchunk * 64) + 6912)])), 0, mask);
  }
  vector_bool mask_1 = asc_create_mask_b32(PAT_ALL);
  auto vreg_0_1 = simd_inst::vdup<int32_t>(0, mask_1, MODE_ZEROING);
  simd_inst::vsts_norm(vreg_0_1, (__ubuf__ int32_t*)(&(((__ubuf__ int32_t*)buf_dyn_shmem)[7296])), 0, mask_1);
}

__simd_vf__ inline void topk_gate_kernel_asc_kernel_simd_vf_1(__ubuf__ uint8_t* buf_dyn_shmem, int32_t scores_ub_version_counter_1) {
  vector_f32 scores_vec[6];
  vector_s32 index_vec[6];
  vector_s32 tmp_idx_vec[6];
  vector_s32 invalid;
  vector_f32 acc;
  vector_s32 acc_idx;
  vector_bool mask_32b = asc_create_mask_b32(PAT_ALL);
  vector_bool one = asc_create_mask_b32(PAT_VL1);
  auto neg_inf = simd_inst::vdup<float>(tl::limits::kFloatNInf, mask_32b, MODE_ZEROING);
  auto int_max = simd_inst::vdup<int32_t>(2147483647, mask_32b, MODE_ZEROING);
  auto lanes = simd_inst::vci<int32_t>(0, INC_ORDER);
  vector_bool v = asc_create_mask_b32(PAT_ALL);
  auto zero = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v, MODE_ZEROING);
  auto zeros = simd_inst::vdup<int32_t>(0, v, MODE_ZEROING);
  invalid = simd_inst::vlds_norm<int32_t>((__ubuf__ int32_t*)(&(((__ubuf__ int32_t*)buf_dyn_shmem)[7296])), 0);
  auto valid = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 0, v, MODE_ZEROING), 1025, v);
  auto logit = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152))])), 0), zero, valid);
  auto nonfinite = simd_inst::vcmps_ne(simd_inst::vsub(logit, logit, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite), v, MODE_ZEROING);
  auto valid_1 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 64, v, MODE_ZEROING), 1025, v);
  auto logit_1 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 64)])), 0), zero, valid_1);
  auto nonfinite_1 = simd_inst::vcmps_ne(simd_inst::vsub(logit_1, logit_1, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_1), v, MODE_ZEROING);
  auto valid_2 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 128, v, MODE_ZEROING), 1025, v);
  auto logit_2 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 128)])), 0), zero, valid_2);
  auto nonfinite_2 = simd_inst::vcmps_ne(simd_inst::vsub(logit_2, logit_2, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_2), v, MODE_ZEROING);
  auto valid_3 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 192, v, MODE_ZEROING), 1025, v);
  auto logit_3 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 192)])), 0), zero, valid_3);
  auto nonfinite_3 = simd_inst::vcmps_ne(simd_inst::vsub(logit_3, logit_3, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_3), v, MODE_ZEROING);
  auto valid_4 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 256, v, MODE_ZEROING), 1025, v);
  auto logit_4 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 256)])), 0), zero, valid_4);
  auto nonfinite_4 = simd_inst::vcmps_ne(simd_inst::vsub(logit_4, logit_4, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_4), v, MODE_ZEROING);
  auto valid_5 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 320, v, MODE_ZEROING), 1025, v);
  auto logit_5 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 320)])), 0), zero, valid_5);
  auto nonfinite_5 = simd_inst::vcmps_ne(simd_inst::vsub(logit_5, logit_5, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_5), v, MODE_ZEROING);
  auto valid_6 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 384, v, MODE_ZEROING), 1025, v);
  auto logit_6 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 384)])), 0), zero, valid_6);
  auto nonfinite_6 = simd_inst::vcmps_ne(simd_inst::vsub(logit_6, logit_6, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_6), v, MODE_ZEROING);
  auto valid_7 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 448, v, MODE_ZEROING), 1025, v);
  auto logit_7 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 448)])), 0), zero, valid_7);
  auto nonfinite_7 = simd_inst::vcmps_ne(simd_inst::vsub(logit_7, logit_7, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_7), v, MODE_ZEROING);
  auto valid_8 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 512, v, MODE_ZEROING), 1025, v);
  auto logit_8 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 512)])), 0), zero, valid_8);
  auto nonfinite_8 = simd_inst::vcmps_ne(simd_inst::vsub(logit_8, logit_8, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_8), v, MODE_ZEROING);
  auto valid_9 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 576, v, MODE_ZEROING), 1025, v);
  auto logit_9 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 576)])), 0), zero, valid_9);
  auto nonfinite_9 = simd_inst::vcmps_ne(simd_inst::vsub(logit_9, logit_9, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_9), v, MODE_ZEROING);
  auto valid_10 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 640, v, MODE_ZEROING), 1025, v);
  auto logit_10 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 640)])), 0), zero, valid_10);
  auto nonfinite_10 = simd_inst::vcmps_ne(simd_inst::vsub(logit_10, logit_10, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_10), v, MODE_ZEROING);
  auto valid_11 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 704, v, MODE_ZEROING), 1025, v);
  auto logit_11 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 704)])), 0), zero, valid_11);
  auto nonfinite_11 = simd_inst::vcmps_ne(simd_inst::vsub(logit_11, logit_11, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_11), v, MODE_ZEROING);
  auto valid_12 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 768, v, MODE_ZEROING), 1025, v);
  auto logit_12 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 768)])), 0), zero, valid_12);
  auto nonfinite_12 = simd_inst::vcmps_ne(simd_inst::vsub(logit_12, logit_12, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_12), v, MODE_ZEROING);
  auto valid_13 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 832, v, MODE_ZEROING), 1025, v);
  auto logit_13 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 832)])), 0), zero, valid_13);
  auto nonfinite_13 = simd_inst::vcmps_ne(simd_inst::vsub(logit_13, logit_13, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_13), v, MODE_ZEROING);
  auto valid_14 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 896, v, MODE_ZEROING), 1025, v);
  auto logit_14 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 896)])), 0), zero, valid_14);
  auto nonfinite_14 = simd_inst::vcmps_ne(simd_inst::vsub(logit_14, logit_14, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_14), v, MODE_ZEROING);
  auto valid_15 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 960, v, MODE_ZEROING), 1025, v);
  auto logit_15 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 960)])), 0), zero, valid_15);
  auto nonfinite_15 = simd_inst::vcmps_ne(simd_inst::vsub(logit_15, logit_15, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_15), v, MODE_ZEROING);
  auto valid_16 = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 1024, v, MODE_ZEROING), 1025, v);
  auto logit_16 = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + 1024)])), 0), zero, valid_16);
  auto nonfinite_16 = simd_inst::vcmps_ne(simd_inst::vsub(logit_16, logit_16, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite_16), v, MODE_ZEROING);
  simd_inst::vsts_norm(simd_inst::vcmax(invalid, v, MODE_ZEROING), (__ubuf__ int32_t*)(&(((__ubuf__ int32_t*)buf_dyn_shmem)[7296])), 0, one);
  auto num_exp = simd_inst::vdup<int32_t>(1025, mask_32b, MODE_ZEROING);
  for (int32_t k = 0; k < 32; ++k) {
    acc = neg_inf;
    for (int32_t group_id = 0; group_id < 3; ++group_id) {
      index_vec[0] = simd_inst::vci<int32_t>((group_id * 384), INC_ORDER);
      scores_vec[0] = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id * 384))])), 0), neg_inf, simd_inst::vcmp_lt(index_vec[0], num_exp, mask_32b));
      index_vec[1] = simd_inst::vci<int32_t>(((group_id * 384) + 64), INC_ORDER);
      scores_vec[1] = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id * 384)) + 64)])), 0), neg_inf, simd_inst::vcmp_lt(index_vec[1], num_exp, mask_32b));
      index_vec[2] = simd_inst::vci<int32_t>(((group_id * 384) + 128), INC_ORDER);
      scores_vec[2] = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id * 384)) + 128)])), 0), neg_inf, simd_inst::vcmp_lt(index_vec[2], num_exp, mask_32b));
      index_vec[3] = simd_inst::vci<int32_t>(((group_id * 384) + 192), INC_ORDER);
      scores_vec[3] = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id * 384)) + 192)])), 0), neg_inf, simd_inst::vcmp_lt(index_vec[3], num_exp, mask_32b));
      index_vec[4] = simd_inst::vci<int32_t>(((group_id * 384) + 256), INC_ORDER);
      scores_vec[4] = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id * 384)) + 256)])), 0), neg_inf, simd_inst::vcmp_lt(index_vec[4], num_exp, mask_32b));
      index_vec[5] = simd_inst::vci<int32_t>(((group_id * 384) + 320), INC_ORDER);
      scores_vec[5] = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id * 384)) + 320)])), 0), neg_inf, simd_inst::vcmp_lt(index_vec[5], num_exp, mask_32b));
      acc = simd_inst::vmax(acc, scores_vec[0], mask_32b, MODE_ZEROING);
      acc = simd_inst::vmax(acc, scores_vec[1], mask_32b, MODE_ZEROING);
      acc = simd_inst::vmax(acc, scores_vec[2], mask_32b, MODE_ZEROING);
      acc = simd_inst::vmax(acc, scores_vec[3], mask_32b, MODE_ZEROING);
      acc = simd_inst::vmax(acc, scores_vec[4], mask_32b, MODE_ZEROING);
      acc = simd_inst::vmax(acc, scores_vec[5], mask_32b, MODE_ZEROING);
    }
    auto mx = simd_inst::vdupv(simd_inst::vcmax(acc, mask_32b, MODE_ZEROING), mask_32b, POS_LOWEST, MODE_ZEROING);
    acc_idx = int_max;
    for (int32_t group_id_1 = 0; group_id_1 < 3; ++group_id_1) {
      index_vec[0] = simd_inst::vci<int32_t>((group_id_1 * 384), INC_ORDER);
      scores_vec[0] = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_1 * 384))])), 0), neg_inf, simd_inst::vcmp_lt(index_vec[0], num_exp, mask_32b));
      tmp_idx_vec[0] = simd_inst::vsel(index_vec[0], int_max, simd_inst::vcmp_eq(scores_vec[0], mx, mask_32b));
      index_vec[1] = simd_inst::vci<int32_t>(((group_id_1 * 384) + 64), INC_ORDER);
      scores_vec[1] = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_1 * 384)) + 64)])), 0), neg_inf, simd_inst::vcmp_lt(index_vec[1], num_exp, mask_32b));
      tmp_idx_vec[1] = simd_inst::vsel(index_vec[1], int_max, simd_inst::vcmp_eq(scores_vec[1], mx, mask_32b));
      index_vec[2] = simd_inst::vci<int32_t>(((group_id_1 * 384) + 128), INC_ORDER);
      scores_vec[2] = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_1 * 384)) + 128)])), 0), neg_inf, simd_inst::vcmp_lt(index_vec[2], num_exp, mask_32b));
      tmp_idx_vec[2] = simd_inst::vsel(index_vec[2], int_max, simd_inst::vcmp_eq(scores_vec[2], mx, mask_32b));
      index_vec[3] = simd_inst::vci<int32_t>(((group_id_1 * 384) + 192), INC_ORDER);
      scores_vec[3] = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_1 * 384)) + 192)])), 0), neg_inf, simd_inst::vcmp_lt(index_vec[3], num_exp, mask_32b));
      tmp_idx_vec[3] = simd_inst::vsel(index_vec[3], int_max, simd_inst::vcmp_eq(scores_vec[3], mx, mask_32b));
      index_vec[4] = simd_inst::vci<int32_t>(((group_id_1 * 384) + 256), INC_ORDER);
      scores_vec[4] = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_1 * 384)) + 256)])), 0), neg_inf, simd_inst::vcmp_lt(index_vec[4], num_exp, mask_32b));
      tmp_idx_vec[4] = simd_inst::vsel(index_vec[4], int_max, simd_inst::vcmp_eq(scores_vec[4], mx, mask_32b));
      index_vec[5] = simd_inst::vci<int32_t>(((group_id_1 * 384) + 320), INC_ORDER);
      scores_vec[5] = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_1 * 384)) + 320)])), 0), neg_inf, simd_inst::vcmp_lt(index_vec[5], num_exp, mask_32b));
      tmp_idx_vec[5] = simd_inst::vsel(index_vec[5], int_max, simd_inst::vcmp_eq(scores_vec[5], mx, mask_32b));
      acc_idx = simd_inst::vmin(acc_idx, tmp_idx_vec[0], mask_32b, MODE_ZEROING);
      acc_idx = simd_inst::vmin(acc_idx, tmp_idx_vec[1], mask_32b, MODE_ZEROING);
      acc_idx = simd_inst::vmin(acc_idx, tmp_idx_vec[2], mask_32b, MODE_ZEROING);
      acc_idx = simd_inst::vmin(acc_idx, tmp_idx_vec[3], mask_32b, MODE_ZEROING);
      acc_idx = simd_inst::vmin(acc_idx, tmp_idx_vec[4], mask_32b, MODE_ZEROING);
      acc_idx = simd_inst::vmin(acc_idx, tmp_idx_vec[5], mask_32b, MODE_ZEROING);
    }
    auto idx = simd_inst::vdupv(simd_inst::vcmin(acc_idx, mask_32b, MODE_ZEROING), mask_32b, POS_LOWEST, MODE_ZEROING);
    simd_inst::vsts_1st(idx, (__ubuf__ int32_t*)(&(((__ubuf__ int32_t*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 64) + ((scores_ub_version_counter_1 % 6) * 64)) + (k * 2)) + 6912)])), 0, one);
    for (int32_t group_id_2 = 0; group_id_2 < 3; ++group_id_2) {
      index_vec[0] = simd_inst::vci<int32_t>((group_id_2 * 384), INC_ORDER);
      scores_vec[0] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_2 * 384))])), 0);
      scores_vec[0] = simd_inst::vsel(neg_inf, scores_vec[0], simd_inst::vcmp_eq(index_vec[0], idx, mask_32b));
      simd_inst::vsts_norm(scores_vec[0], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_2 * 384))])), 0, mask_32b);
      index_vec[1] = simd_inst::vci<int32_t>(((group_id_2 * 384) + 64), INC_ORDER);
      scores_vec[1] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_2 * 384)) + 64)])), 0);
      scores_vec[1] = simd_inst::vsel(neg_inf, scores_vec[1], simd_inst::vcmp_eq(index_vec[1], idx, mask_32b));
      simd_inst::vsts_norm(scores_vec[1], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_2 * 384)) + 64)])), 0, mask_32b);
      index_vec[2] = simd_inst::vci<int32_t>(((group_id_2 * 384) + 128), INC_ORDER);
      scores_vec[2] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_2 * 384)) + 128)])), 0);
      scores_vec[2] = simd_inst::vsel(neg_inf, scores_vec[2], simd_inst::vcmp_eq(index_vec[2], idx, mask_32b));
      simd_inst::vsts_norm(scores_vec[2], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_2 * 384)) + 128)])), 0, mask_32b);
      index_vec[3] = simd_inst::vci<int32_t>(((group_id_2 * 384) + 192), INC_ORDER);
      scores_vec[3] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_2 * 384)) + 192)])), 0);
      scores_vec[3] = simd_inst::vsel(neg_inf, scores_vec[3], simd_inst::vcmp_eq(index_vec[3], idx, mask_32b));
      simd_inst::vsts_norm(scores_vec[3], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_2 * 384)) + 192)])), 0, mask_32b);
      index_vec[4] = simd_inst::vci<int32_t>(((group_id_2 * 384) + 256), INC_ORDER);
      scores_vec[4] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_2 * 384)) + 256)])), 0);
      scores_vec[4] = simd_inst::vsel(neg_inf, scores_vec[4], simd_inst::vcmp_eq(index_vec[4], idx, mask_32b));
      simd_inst::vsts_norm(scores_vec[4], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_2 * 384)) + 256)])), 0, mask_32b);
      index_vec[5] = simd_inst::vci<int32_t>(((group_id_2 * 384) + 320), INC_ORDER);
      scores_vec[5] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_2 * 384)) + 320)])), 0);
      scores_vec[5] = simd_inst::vsel(neg_inf, scores_vec[5], simd_inst::vcmp_eq(index_vec[5], idx, mask_32b));
      simd_inst::vsts_norm(scores_vec[5], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152)) + (group_id_2 * 384)) + 320)])), 0, mask_32b);
    }
    simd_inst::mem_bar(VST_VLD);
  }
}

extern "C" __global__ __vector__ void topk_gate_kernel_asc_kernel(__gm__ float* scores, __gm__ int64_t* topk_idx_view, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t scores_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(4));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(5));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(4));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(5));
  scores_ub_version_counter_1 = 0;
  topk_gate_kernel_asc_kernel_simd_vf_0(buf_dyn_shmem);
  asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(6));
  asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(6));
  for (int32_t w = 0; w < ((num_tokens + 55) / 56); ++w) {
    if (((w * 56) + ((int32_t)block_idx)) < num_tokens) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 1152) + ((scores_ub_version_counter_1 % 6) * 1152))]))), (__gm__ uint8_t*)((&(scores[((((int64_t)w) * (int64_t)57400) + (((int64_t)((int32_t)block_idx)) * (int64_t)1025))]))), 1, 4100, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 4100, 4100);
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      topk_gate_kernel_asc_kernel_simd_vf_1(buf_dyn_shmem, scores_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(((__gm__ int32_t*)topk_idx_view)[((((int64_t)w) * (int64_t)3584) + (((int64_t)((int32_t)block_idx)) * (int64_t)64))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ int32_t*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 64) + ((scores_ub_version_counter_1 % 6) * 64)) + 6912)]))), 1, 256, static_cast<asc_store_l2_cache_mode>(4), 256, 256);
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      scores_ub_version_counter_1 = (scores_ub_version_counter_1 + 1);
    }
  }
  asc_sync_notify(PIPE_V, PIPE_S, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_S, static_cast<event_t>(0));
  device_assert_with_msg((((__ubuf__ int32_t*)buf_dyn_shmem)[7296] == 0), "topk_gate input contains nan or inf!\n  at \/workspace\/tilekernels-env-20261101\/src\/TileKernels\/tile_kernels\/moe\/topk_gate_asc.py:155 in topk_gate_kernel_asc\n");
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(4));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(5));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(4));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(5));
}

