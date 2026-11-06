#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void topk_gate_kernel_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem) {
  vector_bool mask = asc_create_mask_b32(PAT_ALL);
  auto vreg_0 = simd_inst::vdup<int32_t>(0, mask, MODE_ZEROING);
  for (int32_t vchunk = 0; vchunk < 6; ++vchunk) {
    simd_inst::vsts_norm(vreg_0, (__ubuf__ int32_t*)(&(((__ubuf__ int32_t*)buf_dyn_shmem)[((vchunk * 64) + 384)])), 0, mask);
  }
  vector_bool mask_1 = asc_create_mask_b32(PAT_ALL);
  auto vreg_0_1 = simd_inst::vdup<int32_t>(0, mask_1, MODE_ZEROING);
  simd_inst::vsts_norm(vreg_0_1, (__ubuf__ int32_t*)(&(((__ubuf__ int32_t*)buf_dyn_shmem)[768])), 0, mask_1);
}

__simd_vf__ inline void topk_gate_kernel_asc_kernel_simd_vf_1(__ubuf__ uint8_t* buf_dyn_shmem, int32_t scores_ub_version_counter_1) {
  vector_f32 scores_vec[1];
  vector_s32 index_vec[1];
  vector_s32 tmp_idx_vec[1];
  vector_s32 invalid;
  vector_f32 acc_max;
  vector_s32 acc_min_idx;
  vector_bool mask_32b = asc_create_mask_b32(PAT_ALL);
  vector_bool one = asc_create_mask_b32(PAT_VL1);
  auto neg_inf = simd_inst::vdup<float>(tl::limits::kFloatNInf, mask_32b, MODE_ZEROING);
  auto int_max = simd_inst::vdup<int32_t>(2147483647, mask_32b, MODE_ZEROING);
  auto lanes = simd_inst::vci<int32_t>(0, INC_ORDER);
  vector_bool v = asc_create_mask_b32(PAT_ALL);
  auto zero = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v, MODE_ZEROING);
  auto zeros = simd_inst::vdup<int32_t>(0, v, MODE_ZEROING);
  invalid = simd_inst::vlds_norm<int32_t>((__ubuf__ int32_t*)(&(((__ubuf__ int32_t*)buf_dyn_shmem)[768])), 0);
  auto valid = simd_inst::vcmps_lt(simd_inst::vadds(lanes, 0, v, MODE_ZEROING), 35, v);
  auto logit = simd_inst::vsel(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 64) + ((scores_ub_version_counter_1 % 6) * 64))])), 0), zero, valid);
  auto nonfinite = simd_inst::vcmps_ne(simd_inst::vsub(logit, logit, v, MODE_ZEROING), float(0x0p+0f/*0.000000e+00*/), v);
  invalid = simd_inst::vmax(invalid, simd_inst::vsel(simd_inst::vdup<int32_t>(1, v, MODE_ZEROING), zeros, nonfinite), v, MODE_ZEROING);
  simd_inst::vsts_norm(simd_inst::vcmax(invalid, v, MODE_ZEROING), (__ubuf__ int32_t*)(&(((__ubuf__ int32_t*)buf_dyn_shmem)[768])), 0, one);
  scores_vec[0] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 64) + ((scores_ub_version_counter_1 % 6) * 64))])), 0);
  index_vec[0] = simd_inst::vci<int32_t>(0, INC_ORDER);
  auto num_exp = simd_inst::vdup<int32_t>(35, mask_32b, MODE_ZEROING);
  scores_vec[0] = simd_inst::vsel(scores_vec[0], neg_inf, simd_inst::vcmp_lt(index_vec[0], num_exp, mask_32b));
  for (int32_t k = 0; k < 9; ++k) {
    acc_max = scores_vec[0];
    auto mx = simd_inst::vdupv(simd_inst::vcmax(acc_max, mask_32b, MODE_ZEROING), mask_32b, POS_LOWEST, MODE_ZEROING);
    tmp_idx_vec[0] = simd_inst::vsel(index_vec[0], int_max, simd_inst::vcmp_eq(scores_vec[0], mx, mask_32b));
    acc_min_idx = tmp_idx_vec[0];
    auto idx = simd_inst::vdupv(simd_inst::vcmin(acc_min_idx, mask_32b, MODE_ZEROING), mask_32b, POS_LOWEST, MODE_ZEROING);
    simd_inst::vsts_1st(idx, (__ubuf__ int32_t*)(&(((__ubuf__ int32_t*)buf_dyn_shmem)[(((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 64) + ((scores_ub_version_counter_1 % 6) * 64)) + (k * 2)) + 384)])), 0, one);
    scores_vec[0] = simd_inst::vsel(neg_inf, scores_vec[0], simd_inst::vcmp_eq(index_vec[0], idx, mask_32b));
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
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 64) + ((scores_ub_version_counter_1 % 6) * 64))]))), (__gm__ uint8_t*)((&(scores[((((int64_t)w) * (int64_t)1960) + (((int64_t)((int32_t)block_idx)) * (int64_t)35))]))), 1, 140, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 140, 140);
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      topk_gate_kernel_asc_kernel_simd_vf_1(buf_dyn_shmem, scores_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(((__gm__ int32_t*)topk_idx_view)[((((int64_t)w) * (int64_t)1008) + (((int64_t)((int32_t)block_idx)) * (int64_t)18))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ int32_t*)buf_dyn_shmem)[((((6 & ((scores_ub_version_counter_1 % 6) >> 31)) * 64) + ((scores_ub_version_counter_1 % 6) * 64)) + 384)]))), 1, 72, static_cast<asc_store_l2_cache_mode>(4), 72, 72);
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(((6 & ((scores_ub_version_counter_1 % 6) >> 31)) + (scores_ub_version_counter_1 % 6))));
      scores_ub_version_counter_1 = (scores_ub_version_counter_1 + 1);
    }
  }
  asc_sync_notify(PIPE_V, PIPE_S, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_S, static_cast<event_t>(0));
  device_assert_with_msg((((__ubuf__ int32_t*)buf_dyn_shmem)[768] == 0), "topk_gate input contains nan or inf!\n  at \/workspace\/tilekernels-env-20261101\/src\/TileKernels\/tile_kernels\/moe\/topk_gate_asc.py:155 in topk_gate_kernel_asc\n");
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

