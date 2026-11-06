#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void engram_sinkhorn_finalize_kernel_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t row_scale_ub_version_counter_1) {
  vector_f32 accum[4];
  vector_bool v = asc_create_mask_b32(PAT_ALL);
  auto zero = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v, MODE_ZEROING);
  auto alpha_vec = simd_inst::vdup<float>(float(0x1.1e3779b97f4a8p+6f/*7.155418e+01*/), v, MODE_ZEROING);
  accum[0] = zero;
  accum[1] = zero;
  accum[2] = zero;
  accum[3] = zero;
  auto scale = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((row_scale_ub_version_counter_1 & 3) * 8) + 46080)])), 0);
  for (int32_t chunk_group = 0; chunk_group < 20; ++chunk_group) {
    auto value = simd_inst::vmul(simd_inst::vmul(scale, simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((row_scale_ub_version_counter_1 & 3) * 5120) + (chunk_group * 256))])), 0), v, MODE_ZEROING), simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((chunk_group * 256) + 40960)])), 0), v, MODE_ZEROING);
    simd_inst::vmula((&(accum[0])), value, value, v, MODE_ZEROING);
    simd_inst::vsts_norm(value, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((row_scale_ub_version_counter_1 & 3) * 5120) + (chunk_group * 256)) + 20480)])), 0, v);
    auto value_1 = simd_inst::vmul(simd_inst::vmul(scale, simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((row_scale_ub_version_counter_1 & 3) * 5120) + (chunk_group * 256)) + 64)])), 0), v, MODE_ZEROING), simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((chunk_group * 256) + 41024)])), 0), v, MODE_ZEROING);
    simd_inst::vmula((&(accum[1])), value_1, value_1, v, MODE_ZEROING);
    simd_inst::vsts_norm(value_1, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((row_scale_ub_version_counter_1 & 3) * 5120) + (chunk_group * 256)) + 20544)])), 0, v);
    auto value_2 = simd_inst::vmul(simd_inst::vmul(scale, simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((row_scale_ub_version_counter_1 & 3) * 5120) + (chunk_group * 256)) + 128)])), 0), v, MODE_ZEROING), simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((chunk_group * 256) + 41088)])), 0), v, MODE_ZEROING);
    simd_inst::vmula((&(accum[2])), value_2, value_2, v, MODE_ZEROING);
    simd_inst::vsts_norm(value_2, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((row_scale_ub_version_counter_1 & 3) * 5120) + (chunk_group * 256)) + 20608)])), 0, v);
    auto value_3 = simd_inst::vmul(simd_inst::vmul(scale, simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((row_scale_ub_version_counter_1 & 3) * 5120) + (chunk_group * 256)) + 192)])), 0), v, MODE_ZEROING), simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((chunk_group * 256) + 41152)])), 0), v, MODE_ZEROING);
    simd_inst::vmula((&(accum[3])), value_3, value_3, v, MODE_ZEROING);
    simd_inst::vsts_norm(value_3, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((row_scale_ub_version_counter_1 & 3) * 5120) + (chunk_group * 256)) + 20672)])), 0, v);
  }
  accum[0] = simd_inst::vadd(accum[0], accum[2], v, MODE_ZEROING);
  accum[1] = simd_inst::vadd(accum[1], accum[3], v, MODE_ZEROING);
  accum[0] = simd_inst::vadd(accum[0], accum[1], v, MODE_ZEROING);
  auto norm = simd_inst::vsqrt(simd_inst::vcadd(accum[0], v, MODE_ZEROING), v, MODE_ZEROING);
  auto output_scale = simd_inst::vdiv_0ulp_ftz_true(alpha_vec, simd_inst::vadds(norm, float(0x1.79ca10c924223p-67f/*1.000000e-20*/), v, MODE_ZEROING), v, MODE_ZEROING);
  auto output_scale_broadcast = simd_inst::vdupv(output_scale, v, POS_LOWEST, MODE_ZEROING);
  simd_inst::mem_bar(VST_VLD);
  for (int32_t chunk = 0; chunk < 80; ++chunk) {
    simd_inst::vsts_norm(simd_inst::vmul(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((row_scale_ub_version_counter_1 & 3) * 5120) + (chunk * 64)) + 20480)])), 0), output_scale_broadcast, v, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((row_scale_ub_version_counter_1 & 3) * 5120) + (chunk * 64)) + 20480)])), 0, v);
  }
}

extern "C" __global__ __vector__ void engram_sinkhorn_finalize_kernel_asc_kernel(__gm__ float* col_scale, __gm__ float* matrix, __gm__ float* out, __gm__ float* row_scale, int32_t num_rows) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t row_scale_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
  row_scale_ub_version_counter_1 = 0;
  asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[40960]))), (__gm__ uint8_t*)((&(col_scale[0]))), 1, 20480, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 20480, 20480);
  asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(4));
  asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(4));
  for (int32_t w = 0; w < ((num_rows + 55) / 56); ++w) {
    if (((w * 56) + ((int32_t)block_idx)) < num_rows) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>((row_scale_ub_version_counter_1 & 3)));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((row_scale_ub_version_counter_1 & 3) * 5120)]))), (__gm__ uint8_t*)((&(matrix[((((int64_t)w) * (int64_t)286720) + (((int64_t)((int32_t)block_idx)) * (int64_t)5120))]))), 1, 20480, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 20480, 20480);
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((row_scale_ub_version_counter_1 & 3) * 8) + 46080)]))), (__gm__ uint8_t*)((&(row_scale[((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx)))]))), 1, 4, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 4, 4);
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>((row_scale_ub_version_counter_1 & 3)));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>((row_scale_ub_version_counter_1 & 3)));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>((row_scale_ub_version_counter_1 & 3)));
      engram_sinkhorn_finalize_kernel_asc_kernel_simd_vf_0(buf_dyn_shmem, row_scale_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>((row_scale_ub_version_counter_1 & 3)));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>((row_scale_ub_version_counter_1 & 3)));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>((row_scale_ub_version_counter_1 & 3)));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(out[((((int64_t)w) * (int64_t)286720) + (((int64_t)((int32_t)block_idx)) * (int64_t)5120))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((row_scale_ub_version_counter_1 & 3) * 5120) + 20480)]))), 1, 20480, static_cast<asc_store_l2_cache_mode>(4), 20480, 20480);
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>((row_scale_ub_version_counter_1 & 3)));
      row_scale_ub_version_counter_1 = (row_scale_ub_version_counter_1 + 1);
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

