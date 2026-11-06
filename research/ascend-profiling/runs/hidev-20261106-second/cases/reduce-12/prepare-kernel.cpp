#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void engram_sinkhorn_step_reduce_kernel_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem) {
  vector_f32 accum[4];
  vector_bool v = asc_create_mask_b32(PAT_ALL);
  auto zero = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v, MODE_ZEROING);
  accum[0] = zero;
  accum[1] = zero;
  accum[2] = zero;
  accum[3] = zero;
  for (int32_t partial_id = 0; partial_id < 28; ++partial_id) {
    accum[0] = simd_inst::vadd(accum[0], simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(partial_id * 256)])), 0), v, MODE_ZEROING);
    accum[1] = simd_inst::vadd(accum[1], simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((partial_id * 256) + 64)])), 0), v, MODE_ZEROING);
    accum[2] = simd_inst::vadd(accum[2], simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((partial_id * 256) + 128)])), 0), v, MODE_ZEROING);
    accum[3] = simd_inst::vadd(accum[3], simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((partial_id * 256) + 192)])), 0), v, MODE_ZEROING);
  }
  simd_inst::vsts_norm(accum[0], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[7168])), 0, v);
  simd_inst::vsts_norm(accum[1], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[7232])), 0, v);
  simd_inst::vsts_norm(accum[2], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[7296])), 0, v);
  simd_inst::vsts_norm(accum[3], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[7360])), 0, v);
}

extern "C" __global__ __vector__ void engram_sinkhorn_step_reduce_kernel_asc_kernel(__gm__ float* col_sumsq, __gm__ float* col_sumsq_partial) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[0]))), (__gm__ uint8_t*)((&(col_sumsq_partial[(((int32_t)block_idx) * 256)]))), 28, 1024, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 8192, 1024);
  asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(0));
  engram_sinkhorn_step_reduce_kernel_asc_kernel_simd_vf_0(buf_dyn_shmem);
  asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(0));
  asc_copy_ub2gm_align((__gm__ uint8_t*)((&(col_sumsq[(((int32_t)block_idx) * 256)]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[7168]))), 1, 1024, static_cast<asc_store_l2_cache_mode>(4), 1024, 1024);
}

