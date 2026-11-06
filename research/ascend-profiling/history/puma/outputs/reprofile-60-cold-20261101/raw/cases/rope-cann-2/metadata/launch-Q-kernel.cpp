#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void _rope_kernel_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t cos_sin_ub_version_counter_1) {
  vector_f32 first;
  vector_f32 second;
  vector_f32 out_first;
  vector_f32 out_second;
  vector_f32 first_1;
  vector_f32 second_1;
  vector_f32 out_first_1;
  vector_f32 out_second_1;
  for (int32_t row = 0; row < 8; ++row) {
    auto cos_sin_values = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 512) + ((cos_sin_ub_version_counter_1 % 3) * 512)) + (row * 64)) + 47616)])), 0);
    auto v = simd_inst::vintlv(cos_sin_values, cos_sin_values);
    vector_bool v_1 = asc_create_mask_b32(PAT_ALL);
    auto sine = simd_inst::vneg(v.v1, v_1, MODE_ZEROING);
    for (int32_t pair = 0; pair < 15; ++pair) {
      first = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 15872) + ((cos_sin_ub_version_counter_1 % 3) * 15872)) + (row * 1984)) + (pair * 128))])), 0);
      second = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 15872) + ((cos_sin_ub_version_counter_1 % 3) * 15872)) + (row * 1984)) + (pair * 128)) + 64)])), 0);
      auto first_2 = first;
      auto second_2 = second;
      auto v_2 = simd_inst::vintlv(first_2, second_2);
      out_first = simd_inst::vmul(v_2.v1, sine, v_1, MODE_ZEROING);
      simd_inst::vmula((&(out_first)), v_2.v0, v.v0, v_1, MODE_ZEROING);
      out_second = simd_inst::vmul(v_2.v1, v.v0, v_1, MODE_ZEROING);
      simd_inst::vmula((&(out_second)), v_2.v0, v.v1, v_1, MODE_ZEROING);
      auto first_3 = out_first;
      auto second_3 = out_second;
      auto v_3 = simd_inst::vdintlv(first_3, second_3);
      simd_inst::vsts_norm(v_3.v0, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 15872) + ((cos_sin_ub_version_counter_1 % 3) * 15872)) + (row * 1984)) + (pair * 128))])), 0, v_1);
      simd_inst::vsts_norm(v_3.v1, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 15872) + ((cos_sin_ub_version_counter_1 % 3) * 15872)) + (row * 1984)) + (pair * 128)) + 64)])), 0, v_1);
    }
    first_1 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 15872) + ((cos_sin_ub_version_counter_1 % 3) * 15872)) + (row * 1984)) + 1920)])), 0);
    second_1 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 15872) + ((cos_sin_ub_version_counter_1 % 3) * 15872)) + (row * 1984)) + 1920)])), 0);
    auto first_4 = first_1;
    auto second_4 = second_1;
    auto v_4 = simd_inst::vintlv(first_4, second_4);
    out_first_1 = simd_inst::vmul(v_4.v1, sine, v_1, MODE_ZEROING);
    simd_inst::vmula((&(out_first_1)), v_4.v0, v.v0, v_1, MODE_ZEROING);
    out_second_1 = simd_inst::vmul(v_4.v1, v.v0, v_1, MODE_ZEROING);
    simd_inst::vmula((&(out_second_1)), v_4.v0, v.v1, v_1, MODE_ZEROING);
    auto first_5 = out_first_1;
    auto second_5 = out_second_1;
    auto v_5 = simd_inst::vdintlv(first_5, second_5);
    simd_inst::vsts_norm(v_5.v0, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 15872) + ((cos_sin_ub_version_counter_1 % 3) * 15872)) + (row * 1984)) + 1920)])), 0, v_1);
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
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 15872) + ((cos_sin_ub_version_counter_1 % 3) * 15872))]))), (__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)15872) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)batch)) * ((int64_t)x_stride_b)))]))), 1, (min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 7936), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(4), (min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 7936), (min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 7936));
      if ((0 < (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) && (0 < ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8)))) {
        asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 512) + ((cos_sin_ub_version_counter_1 % 3) * 512)) + 47616)]))), (__gm__ uint8_t*)((&(cos_sin_cache[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)512) + (((int64_t)seqlen_offsets) * (int64_t)64))]))), 1, (min(min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 256), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 256), (min(min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 256));
      }
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      _rope_kernel_kernel_simd_vf_0(buf_dyn_shmem, cos_sin_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)15872) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)batch)) * ((int64_t)x_stride_b)))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 15872) + ((cos_sin_ub_version_counter_1 % 3) * 15872))]))), 1, (min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 7936), static_cast<asc_store_l2_cache_mode>(4), (min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 7936), (min(8, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 8))) * 7936));
      asc_sync_notify(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      cos_sin_ub_version_counter_1 = (cos_sin_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(2));
}

