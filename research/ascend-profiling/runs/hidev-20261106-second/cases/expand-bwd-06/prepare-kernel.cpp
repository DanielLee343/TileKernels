#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void expand_to_mhc_bwd_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t o_grad_ub_version_counter_1) {
  vector_f32 acc;
  vector_bool mask_32b = asc_create_mask_b32(PAT_ALL);
  vector_bool mask_16b = asc_create_mask_b16(PAT_ALL);
  for (int32_t c = 0; c < 56; ++c) {
    acc = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) * 14336) + ((o_grad_ub_version_counter_1 % 3) * 14336)) + (c * 64))])), 0), mask_16b, PART_EVEN, MODE_ZEROING);
    auto og = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) * 14336) + ((o_grad_ub_version_counter_1 % 3) * 14336)) + (c * 64)) + 3584)])), 0), mask_16b, PART_EVEN, MODE_ZEROING);
    acc = simd_inst::vadd(acc, og, mask_32b, MODE_ZEROING);
    auto og_1 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) * 14336) + ((o_grad_ub_version_counter_1 % 3) * 14336)) + (c * 64)) + 7168)])), 0), mask_16b, PART_EVEN, MODE_ZEROING);
    acc = simd_inst::vadd(acc, og_1, mask_32b, MODE_ZEROING);
    auto og_2 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) * 14336) + ((o_grad_ub_version_counter_1 % 3) * 14336)) + (c * 64)) + 10752)])), 0), mask_16b, PART_EVEN, MODE_ZEROING);
    acc = simd_inst::vadd(acc, og_2, mask_32b, MODE_ZEROING);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(acc, mask_32b, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) * 3584) + ((o_grad_ub_version_counter_1 % 3) * 3584)) + (c * 64)) + 43008)])), 0, mask_32b);
  }
}

extern "C" __global__ __vector__ void expand_to_mhc_bwd_asc_kernel(__gm__ bfloat16_t* o_grad, __gm__ bfloat16_t* x_grad, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t o_grad_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  o_grad_ub_version_counter_1 = 0;
  for (int32_t w = 0; w < ((num_tokens + 27) / 28); ++w) {
    if ((((w * 56) + ((int32_t)block_idx)) / num_tokens) < 2) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) + (o_grad_ub_version_counter_1 % 3))));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) * 14336) + ((o_grad_ub_version_counter_1 % 3) * 14336))]))), (__gm__ uint8_t*)((&(o_grad[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)num_tokens)) * (int64_t)28672) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)num_tokens)) * (int64_t)3584))]))), 4, 7168, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 14336, 7168);
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) + (o_grad_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) + (o_grad_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) + (o_grad_ub_version_counter_1 % 3))));
      expand_to_mhc_bwd_asc_kernel_simd_vf_0(buf_dyn_shmem, o_grad_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) + (o_grad_ub_version_counter_1 % 3))));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) + (o_grad_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) + (o_grad_ub_version_counter_1 % 3))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(x_grad[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)num_tokens)) * (int64_t)7168) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)num_tokens)) * (int64_t)3584))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) * 3584) + ((o_grad_ub_version_counter_1 % 3) * 3584)) + 43008)]))), 1, 7168, static_cast<asc_store_l2_cache_mode>(4), 7168, 7168);
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((o_grad_ub_version_counter_1 % 3) >> 31)) + (o_grad_ub_version_counter_1 % 3))));
      o_grad_ub_version_counter_1 = (o_grad_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
}

