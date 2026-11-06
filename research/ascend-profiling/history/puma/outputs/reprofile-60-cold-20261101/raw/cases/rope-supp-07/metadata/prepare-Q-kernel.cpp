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
    auto cos_sin_values = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 4096) + ((cos_sin_ub_version_counter_1 % 3) * 4096)) + (row * 64))])), 0);
      vector_u32 v_ = simd_inst::vselr((*(vector_u32 *)(&(cos_sin_values))), (*(vector_u32 *)(&(cos_indices))));
    auto cosine = (*(vector_f32 *)(&(v_)));
      vector_u32 v__1 = simd_inst::vselr((*(vector_u32 *)(&(cos_sin_values))), (*(vector_u32 *)(&(sin_indices))));
    auto neg_sine = (*(vector_f32 *)(&(v__1)));
    auto sine = simd_inst::vneg(neg_sine, v, MODE_ZEROING);
    vector_bool v_1 = asc_create_mask_b16(PAT_ALL);
    first = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 4096) + ((cos_sin_ub_version_counter_1 % 3) * 4096)) + (row * 64)) + 24576)])), 0), v_1, PART_EVEN, MODE_ZEROING);
    second = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 4096) + ((cos_sin_ub_version_counter_1 % 3) * 4096)) + (row * 64)) + 24576)])), 0), v_1, PART_EVEN, MODE_ZEROING);
    auto first_1 = first;
    auto second_1 = second;
    auto v_2 = simd_inst::vdintlv(first_1, second_1);
    out_first = simd_inst::vmul(v_2.v1, sine, v, MODE_ZEROING);
    simd_inst::vmula((&(out_first)), v_2.v0, cosine, v, MODE_ZEROING);
    out_second = simd_inst::vmul(v_2.v1, cosine, v, MODE_ZEROING);
    simd_inst::vmula((&(out_second)), v_2.v0, neg_sine, v, MODE_ZEROING);
    auto first_2 = out_first;
    auto second_2 = out_second;
    auto v_3 = simd_inst::vintlv(first_2, second_2);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(v_3.v0, v_1, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 4096) + ((cos_sin_ub_version_counter_1 % 3) * 4096)) + (row * 64)) + 24576)])), 0, v_1);
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
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 4096) + ((cos_sin_ub_version_counter_1 % 3) * 4096)) + 24576)]))), (__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)4096) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)batch)) * ((int64_t)x_stride_b)))]))), 1, (min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 128), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(4), (min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 128), (min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 128));
      if ((0 < (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) && (0 < ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64)))) {
        asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 4096) + ((cos_sin_ub_version_counter_1 % 3) * 4096))]))), (__gm__ uint8_t*)((&(cos_sin_cache[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)4096) + (((int64_t)seqlen_offsets) * (int64_t)64))]))), 1, (min(min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 256), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 256), (min(min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))), ((seqlen_ro - seqlen_offsets) - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 256));
      }
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      _rope_kernel_kernel_simd_vf_0(buf_dyn_shmem, cos_sin_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)batch)) * (int64_t)4096) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)batch)) * ((int64_t)x_stride_b)))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) * 4096) + ((cos_sin_ub_version_counter_1 % 3) * 4096)) + 24576)]))), 1, (min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 128), static_cast<asc_store_l2_cache_mode>(4), (min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 128), (min(64, (seqlen - ((((w * 56) + ((int32_t)block_idx)) / batch) * 64))) * 128));
      asc_sync_notify(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(((3 & ((cos_sin_ub_version_counter_1 % 3) >> 31)) + (cos_sin_ub_version_counter_1 % 3))));
      cos_sin_ub_version_counter_1 = (cos_sin_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_MTE2, static_cast<event_t>(2));
}

