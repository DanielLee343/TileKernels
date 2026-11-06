#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void cast_back_kernel_ascend_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t sf_raw_ub_version_counter_1) {
  vector_bool mask_low_f32 = asc_create_mask_b32(PAT_VL32);
  for (int32_t group = 0; group < 48; ++group) {
    for (int32_t chunk = 0; chunk < 8; ++chunk) {
      auto scale_low = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 768) + ((sf_raw_ub_version_counter_1 % 3) * 768)) + (group * 16)) + (chunk * 2)) + 55296)])), 0);
      auto scale_high = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 768) + ((sf_raw_ub_version_counter_1 % 3) * 768)) + (group * 16)) + (chunk * 2)) + 55297)])), 0);
      auto scale = simd_inst::vsel(scale_low, scale_high, mask_low_f32);
      auto x_raw = simd_inst::vlds_unpack4<float8_e4m3_t>((__ubuf__ float8_e4m3_t*)(&(((__ubuf__ fp8_e4_t*)buf_dyn_shmem)[((((((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 24576) + ((sf_raw_ub_version_counter_1 % 3) * 24576)) + (group * 512)) + (chunk * 64)) + 147456)])), 0);
      vector_bool v = asc_create_mask_b8(PAT_ALL);
      vector_bool v_1 = asc_create_mask_b32(PAT_ALL);
      auto out_f32 = simd_inst::vmul(simd_inst::vcvt<float>(x_raw, v, PART_P0, MODE_ZEROING), scale, v_1, MODE_ZEROING);
      vector_bool v_2 = asc_create_mask_b16(PAT_ALL);
      auto out_bf16 = simd_inst::vcvt<bfloat16_t>(out_f32, v_2, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING);
      simd_inst::vsts_pack_b32(out_bf16, (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 24576) + ((sf_raw_ub_version_counter_1 % 3) * 24576)) + (group * 512)) + (chunk * 64))])), 0, v_2);
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
  for (int32_t w = 0; w < ((num_tokens + 671) / 672); ++w) {
    if ((((w * 14) + (((int32_t)block_idx) / 4)) / (((num_tokens + 47) / 48) + (((num_tokens + 47) % 48) >> 31))) < 1) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ fp8_e4_t*)buf_dyn_shmem)[((((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 24576) + ((sf_raw_ub_version_counter_1 % 3) * 24576)) + 147456)]))), (__gm__ uint8_t*)((&(x[((((((((int64_t)w) * (int64_t)14) + (((int64_t)((int32_t)block_idx)) / (int64_t)4)) % (((((int64_t)num_tokens) + (int64_t)47) / (int64_t)48) + (((((int64_t)num_tokens) + (int64_t)47) % (int64_t)48) >> (int64_t)63))) * (int64_t)98304) + ((((((int64_t)w) * (int64_t)14) + (((int64_t)((int32_t)block_idx)) / (int64_t)4)) / (((((int64_t)num_tokens) + (int64_t)47) / (int64_t)48) + (((((int64_t)num_tokens) + (int64_t)47) % (int64_t)48) >> (int64_t)63))) * (int64_t)2048)) + ((((int64_t)((int32_t)block_idx)) % (int64_t)4) * (int64_t)512))]))), min(48, max((num_tokens - ((((w * 14) + (((int32_t)block_idx) / 4)) % (((num_tokens + 47) / 48) + (((num_tokens + 47) % 48) >> 31))) * 48)), 0)), 512, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 2048, 512);
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 768) + ((sf_raw_ub_version_counter_1 % 3) * 768)) + 55296)]))), (__gm__ uint8_t*)((&(x_sf[((((((((int64_t)w) * (int64_t)14) + (((int64_t)((int32_t)block_idx)) / (int64_t)4)) / (((((int64_t)num_tokens) + (int64_t)47) / (int64_t)48) + (((((int64_t)num_tokens) + (int64_t)47) % (int64_t)48) >> (int64_t)63))) * (int64_t)64) + (((((((int64_t)w) * (int64_t)14) + (((int64_t)((int32_t)block_idx)) / (int64_t)4)) % (((((int64_t)num_tokens) + (int64_t)47) / (int64_t)48) + (((((int64_t)num_tokens) + (int64_t)47) % (int64_t)48) >> (int64_t)63))) * ((int64_t)sf_stride)) * (int64_t)48)) + ((((int64_t)((int32_t)block_idx)) % (int64_t)4) * (int64_t)16))]))), min(48, max((num_tokens - ((((w * 14) + (((int32_t)block_idx) / 4)) % (((num_tokens + 47) / 48) + (((num_tokens + 47) % 48) >> 31))) * 48)), 0)), 64, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (sf_stride * 4), 64);
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      cast_back_kernel_ascend_kernel_simd_vf_0(buf_dyn_shmem, sf_raw_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) + (sf_raw_ub_version_counter_1 % 3))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(out[((((((((int64_t)w) * (int64_t)14) + (((int64_t)((int32_t)block_idx)) / (int64_t)4)) % (((((int64_t)num_tokens) + (int64_t)47) / (int64_t)48) + (((((int64_t)num_tokens) + (int64_t)47) % (int64_t)48) >> (int64_t)63))) * (int64_t)98304) + ((((((int64_t)w) * (int64_t)14) + (((int64_t)((int32_t)block_idx)) / (int64_t)4)) / (((((int64_t)num_tokens) + (int64_t)47) / (int64_t)48) + (((((int64_t)num_tokens) + (int64_t)47) % (int64_t)48) >> (int64_t)63))) * (int64_t)2048)) + ((((int64_t)((int32_t)block_idx)) % (int64_t)4) * (int64_t)512))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((3 & ((sf_raw_ub_version_counter_1 % 3) >> 31)) * 24576) + ((sf_raw_ub_version_counter_1 % 3) * 24576))]))), min(48, max((num_tokens - ((((w * 14) + (((int32_t)block_idx) / 4)) % (((num_tokens + 47) / 48) + (((num_tokens + 47) % 48) >> 31))) * 48)), 0)), 1024, static_cast<asc_store_l2_cache_mode>(4), 4096, 1024);
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

