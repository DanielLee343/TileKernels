#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void expand_to_mhc_fwd_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t x_ub_version_counter_1) {
  vector_bool mask_16b = asc_create_mask_b16(PAT_ALL);
  for (int32_t c = 0; c < 20; ++c) {
    auto xb = simd_inst::vlds_norm<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((7 & ((x_ub_version_counter_1 % 7) >> 31)) * 2560) + ((x_ub_version_counter_1 % 7) * 2560)) + (c * 128)) + 71680)])), 0);
    simd_inst::vsts_norm(xb, (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((7 & ((x_ub_version_counter_1 % 7) >> 31)) * 10240) + ((x_ub_version_counter_1 % 7) * 10240)) + (c * 128))])), 0, mask_16b);
    simd_inst::vsts_norm(xb, (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((7 & ((x_ub_version_counter_1 % 7) >> 31)) * 10240) + ((x_ub_version_counter_1 % 7) * 10240)) + (c * 128)) + 2560)])), 0, mask_16b);
    simd_inst::vsts_norm(xb, (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((7 & ((x_ub_version_counter_1 % 7) >> 31)) * 10240) + ((x_ub_version_counter_1 % 7) * 10240)) + (c * 128)) + 5120)])), 0, mask_16b);
    simd_inst::vsts_norm(xb, (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((7 & ((x_ub_version_counter_1 % 7) >> 31)) * 10240) + ((x_ub_version_counter_1 % 7) * 10240)) + (c * 128)) + 7680)])), 0, mask_16b);
  }
}

extern "C" __global__ __vector__ void expand_to_mhc_fwd_asc_kernel(__gm__ bfloat16_t* o, __gm__ bfloat16_t* x, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t x_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(4));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(5));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(6));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(4));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(5));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(6));
  x_ub_version_counter_1 = 0;
  for (int32_t w = 0; w < ((num_tokens + 55) / 56); ++w) {
    if ((((w * 56) + ((int32_t)block_idx)) / num_tokens) < 1) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(((7 & ((x_ub_version_counter_1 % 7) >> 31)) + (x_ub_version_counter_1 % 7))));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((7 & ((x_ub_version_counter_1 % 7) >> 31)) * 2560) + ((x_ub_version_counter_1 % 7) * 2560)) + 71680)]))), (__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)num_tokens)) * (int64_t)2560) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)num_tokens)) * (int64_t)2560))]))), 1, 5120, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 5120, 5120);
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((7 & ((x_ub_version_counter_1 % 7) >> 31)) + (x_ub_version_counter_1 % 7))));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(((7 & ((x_ub_version_counter_1 % 7) >> 31)) + (x_ub_version_counter_1 % 7))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((7 & ((x_ub_version_counter_1 % 7) >> 31)) + (x_ub_version_counter_1 % 7))));
      expand_to_mhc_fwd_asc_kernel_simd_vf_0(buf_dyn_shmem, x_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((7 & ((x_ub_version_counter_1 % 7) >> 31)) + (x_ub_version_counter_1 % 7))));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((7 & ((x_ub_version_counter_1 % 7) >> 31)) + (x_ub_version_counter_1 % 7))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((7 & ((x_ub_version_counter_1 % 7) >> 31)) + (x_ub_version_counter_1 % 7))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(o[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)num_tokens)) * (int64_t)10240) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)num_tokens)) * (int64_t)2560))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((7 & ((x_ub_version_counter_1 % 7) >> 31)) * 10240) + ((x_ub_version_counter_1 % 7) * 10240))]))), 1, 20480, static_cast<asc_store_l2_cache_mode>(4), 20480, 20480);
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(((7 & ((x_ub_version_counter_1 % 7) >> 31)) + (x_ub_version_counter_1 % 7))));
      x_ub_version_counter_1 = (x_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(4));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(5));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(6));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(4));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(5));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(6));
}

