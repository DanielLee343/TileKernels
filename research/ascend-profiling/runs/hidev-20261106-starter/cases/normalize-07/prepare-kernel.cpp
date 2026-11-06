#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
__simt_vf__ __launch_bounds__(128) inline void normalize_weight_kernel_kernel_simt_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t weights_ub_version_counter_1) {
  float weights_frag[32];
  float denom_frag[1];
  float norm_frag[32];
  #pragma unroll
  for (int32_t i = 0; i < 16; ++i) {
    *(float2*)(weights_frag + (i * 2)) = *(__ubuf__ float2*)(((__ubuf__ float*)buf_dyn_shmem) + ((((weights_ub_version_counter_1 & 3) * 4096) + (((int32_t)threadIdx.x) * 32)) + (i * 2)));
  }
  denom_frag[0] = float(0x0p+0f/*0.000000e+00*/);
  #pragma unroll
  for (int32_t rv = 0; rv < 32; ++rv) {
    denom_frag[0] = (denom_frag[0] + weights_frag[rv]);
  }
  denom_frag[0] = (denom_frag[0] + float(0x1.79ca10c924223p-67f/*1.000000e-20*/));
  #pragma unroll
  for (int32_t i_1 = 0; i_1 < 16; ++i_1) {
    float2 _;
      float2 v_ = *(float2*)(weights_frag + (i_1 * 2));
      float2 v__1 = make_float2(denom_frag[0], denom_frag[0]);
      _.x = (v_.x/v__1.x);
      _.y = (v_.y/v__1.y);
    *(float2*)(norm_frag + (i_1 * 2)) = _;
  }
  ((__ubuf__ float*)buf_dyn_shmem)[((((weights_ub_version_counter_1 & 3) * 128) + ((int32_t)threadIdx.x)) + 32768)] = denom_frag[0];
  #pragma unroll
  for (int32_t i_2 = 0; i_2 < 16; ++i_2) {
    *(__ubuf__ float2*)(((__ubuf__ float*)buf_dyn_shmem) + (((((weights_ub_version_counter_1 & 3) * 4096) + (((int32_t)threadIdx.x) * 32)) + (i_2 * 2)) + 16384)) = *(float2*)(norm_frag + (i_2 * 2));
  }
}

extern "C" __global__ __vector__ void normalize_weight_kernel_kernel(__gm__ float* denominator, __gm__ float* normalized_weights, __gm__ float* topk_weights, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t weights_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
  weights_ub_version_counter_1 = 0;
  for (int32_t w = 0; w < ((num_tokens + 7167) / 7168); ++w) {
    if (((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 127) >> 7)) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>((weights_ub_version_counter_1 & 3)));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((weights_ub_version_counter_1 & 3) * 4096)]))), (__gm__ uint8_t*)((&(topk_weights[((((int64_t)w) * (int64_t)229376) + (((int64_t)((int32_t)block_idx)) * (int64_t)4096))]))), 1, (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 128), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 128), (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 128));
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>((weights_ub_version_counter_1 & 3)));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>((weights_ub_version_counter_1 & 3)));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>((weights_ub_version_counter_1 & 3)));
      asc_vf_call<normalize_weight_kernel_kernel_simt_vf_0>(cce::dim3(128), buf_dyn_shmem, weights_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>((weights_ub_version_counter_1 & 3)));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>((weights_ub_version_counter_1 & 3)));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>((weights_ub_version_counter_1 & 3)));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(denominator[((((int64_t)w) * (int64_t)7168) + (((int64_t)((int32_t)block_idx)) * (int64_t)128))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((weights_ub_version_counter_1 & 3) * 128) + 32768)]))), 1, (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 4), static_cast<asc_store_l2_cache_mode>(4), (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 4), (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 4));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(normalized_weights[((((int64_t)w) * (int64_t)229376) + (((int64_t)((int32_t)block_idx)) * (int64_t)4096))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((weights_ub_version_counter_1 & 3) * 4096) + 16384)]))), 1, (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 128), static_cast<asc_store_l2_cache_mode>(4), (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 128), (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 128));
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>((weights_ub_version_counter_1 & 3)));
      weights_ub_version_counter_1 = (weights_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
}

