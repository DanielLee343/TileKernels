#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void mhc_fn_normw_merge_fwd_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t normw_ub_version_counter_1) {
  vector_bool mask = asc_create_mask_b32(PAT_ALL);
  for (int32_t vec_pair = 0; vec_pair < 2; ++vec_pair) {
    auto normw0 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((normw_ub_version_counter_1 % 3) >> 31)) * 256) + ((normw_ub_version_counter_1 % 3) * 256)) + (vec_pair * 128)) + 36864)])), 0);
    auto normw1 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((normw_ub_version_counter_1 % 3) >> 31)) * 256) + ((normw_ub_version_counter_1 % 3) * 256)) + (vec_pair * 128)) + 36928)])), 0);
    for (int32_t row = 0; row < 24; ++row) {
      auto fn0 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((normw_ub_version_counter_1 % 3) >> 31)) * 6144) + ((normw_ub_version_counter_1 % 3) * 6144)) + (row * 256)) + (vec_pair * 128))])), 0);
      auto fn1 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((normw_ub_version_counter_1 % 3) >> 31)) * 6144) + ((normw_ub_version_counter_1 % 3) * 6144)) + (row * 256)) + (vec_pair * 128)) + 64)])), 0);
      simd_inst::vsts_norm(simd_inst::vmul(fn0, normw0, mask, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((normw_ub_version_counter_1 % 3) >> 31)) * 6144) + ((normw_ub_version_counter_1 % 3) * 6144)) + (row * 256)) + (vec_pair * 128)) + 18432)])), 0, mask);
      simd_inst::vsts_norm(simd_inst::vmul(fn1, normw1, mask, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((normw_ub_version_counter_1 % 3) >> 31)) * 6144) + ((normw_ub_version_counter_1 % 3) * 6144)) + (row * 256)) + (vec_pair * 128)) + 18496)])), 0, mask);
    }
  }
}

extern "C" __global__ __vector__ void mhc_fn_normw_merge_fwd_asc_kernel(__gm__ float* fn, __gm__ float* normw, __gm__ float* out_fn) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t normw_ub_version_counter_1 = 0;
  normw_ub_version_counter_1 = 0;
  if (((int32_t)block_idx) < 6) {
    asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((normw_ub_version_counter_1 % 3) >> 31)) * 6144) + ((normw_ub_version_counter_1 % 3) * 6144))]))), (__gm__ uint8_t*)((&(fn[(((int32_t)block_idx) * 256)]))), 24, 1024, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 6144, 1024);
    asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((normw_ub_version_counter_1 % 3) >> 31)) * 256) + ((normw_ub_version_counter_1 % 3) * 256)) + 36864)]))), (__gm__ uint8_t*)((&(normw[(((int32_t)block_idx) * 256)]))), 1, 1024, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 1024, 1024);
    asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((normw_ub_version_counter_1 % 3) >> 31)) + (normw_ub_version_counter_1 % 3))));
    asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((normw_ub_version_counter_1 % 3) >> 31)) + (normw_ub_version_counter_1 % 3))));
    mhc_fn_normw_merge_fwd_asc_kernel_simd_vf_0(buf_dyn_shmem, normw_ub_version_counter_1);
    asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((normw_ub_version_counter_1 % 3) >> 31)) + (normw_ub_version_counter_1 % 3))));
    asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((normw_ub_version_counter_1 % 3) >> 31)) + (normw_ub_version_counter_1 % 3))));
    asc_copy_ub2gm_align((__gm__ uint8_t*)((&(out_fn[(((int32_t)block_idx) * 256)]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((normw_ub_version_counter_1 % 3) >> 31)) * 6144) + ((normw_ub_version_counter_1 % 3) * 6144)) + 18432)]))), 24, 1024, static_cast<asc_store_l2_cache_mode>(4), 6144, 1024);
    normw_ub_version_counter_1 = (normw_ub_version_counter_1 + 1);
  }
}

