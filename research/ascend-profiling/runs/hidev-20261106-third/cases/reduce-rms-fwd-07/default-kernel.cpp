#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void mhc_reduce_partials_and_rmsnorm_fwd_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem) {
  vector_bool mask_full = asc_create_mask_b32(PAT_ALL);
  auto zero = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), mask_full, MODE_ZEROING);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1152])), 0, mask_full);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1216])), 0, mask_full);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1280])), 0, mask_full);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1344])), 0, mask_full);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1408])), 0, mask_full);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1472])), 0, mask_full);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[2496])), 0, mask_full);
  simd_inst::mem_bar(VST_VLD);
}

__simd_vf__ inline void mhc_reduce_partials_and_rmsnorm_fwd_asc_kernel_simd_vf_1(__ubuf__ uint8_t* buf_dyn_shmem, int32_t mul_ub_version_counter_1) {
  vector_f32 acc[6];
  vector_f32 acc_sq;
  vector_bool mask_full = asc_create_mask_b32(PAT_ALL);
  vector_bool mask_token = asc_create_mask_b32(PAT_VL16);
  acc[0] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1152])), 0);
  acc[1] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1216])), 0);
  acc[2] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1280])), 0);
  acc[3] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1344])), 0);
  acc[4] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1408])), 0);
  acc[5] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1472])), 0);
  acc_sq = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[2496])), 0);
  acc[0] = simd_inst::vadd(acc[0], simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((mul_ub_version_counter_1 % 3) >> 31)) * 384) + ((mul_ub_version_counter_1 % 3) * 384))])), 0), mask_full, MODE_ZEROING);
  acc[1] = simd_inst::vadd(acc[1], simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((mul_ub_version_counter_1 % 3) >> 31)) * 384) + ((mul_ub_version_counter_1 % 3) * 384)) + 64)])), 0), mask_full, MODE_ZEROING);
  acc[2] = simd_inst::vadd(acc[2], simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((mul_ub_version_counter_1 % 3) >> 31)) * 384) + ((mul_ub_version_counter_1 % 3) * 384)) + 128)])), 0), mask_full, MODE_ZEROING);
  acc[3] = simd_inst::vadd(acc[3], simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((mul_ub_version_counter_1 % 3) >> 31)) * 384) + ((mul_ub_version_counter_1 % 3) * 384)) + 192)])), 0), mask_full, MODE_ZEROING);
  acc[4] = simd_inst::vadd(acc[4], simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((mul_ub_version_counter_1 % 3) >> 31)) * 384) + ((mul_ub_version_counter_1 % 3) * 384)) + 256)])), 0), mask_full, MODE_ZEROING);
  acc[5] = simd_inst::vadd(acc[5], simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((mul_ub_version_counter_1 % 3) >> 31)) * 384) + ((mul_ub_version_counter_1 % 3) * 384)) + 320)])), 0), mask_full, MODE_ZEROING);
  acc_sq = simd_inst::vadd(acc_sq, simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((mul_ub_version_counter_1 % 3) >> 31)) * 64) + ((mul_ub_version_counter_1 % 3) * 64)) + 2304)])), 0), mask_token, MODE_ZEROING);
  simd_inst::vsts_norm(acc[0], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1152])), 0, mask_full);
  simd_inst::vsts_norm(acc[1], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1216])), 0, mask_full);
  simd_inst::vsts_norm(acc[2], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1280])), 0, mask_full);
  simd_inst::vsts_norm(acc[3], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1344])), 0, mask_full);
  simd_inst::vsts_norm(acc[4], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1408])), 0, mask_full);
  simd_inst::vsts_norm(acc[5], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1472])), 0, mask_full);
  simd_inst::vsts_norm(acc_sq, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[2496])), 0, mask_full);
  simd_inst::mem_bar(VST_VLD);
}

