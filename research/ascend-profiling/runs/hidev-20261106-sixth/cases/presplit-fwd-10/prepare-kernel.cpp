#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
__simt_vf__ __launch_bounds__(32) inline void mhc_pre_split_mixes_fwd_simd_mhc4_asc_kernel_simt_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, __gm__ float* mhc_scale, __gm__ float* mhc_base) {
  if (((int32_t)threadIdx.x) < 3) {
    ((__ubuf__ float*)buf_dyn_shmem)[((((int32_t)threadIdx.x) * 8) + 6336)] = mhc_scale[((int32_t)threadIdx.x)];
  }
  if (((int32_t)threadIdx.x) < 24) {
    ((__ubuf__ float*)buf_dyn_shmem)[((((int32_t)threadIdx.x) * 8) + 6144)] = mhc_base[((int32_t)threadIdx.x)];
  }
}

#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void mhc_pre_split_mixes_fwd_simd_mhc4_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t input_mixes_ub_version_counter_1) {
  vector_f32 pre_base_vec;
  vector_f32 post_base_vec;
  vector_f32 comb_base_vec;
  vector_bool mask = asc_create_mask_b32(PAT_ALL);
  auto idx = simd_inst::vci<int32_t>(0, INC_ORDER);
  auto zeros = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), mask, MODE_ZEROING);
  auto ones = simd_inst::vdup<float>(float(0x1p+0f/*1.000000e+00*/), mask, MODE_ZEROING);
  auto col3 = simd_inst::vand(idx, simd_inst::vdup<int32_t>(3, mask, MODE_ZEROING), mask, MODE_ZEROING);
  auto col15 = simd_inst::vand(idx, simd_inst::vdup<int32_t>(15, mask, MODE_ZEROING), mask, MODE_ZEROING);
  auto scale0 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[6336])), 0);
  auto scale1 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[6344])), 0);
  auto scale2 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[6352])), 0);
  pre_base_vec = zeros;
  post_base_vec = zeros;
  comb_base_vec = zeros;
  for (int32_t base_id = 0; base_id < 4; ++base_id) {
    auto base_mask = simd_inst::vcmps_eq(col3, base_id, mask);
    pre_base_vec = simd_inst::vsel(simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((base_id * 8) + 6144)])), 0), pre_base_vec, base_mask);
    post_base_vec = simd_inst::vsel(simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((base_id * 8) + 6176)])), 0), post_base_vec, base_mask);
  }
  for (int32_t base_id_1 = 0; base_id_1 < 16; ++base_id_1) {
    auto base_mask_1 = simd_inst::vcmps_eq(col15, base_id_1, mask);
    comb_base_vec = simd_inst::vsel(simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((base_id_1 * 8) + 6208)])), 0), comb_base_vec, base_mask_1);
  }
  for (int32_t vec_id = 0; vec_id < 4; ++vec_id) {
    auto token = simd_inst::vadd(simd_inst::vshrs(idx, 2, mask, MODE_ZEROING), simd_inst::vdup<int32_t>((vec_id * 16), mask, MODE_ZEROING), mask, MODE_ZEROING);
    auto token_offset = simd_inst::vadd(simd_inst::vshls(token, 4, mask, MODE_ZEROING), simd_inst::vshls(token, 3, mask, MODE_ZEROING), mask, MODE_ZEROING);
    auto pre_index = simd_inst::vadd(token_offset, col3, mask, MODE_ZEROING);
    auto post_index = simd_inst::vadds(pre_index, 4, mask, MODE_ZEROING);
    auto pre_val = simd_inst::vadd(simd_inst::vmul(simd_inst::vgather2((&(((__ubuf__ float*)buf_dyn_shmem)[((input_mixes_ub_version_counter_1 & 1) * 1536)])), (*(vector_u32 *)(&(pre_index))), mask), scale0, mask, MODE_ZEROING), pre_base_vec, mask, MODE_ZEROING);
    auto pre_sig = simd_inst::vdiv_0ulp_ftz_true(ones, simd_inst::vadds(simd_inst::vexpdif(zeros, pre_val, mask), float(0x1p+0f/*1.000000e+00*/), mask, MODE_ZEROING), mask, MODE_ZEROING);
    simd_inst::vsts_norm(simd_inst::vadds(pre_sig, float(0x1.47ae147ae147bp-7f/*1.000000e-02*/), mask, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((input_mixes_ub_version_counter_1 & 1) * 256) + (vec_id * 64)) + 5120)])), 0, mask);
    auto post_val = simd_inst::vadd(simd_inst::vmul(simd_inst::vgather2((&(((__ubuf__ float*)buf_dyn_shmem)[((input_mixes_ub_version_counter_1 & 1) * 1536)])), (*(vector_u32 *)(&(post_index))), mask), scale1, mask, MODE_ZEROING), post_base_vec, mask, MODE_ZEROING);
    auto post_sig = simd_inst::vdiv_0ulp_ftz_true(ones, simd_inst::vadds(simd_inst::vexpdif(zeros, post_val, mask), float(0x1p+0f/*1.000000e+00*/), mask, MODE_ZEROING), mask, MODE_ZEROING);
    simd_inst::vsts_norm(simd_inst::vmuls(post_sig, float(0x1p+1f/*2.000000e+00*/), mask, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((input_mixes_ub_version_counter_1 & 1) * 256) + (vec_id * 64)) + 5632)])), 0, mask);
  }
  for (int32_t vec_id_1 = 0; vec_id_1 < 16; ++vec_id_1) {
    auto token_1 = simd_inst::vadd(simd_inst::vshrs(idx, 4, mask, MODE_ZEROING), simd_inst::vdup<int32_t>((vec_id_1 * 4), mask, MODE_ZEROING), mask, MODE_ZEROING);
    auto token_offset_1 = simd_inst::vadd(simd_inst::vshls(token_1, 4, mask, MODE_ZEROING), simd_inst::vshls(token_1, 3, mask, MODE_ZEROING), mask, MODE_ZEROING);
    auto comb_index = simd_inst::vadd(simd_inst::vadds(token_offset_1, 8, mask, MODE_ZEROING), col15, mask, MODE_ZEROING);
    auto comb_val = simd_inst::vadd(simd_inst::vmul(simd_inst::vgather2((&(((__ubuf__ float*)buf_dyn_shmem)[((input_mixes_ub_version_counter_1 & 1) * 1536)])), (*(vector_u32 *)(&(comb_index))), mask), scale2, mask, MODE_ZEROING), comb_base_vec, mask, MODE_ZEROING);
    simd_inst::vsts_norm(comb_val, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((input_mixes_ub_version_counter_1 & 1) * 1024) + (vec_id_1 * 64)) + 3072)])), 0, mask);
  }
}

