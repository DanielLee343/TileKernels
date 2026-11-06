#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void mhc_pre_apply_mix_fwd_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t mix_ub_version_counter_1) {
  vector_f32 mix_reg[4];
  vector_f32 xs[4];
  vector_f32 acc;
  mix_reg[0] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((mix_ub_version_counter_1 % 3) >> 31)) * 8) + ((mix_ub_version_counter_1 % 3) * 8)) + 19200)])), 0);
  mix_reg[1] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((mix_ub_version_counter_1 % 3) >> 31)) * 8) + ((mix_ub_version_counter_1 % 3) * 8)) + 19201)])), 0);
  mix_reg[2] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((mix_ub_version_counter_1 % 3) >> 31)) * 8) + ((mix_ub_version_counter_1 % 3) * 8)) + 19202)])), 0);
  mix_reg[3] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((mix_ub_version_counter_1 % 3) >> 31)) * 8) + ((mix_ub_version_counter_1 % 3) * 8)) + 19203)])), 0);
  for (int32_t c = 0; c < 40; ++c) {
    vector_bool v = asc_create_mask_b16(PAT_ALL);
    xs[0] = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((mix_ub_version_counter_1 % 3) * 10240)) + (c * 64))])), 0), v, PART_EVEN, MODE_ZEROING);
    vector_bool v_1 = asc_create_mask_b16(PAT_ALL);
    xs[1] = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((mix_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 2560)])), 0), v_1, PART_EVEN, MODE_ZEROING);
    vector_bool v_2 = asc_create_mask_b16(PAT_ALL);
    xs[2] = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((mix_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 5120)])), 0), v_2, PART_EVEN, MODE_ZEROING);
    vector_bool v_3 = asc_create_mask_b16(PAT_ALL);
    xs[3] = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((mix_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 7680)])), 0), v_3, PART_EVEN, MODE_ZEROING);
    vector_bool v_4 = asc_create_mask_b32(PAT_ALL);
    acc = simd_inst::vmul(xs[0], mix_reg[0], v_4, MODE_ZEROING);
    simd_inst::vmula((&(acc)), xs[1], mix_reg[1], v_4, MODE_ZEROING);
    simd_inst::vmula((&(acc)), xs[2], mix_reg[2], v_4, MODE_ZEROING);
    simd_inst::vmula((&(acc)), xs[3], mix_reg[3], v_4, MODE_ZEROING);
    vector_bool v_5 = asc_create_mask_b16(PAT_ALL);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(acc, v_5, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((mix_ub_version_counter_1 % 3) >> 31)) * 2560) + ((mix_ub_version_counter_1 % 3) * 2560)) + (c * 64)) + 30720)])), 0, v_5);
  }
}

extern "C" __global__ __vector__ void mhc_pre_apply_mix_fwd_asc_kernel(__gm__ float* mix, __gm__ bfloat16_t* o, __gm__ bfloat16_t* x, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t mix_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  mix_ub_version_counter_1 = 0;
  for (int32_t w = 0; w < ((num_tokens + 55) / 56); ++w) {
    if ((((w * 56) + ((int32_t)block_idx)) / num_tokens) < 1) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((mix_ub_version_counter_1 % 3) >> 31)) + (mix_ub_version_counter_1 % 3))));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((mix_ub_version_counter_1 % 3) >> 31)) * 8) + ((mix_ub_version_counter_1 % 3) * 8)) + 19200)]))), (__gm__ uint8_t*)((&(mix[((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)num_tokens)) * (int64_t)4)]))), 1, 16, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 16, 16);
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((3 & ((mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((mix_ub_version_counter_1 % 3) * 10240))]))), (__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)num_tokens)) * (int64_t)10240) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)num_tokens)) * (int64_t)2560))]))), 1, 20480, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 20480, 20480);
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((mix_ub_version_counter_1 % 3) >> 31)) + (mix_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((mix_ub_version_counter_1 % 3) >> 31)) + (mix_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((mix_ub_version_counter_1 % 3) >> 31)) + (mix_ub_version_counter_1 % 3))));
      mhc_pre_apply_mix_fwd_asc_kernel_simd_vf_0(buf_dyn_shmem, mix_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((mix_ub_version_counter_1 % 3) >> 31)) + (mix_ub_version_counter_1 % 3))));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((mix_ub_version_counter_1 % 3) >> 31)) + (mix_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((mix_ub_version_counter_1 % 3) >> 31)) + (mix_ub_version_counter_1 % 3))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(o[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)num_tokens)) * (int64_t)2560) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)num_tokens)) * (int64_t)2560))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((mix_ub_version_counter_1 % 3) >> 31)) * 2560) + ((mix_ub_version_counter_1 % 3) * 2560)) + 30720)]))), 1, 5120, static_cast<asc_store_l2_cache_mode>(4), 5120, 5120);
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((mix_ub_version_counter_1 % 3) >> 31)) + (mix_ub_version_counter_1 % 3))));
      mix_ub_version_counter_1 = (mix_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
}

