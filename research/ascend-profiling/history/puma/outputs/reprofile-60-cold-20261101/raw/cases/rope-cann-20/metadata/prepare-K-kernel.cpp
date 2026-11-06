#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void _rope_kernel_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t cos_sin_ub_version_counter_1) {
  vector_f32 first;
  vector_f32 second;
  vector_f32 out_first;
  vector_f32 out_second;
  for (int32_t row = 0; row < 16; ++row) {
    auto cosine = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 2048) + ((cos_sin_ub_version_counter_1 % 3) * 2048)) + (row * 128)) + 43008)])), 0);
    auto neg_sine = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 2048) + ((cos_sin_ub_version_counter_1 % 3) * 2048)) + (row * 128)) + 43072)])), 0);
    vector_bool v = asc_create_mask_b32(PAT_ALL);
    auto sine = simd_inst::vneg(neg_sine, v, MODE_ZEROING);
    for (int32_t second_head = 0; second_head < 7; ++second_head) {
      first = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 14336) + ((cos_sin_ub_version_counter_1 % 3) * 14336)) + (row * 896)) + (second_head * 128))])), 0);
      second = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 14336) + ((cos_sin_ub_version_counter_1 % 3) * 14336)) + (row * 896)) + (second_head * 128)) + 64)])), 0);
      auto first_1 = first;
      auto second_1 = second;
      auto v_1 = simd_inst::vdintlv(first_1, second_1);
      out_first = simd_inst::vmul(v_1.v1, sine, v, MODE_ZEROING);
      simd_inst::vmula((&(out_first)), v_1.v0, cosine, v, MODE_ZEROING);
      out_second = simd_inst::vmul(v_1.v1, cosine, v, MODE_ZEROING);
      simd_inst::vmula((&(out_second)), v_1.v0, neg_sine, v, MODE_ZEROING);
      auto first_2 = out_first;
      auto second_2 = out_second;
      auto v_2 = simd_inst::vintlv(first_2, second_2);
      simd_inst::vsts_norm(v_2.v0, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 14336) + ((cos_sin_ub_version_counter_1 % 3) * 14336)) + (row * 896)) + (second_head * 128))])), 0, v);
      simd_inst::vsts_norm(v_2.v1, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 14336) + ((cos_sin_ub_version_counter_1 % 3) * 14336)) + (row * 896)) + (second_head * 128)) + 64)])), 0, v);
    }
  }
}

extern "C" __global__ __vector__ void _rope_kernel_kernel(__gm__ float* cos_sin_cache, __gm__ float* x, int32_t batch, int32_t seqlen, int32_t seqlen_offsets, int32_t seqlen_ro, int32_t x_stride_b) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t cos_sin_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(2));
  cos_sin_ub_version_counter_1 = 0;
  for (int32_t w = 0; w < (((((seqlen + 15) >> 4) * batch) + 55) / 56); ++w) {
    if ((((w * 56) + ((int32_t)block_idx)) / batch) < ((seqlen + 15) >> 4)) {
      asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 14336) + ((cos_sin_ub_version_counter_1 % 3) * 14336))]))), (__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)14336) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)batch)) * ((int64_t)x_stride_b)))]))), 1, (min(16, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))) * 3584), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(4), (min(16, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))) * 3584), (min(16, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))) * 3584));
      if ((0 < (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))) && (0 < ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16)))) {
        asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 2048) + ((cos_sin_ub_version_counter_1 % 3) * 2048)) + 43008)]))), (__gm__ uint8_t*)((&(cos_sin_cache[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)2048) + (((int64_t)seqlen_offsets) * (int64_t)128))]))), 1, (min(min(16, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))) * 512), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(min(16, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))) * 512), (min(min(16, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))) * 512));
      }
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      _rope_kernel_kernel_simd_vf_0(buf_dyn_shmem, cos_sin_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)14336) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)batch)) * ((int64_t)x_stride_b)))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 14336) + ((cos_sin_ub_version_counter_1 % 3) * 14336))]))), 1, (min(16, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))) * 3584), static_cast<asc_store_l2_cache_mode>(4), (min(16, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))) * 3584), (min(16, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 16))) * 3584));
      asc_sync_notify(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      cos_sin_ub_version_counter_1 = (cos_sin_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(2));
}

