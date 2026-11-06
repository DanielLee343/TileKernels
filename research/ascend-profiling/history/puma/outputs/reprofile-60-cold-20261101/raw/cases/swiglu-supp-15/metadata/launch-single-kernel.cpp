#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void swiglu_forward_kernel_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t xl_ub_version_counter_1) {
  vector_bool v = asc_create_mask_b32(PAT_ALL);
  auto zeros = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v, MODE_ZEROING);
  for (int32_t tile_id = 0; tile_id < 32; ++tile_id) {
    vector_bool v_1 = asc_create_mask_b16(PAT_ALL);
    auto silu_l = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + (tile_id * 256))])), 0), v_1, PART_EVEN, MODE_ZEROING);
    auto mul_r = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + (tile_id * 256)) + 24576)])), 0), v_1, PART_EVEN, MODE_ZEROING);
    auto denominator = simd_inst::vadds(simd_inst::vexpdif(zeros, silu_l, v), float(0x1p+0f/*1.000000e+00*/), v, MODE_ZEROING);
    auto quotient = simd_inst::vdiv_0ulp_ftz_true(silu_l, denominator, v, MODE_ZEROING);
    auto out_val = simd_inst::vmul(quotient, mul_r, v, MODE_ZEROING);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(out_val, v_1, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + (tile_id * 256)) + 49152)])), 0, v_1);
    vector_bool v_2 = asc_create_mask_b16(PAT_ALL);
    auto silu_l_1 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + (tile_id * 256)) + 64)])), 0), v_2, PART_EVEN, MODE_ZEROING);
    auto mul_r_1 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + (tile_id * 256)) + 24640)])), 0), v_2, PART_EVEN, MODE_ZEROING);
    auto denominator_1 = simd_inst::vadds(simd_inst::vexpdif(zeros, silu_l_1, v), float(0x1p+0f/*1.000000e+00*/), v, MODE_ZEROING);
    auto quotient_1 = simd_inst::vdiv_0ulp_ftz_true(silu_l_1, denominator_1, v, MODE_ZEROING);
    auto out_val_1 = simd_inst::vmul(quotient_1, mul_r_1, v, MODE_ZEROING);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(out_val_1, v_2, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + (tile_id * 256)) + 49216)])), 0, v_2);
    vector_bool v_3 = asc_create_mask_b16(PAT_ALL);
    auto silu_l_2 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + (tile_id * 256)) + 128)])), 0), v_3, PART_EVEN, MODE_ZEROING);
    auto mul_r_2 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + (tile_id * 256)) + 24704)])), 0), v_3, PART_EVEN, MODE_ZEROING);
    auto denominator_2 = simd_inst::vadds(simd_inst::vexpdif(zeros, silu_l_2, v), float(0x1p+0f/*1.000000e+00*/), v, MODE_ZEROING);
    auto quotient_2 = simd_inst::vdiv_0ulp_ftz_true(silu_l_2, denominator_2, v, MODE_ZEROING);
    auto out_val_2 = simd_inst::vmul(quotient_2, mul_r_2, v, MODE_ZEROING);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(out_val_2, v_3, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + (tile_id * 256)) + 49280)])), 0, v_3);
    vector_bool v_4 = asc_create_mask_b16(PAT_ALL);
    auto silu_l_3 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + (tile_id * 256)) + 192)])), 0), v_4, PART_EVEN, MODE_ZEROING);
    auto mul_r_3 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + (tile_id * 256)) + 24768)])), 0), v_4, PART_EVEN, MODE_ZEROING);
    auto denominator_3 = simd_inst::vadds(simd_inst::vexpdif(zeros, silu_l_3, v), float(0x1p+0f/*1.000000e+00*/), v, MODE_ZEROING);
    auto quotient_3 = simd_inst::vdiv_0ulp_ftz_true(silu_l_3, denominator_3, v, MODE_ZEROING);
    auto out_val_3 = simd_inst::vmul(quotient_3, mul_r_3, v, MODE_ZEROING);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(out_val_3, v_4, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + (tile_id * 256)) + 49344)])), 0, v_4);
  }
}

