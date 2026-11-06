#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void engram_fused_weight_kernel_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t hidden_ub_version_counter_1) {
  vector_bool v = asc_create_mask_b16(PAT_ALL);
  auto hidden_f32 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 1536)])), 0), v, PART_EVEN, MODE_ZEROING);
  auto embed_f32 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 2304)])), 0), v, PART_EVEN, MODE_ZEROING);
  vector_bool v_1 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_norm(simd_inst::vmul(hidden_f32, embed_f32, v_1, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256))])), 0, v_1);
  vector_bool v_2 = asc_create_mask_b16(PAT_ALL);
  auto hidden_f32_1 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 1600)])), 0), v_2, PART_EVEN, MODE_ZEROING);
  auto embed_f32_1 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 2368)])), 0), v_2, PART_EVEN, MODE_ZEROING);
  vector_bool v_3 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_norm(simd_inst::vmul(hidden_f32_1, embed_f32_1, v_3, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 64)])), 0, v_3);
  vector_bool v_4 = asc_create_mask_b16(PAT_ALL);
  auto hidden_f32_2 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 1664)])), 0), v_4, PART_EVEN, MODE_ZEROING);
  auto embed_f32_2 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 2432)])), 0), v_4, PART_EVEN, MODE_ZEROING);
  vector_bool v_5 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_norm(simd_inst::vmul(hidden_f32_2, embed_f32_2, v_5, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 128)])), 0, v_5);
  vector_bool v_6 = asc_create_mask_b16(PAT_ALL);
  auto hidden_f32_3 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 1728)])), 0), v_6, PART_EVEN, MODE_ZEROING);
  auto embed_f32_3 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 2496)])), 0), v_6, PART_EVEN, MODE_ZEROING);
  vector_bool v_7 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_norm(simd_inst::vmul(hidden_f32_3, embed_f32_3, v_7, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 192)])), 0, v_7);
}

extern "C" __global__ __vector__ void engram_fused_weight_kernel_asc_kernel(__gm__ bfloat16_t* weight_embed, __gm__ float* weight_fused, __gm__ bfloat16_t* weight_hidden) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t hidden_ub_version_counter_1 = 0;
  hidden_ub_version_counter_1 = 0;
  if (((int32_t)block_idx) < 28) {
    asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 1536)]))), (__gm__ uint8_t*)((&(weight_hidden[(((((int32_t)block_idx) % 4) * 1792) + ((((int32_t)block_idx) / 4) * 256))]))), 1, 512, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 512, 512);
    asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256)) + 2304)]))), (__gm__ uint8_t*)((&(weight_embed[(((((int32_t)block_idx) % 4) * 1792) + ((((int32_t)block_idx) / 4) * 256))]))), 1, 512, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 512, 512);
    asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) + (hidden_ub_version_counter_1 % 3))));
    asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) + (hidden_ub_version_counter_1 % 3))));
    engram_fused_weight_kernel_asc_kernel_simd_vf_0(buf_dyn_shmem, hidden_ub_version_counter_1);
    asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) + (hidden_ub_version_counter_1 % 3))));
    asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) + (hidden_ub_version_counter_1 % 3))));
    asc_copy_ub2gm_align((__gm__ uint8_t*)((&(weight_fused[(((((int32_t)block_idx) % 4) * 1792) + ((((int32_t)block_idx) / 4) * 256))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((hidden_ub_version_counter_1 % 3) >> 31)) * 256) + ((hidden_ub_version_counter_1 % 3) * 256))]))), 1, 1024, static_cast<asc_store_l2_cache_mode>(4), 1024, 1024);
    hidden_ub_version_counter_1 = (hidden_ub_version_counter_1 + 1);
  }
}

