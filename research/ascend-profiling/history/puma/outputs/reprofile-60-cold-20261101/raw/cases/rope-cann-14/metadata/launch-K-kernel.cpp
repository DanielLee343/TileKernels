#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void _rope_kernel_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t cos_sin_ub_version_counter_1) {
  vector_f32 first;
  vector_f32 second;
  vector_f32 out_first;
  vector_f32 out_second;
  for (int32_t row = 0; row < 8; ++row) {
    auto cosine = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 1024) + ((cos_sin_ub_version_counter_1 % 3) * 1024)) + (row * 128)) + 52224)])), 0);
    auto neg_sine = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 1024) + ((cos_sin_ub_version_counter_1 % 3) * 1024)) + (row * 128)) + 52288)])), 0);
    vector_bool v = asc_create_mask_b32(PAT_ALL);
    auto sine = simd_inst::vneg(neg_sine, v, MODE_ZEROING);
    for (int32_t second_head = 0; second_head < 17; ++second_head) {
      first = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 17408) + ((cos_sin_ub_version_counter_1 % 3) * 17408)) + (row * 2176)) + (second_head * 128))])), 0);
      second = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 17408) + ((cos_sin_ub_version_counter_1 % 3) * 17408)) + (row * 2176)) + (second_head * 128)) + 64)])), 0);
      auto first_1 = first;
      auto second_1 = second;
      out_first = simd_inst::vmul(second_1, sine, v, MODE_ZEROING);
      simd_inst::vmula((&(out_first)), first_1, cosine, v, MODE_ZEROING);
      out_second = simd_inst::vmul(second_1, cosine, v, MODE_ZEROING);
      simd_inst::vmula((&(out_second)), first_1, neg_sine, v, MODE_ZEROING);
      auto first_2 = out_first;
      auto second_2 = out_second;
      simd_inst::vsts_norm(first_2, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 17408) + ((cos_sin_ub_version_counter_1 % 3) * 17408)) + (row * 2176)) + (second_head * 128))])), 0, v);
      simd_inst::vsts_norm(second_2, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 17408) + ((cos_sin_ub_version_counter_1 % 3) * 17408)) + (row * 2176)) + (second_head * 128)) + 64)])), 0, v);
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
  for (int32_t w = 0; w < (((((seqlen + 7) >> 3) * batch) + 55) / 56); ++w) {
    if ((((w * 56) + ((int32_t)block_idx)) / batch) < ((seqlen + 7) >> 3)) {
      asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 17408) + ((cos_sin_ub_version_counter_1 % 3) * 17408))]))), (__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)17408) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)batch)) * ((int64_t)x_stride_b)))]))), 1, (min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 8704), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(4), (min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 8704), (min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 8704));
      if ((0 < (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) && (0 < ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8)))) {
        asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 1024) + ((cos_sin_ub_version_counter_1 % 3) * 1024)) + 52224)]))), (__gm__ uint8_t*)((&(cos_sin_cache[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)1024) + (((int64_t)seqlen_offsets) * (int64_t)128))]))), 1, (min(min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 512), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 512), (min(min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 512));
      }
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      _rope_kernel_kernel_simd_vf_0(buf_dyn_shmem, cos_sin_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)17408) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)batch)) * ((int64_t)x_stride_b)))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 17408) + ((cos_sin_ub_version_counter_1 % 3) * 17408))]))), 1, (min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 8704), static_cast<asc_store_l2_cache_mode>(4), (min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 8704), (min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 8704));
      asc_sync_notify(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      cos_sin_ub_version_counter_1 = (cos_sin_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(2));
}

