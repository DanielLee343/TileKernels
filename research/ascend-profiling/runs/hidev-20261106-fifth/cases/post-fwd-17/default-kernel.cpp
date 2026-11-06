#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void mhc_post_fwd_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t comb_res_mix_ub_version_counter_1) {
  vector_f32 comb_mix[16];
  vector_f32 post_mix[4];
  vector_f32 out_reg[4];
  vector_f32 res[4];
  comb_mix[0] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34560)])), 0);
  comb_mix[1] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34561)])), 0);
  comb_mix[2] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34562)])), 0);
  comb_mix[3] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34563)])), 0);
  comb_mix[4] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34564)])), 0);
  comb_mix[5] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34565)])), 0);
  comb_mix[6] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34566)])), 0);
  comb_mix[7] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34567)])), 0);
  comb_mix[8] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34568)])), 0);
  comb_mix[9] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34569)])), 0);
  comb_mix[10] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34570)])), 0);
  comb_mix[11] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34571)])), 0);
  comb_mix[12] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34572)])), 0);
  comb_mix[13] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34573)])), 0);
  comb_mix[14] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34574)])), 0);
  comb_mix[15] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34575)])), 0);
  post_mix[0] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 8) + ((comb_res_mix_ub_version_counter_1 % 3) * 8)) + 34608)])), 0);
  post_mix[1] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 8) + ((comb_res_mix_ub_version_counter_1 % 3) * 8)) + 34609)])), 0);
  post_mix[2] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 8) + ((comb_res_mix_ub_version_counter_1 % 3) * 8)) + 34610)])), 0);
  post_mix[3] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 8) + ((comb_res_mix_ub_version_counter_1 % 3) * 8)) + 34611)])), 0);
  for (int32_t c = 0; c < 40; ++c) {
    vector_bool v = asc_create_mask_b16(PAT_ALL);
    auto x_f32 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 2560) + ((comb_res_mix_ub_version_counter_1 % 3) * 2560)) + (c * 64)) + 61440)])), 0), v, PART_EVEN, MODE_ZEROING);
    res[0] = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((comb_res_mix_ub_version_counter_1 % 3) * 10240)) + (c * 64))])), 0), v, PART_EVEN, MODE_ZEROING);
    res[1] = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((comb_res_mix_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 2560)])), 0), v, PART_EVEN, MODE_ZEROING);
    res[2] = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((comb_res_mix_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 5120)])), 0), v, PART_EVEN, MODE_ZEROING);
    res[3] = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((comb_res_mix_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 7680)])), 0), v, PART_EVEN, MODE_ZEROING);
    vector_bool v_1 = asc_create_mask_b32(PAT_ALL);
    out_reg[0] = simd_inst::vmul(x_f32, post_mix[0], v_1, MODE_ZEROING);
    vector_bool v_2 = asc_create_mask_b32(PAT_ALL);
    out_reg[1] = simd_inst::vmul(x_f32, post_mix[1], v_2, MODE_ZEROING);
    vector_bool v_3 = asc_create_mask_b32(PAT_ALL);
    out_reg[2] = simd_inst::vmul(x_f32, post_mix[2], v_3, MODE_ZEROING);
    vector_bool v_4 = asc_create_mask_b32(PAT_ALL);
    out_reg[3] = simd_inst::vmul(x_f32, post_mix[3], v_4, MODE_ZEROING);
    vector_bool v_5 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[0])), res[0], comb_mix[0], v_5, MODE_ZEROING);
    vector_bool v_6 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[1])), res[0], comb_mix[1], v_6, MODE_ZEROING);
    vector_bool v_7 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[2])), res[0], comb_mix[2], v_7, MODE_ZEROING);
    vector_bool v_8 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[3])), res[0], comb_mix[3], v_8, MODE_ZEROING);
    vector_bool v_9 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[0])), res[1], comb_mix[4], v_9, MODE_ZEROING);
    vector_bool v_10 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[1])), res[1], comb_mix[5], v_10, MODE_ZEROING);
    vector_bool v_11 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[2])), res[1], comb_mix[6], v_11, MODE_ZEROING);
    vector_bool v_12 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[3])), res[1], comb_mix[7], v_12, MODE_ZEROING);
    vector_bool v_13 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[0])), res[2], comb_mix[8], v_13, MODE_ZEROING);
    vector_bool v_14 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[1])), res[2], comb_mix[9], v_14, MODE_ZEROING);
    vector_bool v_15 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[2])), res[2], comb_mix[10], v_15, MODE_ZEROING);
    vector_bool v_16 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[3])), res[2], comb_mix[11], v_16, MODE_ZEROING);
    vector_bool v_17 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[0])), res[3], comb_mix[12], v_17, MODE_ZEROING);
    vector_bool v_18 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[1])), res[3], comb_mix[13], v_18, MODE_ZEROING);
    vector_bool v_19 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[2])), res[3], comb_mix[14], v_19, MODE_ZEROING);
    vector_bool v_20 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(out_reg[3])), res[3], comb_mix[15], v_20, MODE_ZEROING);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(out_reg[0], v, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((comb_res_mix_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 30720)])), 0, v);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(out_reg[1], v, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((comb_res_mix_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 33280)])), 0, v);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(out_reg[2], v, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((comb_res_mix_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 35840)])), 0, v);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(out_reg[3], v, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((comb_res_mix_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 38400)])), 0, v);
  }
}