extern "C" __global__ __vector__ void swiglu_forward_kernel_kernel(__gm__ bfloat16_t* out, __gm__ bfloat16_t* x, int32_t num_expanded_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t token_base = 0;
  int32_t token_id = 0;
  int8_t valid = (int8_t)0;
  float weight = float(0x0p+0f/*0.000000e+00*/);
  int32_t xl_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  xl_ub_version_counter_1 = 0;
  for (int32_t w = 0; w < ((num_expanded_tokens + 55) / 56); ++w) {
    if (((w * 56) + ((int32_t)block_idx)) < num_expanded_tokens) {
      token_base = ((w * 56) + ((int32_t)block_idx));
    }
    int8_t valid_group = ((int8_t)(bool)0);
    if (((w * 56) + ((int32_t)block_idx)) < num_expanded_tokens) {
      valid_group = ((int8_t)(token_base < num_expanded_tokens));
      if ((bool)valid_group) {
        token_id = token_base;
        int32_t token_id_1 = token_id;
        valid = ((int8_t)(token_id_1 < num_expanded_tokens));
        bool valid_1 = ((bool)valid);
        int32_t token_id_2 = 0;
        if (valid_1) {
          token_id_2 = token_id;
          weight = float(0x1p+0f/*1.000000e+00*/);
        }
        int32_t token_id_3 = 0;
        if (valid_1) {
          token_id_3 = token_id;
          asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((xl_ub_version_counter_1 % 3) >> 31)) + (xl_ub_version_counter_1 % 3))));
          if (0 < (num_expanded_tokens - token_id_2)) {
            asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192))]))), (__gm__ uint8_t*)((&(x[(((int64_t)token_id_2) * (int64_t)16384)]))), 1, 16384, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 16384, 16384);
          }
          if (0 < (num_expanded_tokens - token_id_2)) {
            asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + 24576)]))), (__gm__ uint8_t*)((&(x[((((int64_t)token_id_2) * (int64_t)16384) + (int64_t)8192)]))), 1, 16384, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 16384, 16384);
          }
          asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((xl_ub_version_counter_1 % 3) >> 31)) + (xl_ub_version_counter_1 % 3))));
          asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((xl_ub_version_counter_1 % 3) >> 31)) + (xl_ub_version_counter_1 % 3))));
          asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((xl_ub_version_counter_1 % 3) >> 31)) + (xl_ub_version_counter_1 % 3))));
          swiglu_forward_kernel_kernel_simd_vf_0(buf_dyn_shmem, xl_ub_version_counter_1);
          asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((xl_ub_version_counter_1 % 3) >> 31)) + (xl_ub_version_counter_1 % 3))));
          asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((xl_ub_version_counter_1 % 3) >> 31)) + (xl_ub_version_counter_1 % 3))));
          asc_sync_pipe(PIPE_MTE3);
          asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((xl_ub_version_counter_1 % 3) >> 31)) + (xl_ub_version_counter_1 % 3))));
          if (0 < (num_expanded_tokens - token_id_3)) {
            asc_copy_ub2gm_align((__gm__ uint8_t*)((&(out[(((int64_t)token_id_3) * (int64_t)8192)]))), (__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((xl_ub_version_counter_1 % 3) >> 31)) * 8192) + ((xl_ub_version_counter_1 % 3) * 8192)) + 49152)]))), 1, 16384, static_cast<asc_store_l2_cache_mode>(4), 16384, 16384);
          }
          asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((xl_ub_version_counter_1 % 3) >> 31)) + (xl_ub_version_counter_1 % 3))));
          xl_ub_version_counter_1 = (xl_ub_version_counter_1 + 1);
        }
      }
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
}

