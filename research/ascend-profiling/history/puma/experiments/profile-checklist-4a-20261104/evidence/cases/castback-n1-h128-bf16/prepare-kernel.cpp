#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void cast_back_kernel_ascend_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t sf_raw_ub_version_counter_1) {
  vector_bool mask_low_f32 = asc_create_mask_b32(PAT_VL32);
  for (int32_t group = 0; group < 184; ++group) {
    for (int32_t chunk = 0; chunk < 2; ++chunk) {
      auto scale_low = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 1472) + ((sf_raw_ub_version_counter_1 % 3) * 1472)) + (group * 8)) + (chunk * 2)) + 52992)])), 0);
      auto scale_high = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 1472) + ((sf_raw_ub_version_counter_1 % 3) * 1472)) + (group * 8)) + (chunk * 2)) + 52993)])), 0);
      auto scale = simd_inst::vsel(scale_low, scale_high, mask_low_f32);
      auto x_raw = simd_inst::vlds_unpack4<float8_e4m3_t>((__ubuf__ float8_e4m3_t*)(&(((__ubuf__ fp8_e4_t*)buf_dyn_shmem)[((((((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 23552) + ((sf_raw_ub_version_counter_1 % 3) * 23552)) + (group * 128)) + (chunk * 64)) + 141312)])), 0);
      vector_bool v = asc_create_mask_b8(PAT_ALL);
      vector_bool v_1 = asc_create_mask_b32(PAT_ALL);
      auto out_f32 = simd_inst::vmul(simd_inst::vcvt<float>(x_raw, v, PART_P0, MODE_ZEROING), scale, v_1, MODE_ZEROING);
      vector_bool v_2 = asc_create_mask_b16(PAT_ALL);
      auto out_bf16 = simd_inst::vcvt<bfloat16_t>(out_f32, v_2, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING);
      simd_inst::vsts_pack_b32(out_bf16, (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 23552) + ((sf_raw_ub_version_counter_1 % 3) * 23552)) + (group * 128)) + (chunk * 64))])), 0, v_2);
    }
  }
}

extern "C" __global__ __vector__ void cast_back_kernel_ascend_kernel(__gm__ bfloat16_t* out, __gm__ fp8_e4_t* x, __gm__ float* x_sf, int32_t num_tokens, int32_t sf_stride) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t sf_raw_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  sf_raw_ub_version_counter_1 = 0;
  for (int32_t w = 0; w < ((num_tokens + 10303) / 10304); ++w) {
    if ((((w * 56) + ((int32_t)block_idx)) / (((num_tokens + 183) / 184) + (((num_tokens + 183) % 184) >> 31))) < 1) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ fp8_e4_t*)buf_dyn_shmem)[((((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 23552) + ((sf_raw_ub_version_counter_1 % 3) * 23552)) + 141312)]))), (__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % (((((int64_t)num_tokens) + (int64_t)183) / (int64_t)184) + (((((int64_t)num_tokens) + (int64_t)183) % (int64_t)184) >> (int64_t)63))) * (int64_t)23552) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / (((((int64_t)num_tokens) + (int64_t)183) / (int64_t)184) + (((((int64_t)num_tokens) + (int64_t)183) % (int64_t)184) >> (int64_t)63))) * (int64_t)128))]))), 1, (min(184, max((num_tokens - ((((w * 56) + ((int32_t)block_idx)) % (((num_tokens + 183) / 184) + (((num_tokens + 183) % 184) >> 31))) * 184)), 0)) * 128), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(184, max((num_tokens - ((((w * 56) + ((int32_t)block_idx)) % (((num_tokens + 183) / 184) + (((num_tokens + 183) % 184) >> 31))) * 184)), 0)) * 128), (min(184, max((num_tokens - ((((w * 56) + ((int32_t)block_idx)) % (((num_tokens + 183) / 184) + (((num_tokens + 183) % 184) >> 31))) * 184)), 0)) * 128));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 1472) + ((sf_raw_ub_version_counter_1 % 3) * 1472)) + 52992)]))), (__gm__ uint8_t*)((&(x_sf[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % (((((int64_t)num_tokens) + (int64_t)183) / (int64_t)184) + (((((int64_t)num_tokens) + (int64_t)183) % (int64_t)184) >> (int64_t)63))) * ((int64_t)sf_stride)) * (int64_t)184)]))), min(184, max((num_tokens - ((((w * 56) + ((int32_t)block_idx)) % (((num_tokens + 183) / 184) + (((num_tokens + 183) % 184) >> 31))) * 184)), 0)), 16, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (sf_stride * 4), 32);
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      cast_back_kernel_ascend_kernel_simd_vf_0(buf_dyn_shmem, sf_raw_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(out[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % (((((int64_t)num_tokens) + (int64_t)183) / (int64_t)184) + (((((int64_t)num_tokens) + (int64_t)183) % (int64_t)184) >> (int64_t)63))) * (int64_t)23552) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / (((((int64_t)num_tokens) + (int64_t)183) / (int64_t)184) + (((((int64_t)num_tokens) + (int64_t)183) % (int64_t)184) >> (int64_t)63))) * (int64_t)128))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 23552) + ((sf_raw_ub_version_counter_1 % 3) * 23552))]))), 1, (min(184, max((num_tokens - ((((w * 56) + ((int32_t)block_idx)) % (((num_tokens + 183) / 184) + (((num_tokens + 183) % 184) >> 31))) * 184)), 0)) * 256), static_cast<asc_store_l2_cache_mode>(4), (min(184, max((num_tokens - ((((w * 56) + ((int32_t)block_idx)) % (((num_tokens + 183) / 184) + (((num_tokens + 183) % 184) >> 31))) * 184)), 0)) * 256), (min(184, max((num_tokens - ((((w * 56) + ((int32_t)block_idx)) % (((num_tokens + 183) / 184) + (((num_tokens + 183) % 184) >> 31))) * 184)), 0)) * 256));
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      sf_raw_ub_version_counter_1 = (sf_raw_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
}