extern "C" __global__ __vector__ void mhc_pre_split_mixes_fwd_simd_mhc4_asc_kernel(__gm__ float* comb_res_mix, __gm__ float* input_mixes, __gm__ float* mhc_base, __gm__ float* mhc_scale, __gm__ float* post_layer_mix, __gm__ float* pre_layer_mix, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t input_mixes_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  input_mixes_ub_version_counter_1 = 0;
  asc_vf_call<mhc_pre_split_mixes_fwd_simd_mhc4_asc_kernel_simt_vf_0>(cce::dim3(32), buf_dyn_shmem, mhc_scale, mhc_base);
  for (int32_t w = 0; w < ((((((((((num_tokens + 63) >> 6) - 1) / max(1, min(8, ((num_tokens + 63) >> 6)))) + (((((num_tokens + 63) >> 6) - 1) % max(1, min(8, ((num_tokens + 63) >> 6)))) >> 31)) + 1) * max(1, min(8, ((num_tokens + 63) >> 6)))) + 55) / 56) + ((((((((((num_tokens + 63) >> 6) - 1) / max(1, min(8, ((num_tokens + 63) >> 6)))) + (((((num_tokens + 63) >> 6) - 1) % max(1, min(8, ((num_tokens + 63) >> 6)))) >> 31)) + 1) * max(1, min(8, ((num_tokens + 63) >> 6)))) + 55) % 56) >> 31)); ++w) {
    if ((((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) + (((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6))))) < ((num_tokens + 63) >> 6)) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>((input_mixes_ub_version_counter_1 & 1)));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((input_mixes_ub_version_counter_1 & 1) * 1536)]))), (__gm__ uint8_t*)((&(input_mixes[((((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)63) >> (int64_t)6)))) * max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)63) >> (int64_t)6)))) * (int64_t)1536) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)63) >> (int64_t)6)))) * (int64_t)1536))]))), 1, (min(64, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)), 0)) * 96), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(64, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)), 0)) * 96), (min(64, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)), 0)) * 96));
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>((input_mixes_ub_version_counter_1 & 1)));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>((input_mixes_ub_version_counter_1 & 1)));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>((input_mixes_ub_version_counter_1 & 1)));
      mhc_pre_split_mixes_fwd_simd_mhc4_asc_kernel_simd_vf_0(buf_dyn_shmem, input_mixes_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>((input_mixes_ub_version_counter_1 & 1)));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>((input_mixes_ub_version_counter_1 & 1)));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>((input_mixes_ub_version_counter_1 & 1)));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(post_layer_mix[((((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)63) >> (int64_t)6)))) * max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)63) >> (int64_t)6)))) * (int64_t)256) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)63) >> (int64_t)6)))) * (int64_t)256))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((input_mixes_ub_version_counter_1 & 1) * 256) + 5632)]))), 1, (min(64, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)), 0)) * 16), static_cast<asc_store_l2_cache_mode>(4), (min(64, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)), 0)) * 16), (min(64, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)), 0)) * 16));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(pre_layer_mix[((((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)63) >> (int64_t)6)))) * max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)63) >> (int64_t)6)))) * (int64_t)256) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)63) >> (int64_t)6)))) * (int64_t)256))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((input_mixes_ub_version_counter_1 & 1) * 256) + 5120)]))), 1, (min(64, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)), 0)) * 16), static_cast<asc_store_l2_cache_mode>(4), (min(64, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)), 0)) * 16), (min(64, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)), 0)) * 16));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(comb_res_mix[((((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)63) >> (int64_t)6)))) * max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)63) >> (int64_t)6)))) * (int64_t)1024) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)63) >> (int64_t)6)))) * (int64_t)1024))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((input_mixes_ub_version_counter_1 & 1) * 1024) + 3072)]))), 1, (min(64, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)), 0)) * 64), static_cast<asc_store_l2_cache_mode>(4), (min(64, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)), 0)) * 64), (min(64, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 63) >> 6)))) * max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 63) >> 6)))) * 64)), 0)) * 64));
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>((input_mixes_ub_version_counter_1 & 1)));
      input_mixes_ub_version_counter_1 = (input_mixes_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
}

