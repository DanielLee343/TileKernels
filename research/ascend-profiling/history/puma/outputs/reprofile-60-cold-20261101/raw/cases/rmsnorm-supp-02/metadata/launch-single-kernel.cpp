#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void norm_forward_kernel_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t x_ub_version_counter_1) {
  vector_bool v = asc_create_mask_b32(PAT_ALL);
  auto zero = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v, MODE_ZEROING);
  for (uint16_t vector = (uint16_t)2; vector < (uint16_t)4; ++vector) {
    for (uint16_t row = (uint16_t)0; row < (uint16_t)32; ++row) {
      simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 8192) + ((x_ub_version_counter_1 % 3) * 8192)) + (((int32_t)row) * 256)) + (((int32_t)vector) * 64))])), 0, v);
    }
  }
}

__simd_vf__ inline void norm_forward_kernel_kernel_simd_vf_1(__ubuf__ uint8_t* buf_dyn_shmem, int32_t x_ub_version_counter_1) {
  vector_f32 sums[4];
  vector_f32 x;
  vector_f32 product_error[1];
  vector_f32 value_error[1];
  vector_f32 square_error[1];
  vector_f32 residual[1];
  vector_f32 refined[1];
  for (uint16_t row = (uint16_t)0; row < (uint16_t)32; ++row) {
    vector_bool v = asc_create_mask_b32(PAT_ALL);
    sums[0] = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v, MODE_ZEROING);
    vector_bool v_1 = asc_create_mask_b32(PAT_ALL);
    sums[1] = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v_1, MODE_ZEROING);
    vector_bool v_2 = asc_create_mask_b32(PAT_ALL);
    sums[2] = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v_2, MODE_ZEROING);
    vector_bool v_3 = asc_create_mask_b32(PAT_ALL);
    sums[3] = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v_3, MODE_ZEROING);
    x = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 8192) + ((x_ub_version_counter_1 % 3) * 8192)) + (((int32_t)row) * 256))])), 0);
    auto low = x;
    vector_bool v_4 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(sums[0])), low, low, v_4, MODE_ZEROING);
    x = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 8192) + ((x_ub_version_counter_1 % 3) * 8192)) + (((int32_t)row) * 256)) + 64)])), 0);
    auto low_1 = x;
    vector_bool v_5 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(sums[1])), low_1, low_1, v_5, MODE_ZEROING);
    x = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 8192) + ((x_ub_version_counter_1 % 3) * 8192)) + (((int32_t)row) * 256)) + 128)])), 0);
    auto low_2 = x;
    vector_bool v_6 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(sums[2])), low_2, low_2, v_6, MODE_ZEROING);
    x = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 8192) + ((x_ub_version_counter_1 % 3) * 8192)) + (((int32_t)row) * 256)) + 192)])), 0);
    auto low_3 = x;
    vector_bool v_7 = asc_create_mask_b32(PAT_ALL);
    simd_inst::vmula((&(sums[3])), low_3, low_3, v_7, MODE_ZEROING);
    vector_bool v_8 = asc_create_mask_b32(PAT_ALL);
    sums[0] = simd_inst::vadd(sums[0], sums[1], v_8, MODE_ZEROING);
    vector_bool v_9 = asc_create_mask_b32(PAT_ALL);
    sums[0] = simd_inst::vadd(sums[0], sums[2], v_9, MODE_ZEROING);
    vector_bool v_10 = asc_create_mask_b32(PAT_ALL);
    sums[0] = simd_inst::vadd(sums[0], sums[3], v_10, MODE_ZEROING);
    vector_bool v_11 = asc_create_mask_b32(PAT_ALL);
    auto square_sum = simd_inst::vcadd(sums[0], v_11, MODE_ZEROING);
    simd_inst::vsts_1st(square_sum, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((int32_t)row) + 49408)])), 0, v_11);
  }
  simd_inst::mem_bar(VST_VLD);
  auto a = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[49408])), 0);
  vector_bool v_12 = asc_create_mask_b32(PAT_ALL);
  auto reciprocal_c0_hi_vector = simd_inst::vdup<float>(float(0x1p-7f/*7.812500e-03*/), v_12, MODE_ZEROING);
  auto product = simd_inst::vmuls(a, float(0x1p-7f/*7.812500e-03*/), v_12, MODE_ZEROING);
  auto value = simd_inst::vadds(product, float(0x1.4f8b58p-17f/*1.000000e-05*/), v_12, MODE_ZEROING);
  auto virtual_c1 = simd_inst::vsub(value, product, v_12, MODE_ZEROING);
  auto product_sum_error = simd_inst::vsub(product, simd_inst::vsub(value, virtual_c1, v_12, MODE_ZEROING), v_12, MODE_ZEROING);
  auto c1_sum_error = simd_inst::vadds(simd_inst::vneg(virtual_c1, v_12, MODE_ZEROING), float(0x1.4f8b58p-17f/*1.000000e-05*/), v_12, MODE_ZEROING);
  auto sum_error = simd_inst::vadd(product_sum_error, c1_sum_error, v_12, MODE_ZEROING);
  product_error[0] = simd_inst::vneg(product, v_12, MODE_ZEROING);
  simd_inst::vmula((&(product_error[0])), a, reciprocal_c0_hi_vector, v_12, MODE_ZEROING);
  value_error[0] = simd_inst::vadd(product_error[0], sum_error, v_12, MODE_ZEROING);
  simd_inst::vmula((&(value_error[0])), a, simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v_12, MODE_ZEROING), v_12, MODE_ZEROING);
  value_error[0] = simd_inst::vadds(value_error[0], float(0x1.1c6d1ep-42f/*2.526212e-13*/), v_12, MODE_ZEROING);
  auto value_error_1 = value_error[0];
  auto estimate = simd_inst::vdiv_0ulp_ftz_true(simd_inst::vdup<float>(float(0x1p+0f/*1.000000e+00*/), v_12, MODE_ZEROING), simd_inst::vsqrt(value, v_12, MODE_ZEROING), v_12, MODE_ZEROING);
  auto estimate_squared = simd_inst::vmul(estimate, estimate, v_12, MODE_ZEROING);
  square_error[0] = simd_inst::vneg(estimate_squared, v_12, MODE_ZEROING);
  simd_inst::vmula((&(square_error[0])), estimate, estimate, v_12, MODE_ZEROING);
  residual[0] = simd_inst::vdup<float>(float(0x1p+0f/*1.000000e+00*/), v_12, MODE_ZEROING);
  auto negative_value = simd_inst::vneg(value, v_12, MODE_ZEROING);
  auto negative_value_error = simd_inst::vneg(value_error_1, v_12, MODE_ZEROING);
  simd_inst::vmula((&(residual[0])), negative_value, estimate_squared, v_12, MODE_ZEROING);
  simd_inst::vmula((&(residual[0])), negative_value, square_error[0], v_12, MODE_ZEROING);
  simd_inst::vmula((&(residual[0])), negative_value_error, estimate_squared, v_12, MODE_ZEROING);
  simd_inst::vmula((&(residual[0])), negative_value_error, square_error[0], v_12, MODE_ZEROING);
  refined[0] = estimate;
  simd_inst::vmula((&(refined[0])), simd_inst::vmuls(estimate, float(0x1p-1f/*5.000000e-01*/), v_12, MODE_ZEROING), residual[0], v_12, MODE_ZEROING);
  auto rstd_values = refined[0];
  for (uint16_t pair = (uint16_t)0; pair < (uint16_t)2; ++pair) {
    auto w0 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((int32_t)pair) * 128) + 49152)])), 0);
    auto w1 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((int32_t)pair) * 128) + 49216)])), 0);
    for (uint16_t _ = (uint16_t)0; _ < (uint16_t)32; ++_) {
        vector_u32 v_ = simd_inst::vselr((*(vector_u32 *)(&(rstd_values))), simd_inst::vdup<uint32_t>(_, v_12, MODE_ZEROING));
      auto inv_rms = (*(vector_f32 *)(&(v_)));
      auto x0 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 8192) + ((x_ub_version_counter_1 % 3) * 8192)) + (((int32_t)_) * 256)) + (((int32_t)pair) * 128))])), 0);
      auto x1 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 8192) + ((x_ub_version_counter_1 % 3) * 8192)) + (((int32_t)_) * 256)) + (((int32_t)pair) * 128)) + 64)])), 0);
      auto y0 = simd_inst::vmul(x0, inv_rms, v_12, MODE_ZEROING);
      auto y1 = simd_inst::vmul(x1, inv_rms, v_12, MODE_ZEROING);
      auto x0_1 = simd_inst::vmul(y0, w0, v_12, MODE_ZEROING);
      auto x1_1 = simd_inst::vmul(y1, w1, v_12, MODE_ZEROING);
      simd_inst::vsts_norm(x0_1, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 8192) + ((x_ub_version_counter_1 % 3) * 8192)) + (((int32_t)_) * 256)) + (((int32_t)pair) * 128)) + 24576)])), 0, v_12);
      simd_inst::vsts_norm(x1_1, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 8192) + ((x_ub_version_counter_1 % 3) * 8192)) + (((int32_t)_) * 256)) + (((int32_t)pair) * 128)) + 24640)])), 0, v_12);
    }
  }
}

