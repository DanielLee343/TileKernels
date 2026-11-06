#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void _rope_kernel_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t cos_sin_ub_version_counter_1) {
  vector_f32 first;
  vector_f32 second;
  vector_f32 out_first;
  vector_f32 out_second;
  vector_bool v = asc_create_mask_b32(PAT_ALL);
  auto cos_indices = simd_inst::vand(simd_inst::vci<int32_t>(0, INC_ORDER), simd_inst::vdup<int32_t>(31, v, MODE_ZEROING), v, MODE_ZEROING);
  auto sin_indices = simd_inst::vor(cos_indices, simd_inst::vdup<int32_t>(32, v, MODE_ZEROING), v, MODE_ZEROING);
  for (int32_t row = 0; row < 64; ++row) {
    auto cos_sin_values = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 4096) + ((cos_sin_ub_version_counter_1 % 3) * 4096)) + (row * 64)) + 49152)])), 0);
      vector_u32 v_ = simd_inst::vselr((*(vector_u32 *)(&(cos_sin_values))), (*(vector_u32 *)(&(cos_indices))));
    auto cosine = (*(vector_f32 *)(&(v_)));
      vector_u32 v__1 = simd_inst::vselr((*(vector_u32 *)(&(cos_sin_values))), (*(vector_u32 *)(&(sin_indices))));
    auto neg_sine = (*(vector_f32 *)(&(v__1)));
    auto sine = simd_inst::vneg(neg_sine, v, MODE_ZEROING);
    for (int32_t pair = 0; pair < 4; ++pair) {
      auto packed = simd_inst::vlds_norm<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 32768) + ((cos_sin_ub_version_counter_1 % 3) * 32768)) + (row * 512)) + (pair * 128))])), 0);
      vector_bool v_1 = asc_create_mask_b16(PAT_ALL);
      first = simd_inst::vcvt<float>(packed, v_1, PART_EVEN, MODE_ZEROING);
      second = simd_inst::vcvt<float>(packed, v_1, PART_ODD, MODE_ZEROING);
      auto first_1 = first;
      auto second_1 = second;
      out_first = simd_inst::vmul(second_1, sine, v, MODE_ZEROING);
      simd_inst::vmula((&(out_first)), first_1, cosine, v, MODE_ZEROING);
      out_second = simd_inst::vmul(second_1, cosine, v, MODE_ZEROING);
      simd_inst::vmula((&(out_second)), first_1, neg_sine, v, MODE_ZEROING);
      auto first_2 = out_first;
      auto second_2 = out_second;
        vector_bf16 v__2 = simd_inst::vcvt<bfloat16_t>(first_2, v_1, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING);
      auto first_bf16 = (*(vector_u16 *)(&(v__2)));
        vector_bf16 v__3 = simd_inst::vcvt<bfloat16_t>(second_2, v_1, ROUND_R, RS_ENABLE, PART_ODD, MODE_ZEROING);
      auto second_bf16 = (*(vector_u16 *)(&(v__3)));
        vector_u16 v__4 = simd_inst::vor(first_bf16, second_bf16, v_1, MODE_ZEROING);
      auto packed_1 = (*(vector_bf16 *)(&(v__4)));
      simd_inst::vsts_norm(packed_1, (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 32768) + ((cos_sin_ub_version_counter_1 % 3) * 32768)) + (row * 512)) + (pair * 128))])), 0, v_1);
    }
  }
}

extern "C" __global__ __vector__ void _rope_kernel_kernel(__gm__ float* cos_sin_cache, __gm__ bfloat16_t* x, int32_t batch, int32_t seqlen, int32_t seqlen_offsets, int32_t seqlen_ro, int32_t x_stride_b) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t cos_sin_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(2));
  cos_sin_ub_version_counter_1 = 0;
  for (int32_t w = 0; w < (((((seqlen + 63) >> 6) * batch) + 55) / 56); ++w) {
    if ((((w * 56) + ((int32_t)block_idx)) / batch) < ((seqlen + 63) >> 6)) {
      asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 32768) + ((cos_sin_ub_version_counter_1 % 3) * 32768))]))), (__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)32768) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)batch)) * ((int64_t)x_stride_b)))]))), 1, (min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 1024), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(4), (min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 1024), (min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 1024));
      if ((0 < (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) && (0 < ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64)))) {
        asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 4096) + ((cos_sin_ub_version_counter_1 % 3) * 4096)) + 49152)]))), (__gm__ uint8_t*)((&(cos_sin_cache[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)4096) + (((int64_t)seqlen_offsets) * (int64_t)64))]))), 1, (min(min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 256), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 256), (min(min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 256));
      }
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      _rope_kernel_kernel_simd_vf_0(buf_dyn_shmem, cos_sin_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)32768) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)batch)) * ((int64_t)x_stride_b)))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 32768) + ((cos_sin_ub_version_counter_1 % 3) * 32768))]))), 1, (min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 1024), static_cast<asc_store_l2_cache_mode>(4), (min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 1024), (min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 1024));
      asc_sync_notify(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      cos_sin_ub_version_counter_1 = (cos_sin_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(2));
}