extern "C" __global__ __vector__ void mhc_post_fwd_asc_kernel(__gm__ float* comb_res_mix, __gm__ bfloat16_t* out, __gm__ float* post_layer_mix, __gm__ bfloat16_t* residual, __gm__ bfloat16_t* x, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t comb_res_mix_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  comb_res_mix_ub_version_counter_1 = 0;
  for (int32_t w = 0; w < ((num_tokens + 27) / 28); ++w) {
    if ((((w * 56) + ((int32_t)block_idx)) / num_tokens) < 2) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) + (comb_res_mix_ub_version_counter_1 % 3))));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 16) + ((comb_res_mix_ub_version_counter_1 % 3) * 16)) + 34560)]))), (__gm__ uint8_t*)((&(comb_res_mix[((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)num_tokens)) * (int64_t)16)]))), 1, 64, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 64, 64);
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 8) + ((comb_res_mix_ub_version_counter_1 % 3) * 8)) + 34608)]))), (__gm__ uint8_t*)((&(post_layer_mix[((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)num_tokens)) * (int64_t)4)]))), 1, 16, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 16, 16);
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((comb_res_mix_ub_version_counter_1 % 3) * 10240))]))), (__gm__ uint8_t*)((&(residual[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)num_tokens)) * (int64_t)20480) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)num_tokens)) * (int64_t)2560))]))), 4, 5120, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 10240, 5120);
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 2560) + ((comb_res_mix_ub_version_counter_1 % 3) * 2560)) + 61440)]))), (__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)num_tokens)) * (int64_t)5120) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)num_tokens)) * (int64_t)2560))]))), 1, 5120, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 5120, 5120);
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) + (comb_res_mix_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) + (comb_res_mix_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) + (comb_res_mix_ub_version_counter_1 % 3))));
      mhc_post_fwd_asc_kernel_simd_vf_0(buf_dyn_shmem, comb_res_mix_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) + (comb_res_mix_ub_version_counter_1 % 3))));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) + (comb_res_mix_ub_version_counter_1 % 3))));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) + (comb_res_mix_ub_version_counter_1 % 3))));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(out[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)num_tokens)) * (int64_t)20480) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / ((int64_t)num_tokens)) * (int64_t)2560))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) * 10240) + ((comb_res_mix_ub_version_counter_1 % 3) * 10240)) + 30720)]))), 4, 5120, static_cast<asc_store_l2_cache_mode>(4), 10240, 5120);
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((comb_res_mix_ub_version_counter_1 % 3) >> 31)) + (comb_res_mix_ub_version_counter_1 % 3))));
      comb_res_mix_ub_version_counter_1 = (comb_res_mix_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
}