extern "C" __global__ __vector__ void norm_forward_kernel_kernel(__gm__ float* out, __gm__ float* weight, __gm__ float* x, int32_t batch, int32_t num_tokens, int32_t out_batch_stride, int32_t out_stride, int32_t x_batch_stride, int32_t x_stride) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t rows_per_block = 0;
  int32_t x_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  x_ub_version_counter_1 = 0;
  asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[49152]))), (__gm__ uint8_t*)((&(weight[0]))), 1, 512, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 512, 512);
  asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(3));
  rows_per_block = min(max(((((num_tokens + 1791) / 1792) * 32) + ((((num_tokens + 1791) % 1792) >> 31) * 32)), 4), 128);
  int32_t rmod = (((num_tokens + rows_per_block) - 1) % rows_per_block);
  int32_t rdiv = (((num_tokens + rows_per_block) - 1) / rows_per_block);
  int32_t num_token_blocks = ((((0 <= rows_per_block) && (0 <= rmod)) || ((rows_per_block < 0) && (rmod <= 0))) ? rdiv : (rdiv - 1));
  asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(3));
  for (int32_t w = 0; w < (((num_token_blocks * batch) + 55) / 56); ++w) {
    int32_t token_base = 0;
    if ((((w * 56) + ((int32_t)block_idx)) / batch) < num_token_blocks) {
      token_base = ((((w * 56) + ((int32_t)block_idx)) / batch) * rows_per_block);
    }
    int32_t __loop_bound_0 = 0;
    if ((((w * 56) + ((int32_t)block_idx)) / batch) < num_token_blocks) {
      __loop_bound_0 = (rows_per_block >> 5);
      for (int32_t tile_index = 0; tile_index < __loop_bound_0; ++tile_index) {
        bool __cond_0 = (((tile_index * 32) + token_base) < num_tokens);
        if (__cond_0) {
          norm_forward_kernel_kernel_simd_vf_0(buf_dyn_shmem, x_ub_version_counter_1);
          asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
          if ((0 < (batch - (((w * 56) + ((int32_t)block_idx)) % batch))) && (0 < ((num_tokens - token_base) - (tile_index * 32)))) {
            asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 8192) + ((x_ub_version_counter_1 % 3) * 8192))]))), (__gm__ uint8_t*)((&(x[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)batch)) * ((int64_t)x_batch_stride)) + (((((int64_t)tile_index) * (int64_t)32) + ((int64_t)token_base)) * ((int64_t)x_stride)))]))), min(32, max(((num_tokens - token_base) - (tile_index * 32)), 0)), 512, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(4), (x_stride * 4), 1024);
          }
          asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
          asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
          asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
          norm_forward_kernel_kernel_simd_vf_1(buf_dyn_shmem, x_ub_version_counter_1);
          asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
          asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
          asc_sync_pipe(PIPE_MTE3);
          asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
          if ((0 < ((num_tokens - token_base) - (tile_index * 32))) && (0 < (batch - (((w * 56) + ((int32_t)block_idx)) % batch)))) {
            asc_copy_ub2gm_align((__gm__ uint8_t*)((&(out[(((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % ((int64_t)batch)) * ((int64_t)out_batch_stride)) + (((((int64_t)tile_index) * (int64_t)32) + ((int64_t)token_base)) * ((int64_t)out_stride)))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 8192) + ((x_ub_version_counter_1 % 3) * 8192)) + 24576)]))), min(32, max(((num_tokens - token_base) - (tile_index * 32)), 0)), 512, static_cast<asc_store_l2_cache_mode>(4), (out_stride * 4), 1024);
          }
          asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
          x_ub_version_counter_1 = (x_ub_version_counter_1 + 1);
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