__simd_vf__ inline void mhc_reduce_partials_and_rmsnorm_fwd_asc_kernel_simd_vf_2(__ubuf__ uint8_t* buf_dyn_shmem) {
  vector_f32 final_sq_acc;
  vector_f32 rms_vec;
  vector_bool mask_full = asc_create_mask_b32(PAT_ALL);
  auto inv_rms_group_size = simd_inst::vdup<float>(float(0x1.999999999999ap-15f/*4.882813e-05*/), mask_full, MODE_ZEROING);
  auto one = simd_inst::vdup<float>(float(0x1p+0f/*1.000000e+00*/), mask_full, MODE_ZEROING);
  auto zero = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), mask_full, MODE_ZEROING);
  auto lane_idx = simd_inst::vci<int32_t>(0, INC_ORDER);
  final_sq_acc = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[2496])), 0);
  simd_inst::vsts_norm(final_sq_acc, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[2560])), 0, mask_full);
  simd_inst::mem_bar(VST_VLD);
  auto acc_vec = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1152])), 0);
  rms_vec = zero;
  for (int32_t token_idx = 0; token_idx < 3; ++token_idx) {
    auto sq_val = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(token_idx + 2560)])), 0);
    auto rms_val = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_val, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
    auto token_mask = simd_inst::pand(simd_inst::vcmps_ge(lane_idx, (token_idx * 24), mask_full), simd_inst::vcmps_lt(lane_idx, ((token_idx * 24) + 24), mask_full), mask_full);
    rms_vec = simd_inst::vsel(rms_val, rms_vec, token_mask);
  }
  simd_inst::vsts_norm(acc_vec, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1536])), 0, mask_full);
  simd_inst::vsts_norm(simd_inst::vmul(acc_vec, rms_vec, mask_full, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1920])), 0, mask_full);
  auto acc_vec_1 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1216])), 0);
  rms_vec = zero;
  for (int32_t token_idx_1 = 2; token_idx_1 < 6; ++token_idx_1) {
    auto sq_val_1 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(token_idx_1 + 2560)])), 0);
    auto rms_val_1 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_val_1, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
    auto token_mask_1 = simd_inst::pand(simd_inst::vcmps_ge(lane_idx, ((token_idx_1 * 24) - 64), mask_full), simd_inst::vcmps_lt(lane_idx, ((token_idx_1 * 24) - 40), mask_full), mask_full);
    rms_vec = simd_inst::vsel(rms_val_1, rms_vec, token_mask_1);
  }
  simd_inst::vsts_norm(acc_vec_1, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1600])), 0, mask_full);
  simd_inst::vsts_norm(simd_inst::vmul(acc_vec_1, rms_vec, mask_full, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1984])), 0, mask_full);
  auto acc_vec_2 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1280])), 0);
  rms_vec = zero;
  for (int32_t token_idx_2 = 5; token_idx_2 < 8; ++token_idx_2) {
    auto sq_val_2 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(token_idx_2 + 2560)])), 0);
    auto rms_val_2 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_val_2, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
    auto token_mask_2 = simd_inst::pand(simd_inst::vcmps_ge(lane_idx, ((token_idx_2 * 24) - 128), mask_full), simd_inst::vcmps_lt(lane_idx, ((token_idx_2 * 24) - 104), mask_full), mask_full);
    rms_vec = simd_inst::vsel(rms_val_2, rms_vec, token_mask_2);
  }
  simd_inst::vsts_norm(acc_vec_2, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1664])), 0, mask_full);
  simd_inst::vsts_norm(simd_inst::vmul(acc_vec_2, rms_vec, mask_full, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[2048])), 0, mask_full);
  auto acc_vec_3 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1344])), 0);
  rms_vec = zero;
  for (int32_t token_idx_3 = 8; token_idx_3 < 11; ++token_idx_3) {
    auto sq_val_3 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(token_idx_3 + 2560)])), 0);
    auto rms_val_3 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_val_3, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
    auto token_mask_3 = simd_inst::pand(simd_inst::vcmps_ge(lane_idx, ((token_idx_3 * 24) - 192), mask_full), simd_inst::vcmps_lt(lane_idx, ((token_idx_3 * 24) - 168), mask_full), mask_full);
    rms_vec = simd_inst::vsel(rms_val_3, rms_vec, token_mask_3);
  }
  simd_inst::vsts_norm(acc_vec_3, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1728])), 0, mask_full);
  simd_inst::vsts_norm(simd_inst::vmul(acc_vec_3, rms_vec, mask_full, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[2112])), 0, mask_full);
  auto acc_vec_4 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1408])), 0);
  rms_vec = zero;
  for (int32_t token_idx_4 = 10; token_idx_4 < 14; ++token_idx_4) {
    auto sq_val_4 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(token_idx_4 + 2560)])), 0);
    auto rms_val_4 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_val_4, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
    auto token_mask_4 = simd_inst::pand(simd_inst::vcmps_ge(lane_idx, ((token_idx_4 * 24) - 256), mask_full), simd_inst::vcmps_lt(lane_idx, ((token_idx_4 * 24) - 232), mask_full), mask_full);
    rms_vec = simd_inst::vsel(rms_val_4, rms_vec, token_mask_4);
  }
  simd_inst::vsts_norm(acc_vec_4, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1792])), 0, mask_full);
  simd_inst::vsts_norm(simd_inst::vmul(acc_vec_4, rms_vec, mask_full, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[2176])), 0, mask_full);
  auto acc_vec_5 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1472])), 0);
  rms_vec = zero;
  for (int32_t token_idx_5 = 13; token_idx_5 < 16; ++token_idx_5) {
    auto sq_val_5 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(token_idx_5 + 2560)])), 0);
    auto rms_val_5 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_val_5, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
    auto token_mask_5 = simd_inst::pand(simd_inst::vcmps_ge(lane_idx, ((token_idx_5 * 24) - 320), mask_full), simd_inst::vcmps_lt(lane_idx, ((token_idx_5 * 24) - 296), mask_full), mask_full);
    rms_vec = simd_inst::vsel(rms_val_5, rms_vec, token_mask_5);
  }
  simd_inst::vsts_norm(acc_vec_5, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[1856])), 0, mask_full);
  simd_inst::vsts_norm(simd_inst::vmul(acc_vec_5, rms_vec, mask_full, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[2240])), 0, mask_full);
}

extern "C" __global__ __vector__ void mhc_reduce_partials_and_rmsnorm_fwd_asc_kernel(__gm__ float* out, __gm__ float* out_mul, __gm__ float* out_mul_splitted, __gm__ float* sqrsum, __gm__ float* sqrsum_splitted, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t mul_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  mul_ub_version_counter_1 = 0;
  for (int32_t w = 0; w < ((num_tokens + 895) / 896); ++w) {
    if (((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) {
      mhc_reduce_partials_and_rmsnorm_fwd_asc_kernel_simd_vf_0(buf_dyn_shmem);
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((mul_ub_version_counter_1 % 3) >> 31)) + (mul_ub_version_counter_1 % 3))));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((mul_ub_version_counter_1 % 3) >> 31)) * 384) + ((mul_ub_version_counter_1 % 3) * 384))]))), (__gm__ uint8_t*)((&(out_mul_splitted[((((int64_t)w) * (int64_t)21504) + (((int64_t)((int32_t)block_idx)) * (int64_t)384))]))), 1, (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 96), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 96), (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 96));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((mul_ub_version_counter_1 % 3) >> 31)) * 64) + ((mul_ub_version_counter_1 % 3) * 64)) + 2304)]))), (__gm__ uint8_t*)((&(sqrsum_splitted[((((int64_t)w) * (int64_t)896) + (((int64_t)((int32_t)block_idx)) * (int64_t)16))]))), 1, (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 4), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 4), (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 4));
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((mul_ub_version_counter_1 % 3) >> 31)) + (mul_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((mul_ub_version_counter_1 % 3) >> 31)) + (mul_ub_version_counter_1 % 3))));
      mhc_reduce_partials_and_rmsnorm_fwd_asc_kernel_simd_vf_1(buf_dyn_shmem, mul_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((mul_ub_version_counter_1 % 3) >> 31)) + (mul_ub_version_counter_1 % 3))));
      mul_ub_version_counter_1 = (mul_ub_version_counter_1 + 1);
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
      mhc_reduce_partials_and_rmsnorm_fwd_asc_kernel_simd_vf_2(buf_dyn_shmem);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(0));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(0));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(out[((((int64_t)w) * (int64_t)21504) + (((int64_t)((int32_t)block_idx)) * (int64_t)384))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[1920]))), 1, (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 96), static_cast<asc_store_l2_cache_mode>(4), (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 96), (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 96));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(out_mul[((((int64_t)w) * (int64_t)21504) + (((int64_t)((int32_t)block_idx)) * (int64_t)384))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[1536]))), 1, (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 96), static_cast<asc_store_l2_cache_mode>(4), (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 96), (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 96));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(sqrsum[((((int64_t)w) * (int64_t)896) + (((int64_t)((int32_t)block_idx)) * (int64_t)16))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[2560]))), 1, (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 4), static_cast<asc_store_l2_cache_mode>(4), (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 4), (min(16, max(((num_tokens - (((int32_t)block_idx) * 16)) - (w * 896)), 0)) * 4));
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
    }
  }
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
}

