#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void mhc_reduce_partials_and_rmsnorm_bwd_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t out_grad_ub_version_counter_1) {
  vector_f32 sq_grad_compact;
  vector_bool mask_full = asc_create_mask_b32(PAT_ALL);
  vector_bool mask_lane0 = asc_create_mask_b32(PAT_VL1);
  vector_bool mask_first_token = asc_create_mask_b32(PAT_VL32);
  auto lane_idx = simd_inst::vci<int32_t>(0, INC_ORDER);
  auto first_token_mask = simd_inst::vcmps_lt(lane_idx, 24, mask_full);
  auto second_token_mask = simd_inst::pand(simd_inst::vcmps_ge(lane_idx, 32, mask_full), simd_inst::vcmps_lt(lane_idx, 56, mask_full), mask_full);
  auto inv_rms_group_size = simd_inst::vdup<float>(float(0x1.999999999999ap-11f/*7.812500e-04*/), mask_full, MODE_ZEROING);
  auto one = simd_inst::vdup<float>(float(0x1p+0f/*1.000000e+00*/), mask_full, MODE_ZEROING);
  auto neg_half = simd_inst::vdup<float>(float(-0x1p-1f/*-5.000000e-01*/), mask_full, MODE_ZEROING);
  auto grad_pair = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512))])), 0);
  auto mul_pair = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 3072)])), 0);
  auto sq_even = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10368)])), 0);
  auto sq_odd = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10369)])), 0);
  auto rms_even = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_even, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_odd = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_odd, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_pair = simd_inst::vsel(rms_even, rms_odd, mask_first_token);
  auto grad_mul = simd_inst::vmul(grad_pair, mul_pair, mask_full, MODE_ZEROING);
  auto out_mul_grad_pair = simd_inst::vmul(grad_pair, rms_pair, mask_full, MODE_ZEROING);
  simd_inst::vsts_norm(out_mul_grad_pair, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 6144)])), 0, mask_full);
  auto rms_grad_even = simd_inst::vcadd(grad_mul, first_token_mask, MODE_ZEROING);
  auto rms_grad_odd = simd_inst::vcadd(grad_mul, second_token_mask, MODE_ZEROING);
  auto denom_even = simd_inst::vadds(sq_even, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto denom_odd = simd_inst::vadds(sq_odd, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto sq_grad_even = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_even, rms_even, mask_full, MODE_ZEROING), denom_even, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  auto sq_grad_odd = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_odd, rms_odd, mask_full, MODE_ZEROING), denom_odd, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  simd_inst::vsts_1st(sq_grad_even, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9216)])), 0, mask_lane0);
  simd_inst::vsts_1st(sq_grad_odd, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9224)])), 0, mask_lane0);
  auto grad_pair_1 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 64)])), 0);
  auto mul_pair_1 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 3136)])), 0);
  auto sq_even_1 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10370)])), 0);
  auto sq_odd_1 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10371)])), 0);
  auto rms_even_1 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_even_1, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_odd_1 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_odd_1, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_pair_1 = simd_inst::vsel(rms_even_1, rms_odd_1, mask_first_token);
  auto grad_mul_1 = simd_inst::vmul(grad_pair_1, mul_pair_1, mask_full, MODE_ZEROING);
  auto out_mul_grad_pair_1 = simd_inst::vmul(grad_pair_1, rms_pair_1, mask_full, MODE_ZEROING);
  simd_inst::vsts_norm(out_mul_grad_pair_1, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 6208)])), 0, mask_full);
  auto rms_grad_even_1 = simd_inst::vcadd(grad_mul_1, first_token_mask, MODE_ZEROING);
  auto rms_grad_odd_1 = simd_inst::vcadd(grad_mul_1, second_token_mask, MODE_ZEROING);
  auto denom_even_1 = simd_inst::vadds(sq_even_1, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto denom_odd_1 = simd_inst::vadds(sq_odd_1, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto sq_grad_even_1 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_even_1, rms_even_1, mask_full, MODE_ZEROING), denom_even_1, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  auto sq_grad_odd_1 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_odd_1, rms_odd_1, mask_full, MODE_ZEROING), denom_odd_1, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  simd_inst::vsts_1st(sq_grad_even_1, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9232)])), 0, mask_lane0);
  simd_inst::vsts_1st(sq_grad_odd_1, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9240)])), 0, mask_lane0);
  auto grad_pair_2 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 128)])), 0);
  auto mul_pair_2 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 3200)])), 0);
  auto sq_even_2 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10372)])), 0);
  auto sq_odd_2 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10373)])), 0);
  auto rms_even_2 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_even_2, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_odd_2 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_odd_2, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_pair_2 = simd_inst::vsel(rms_even_2, rms_odd_2, mask_first_token);
  auto grad_mul_2 = simd_inst::vmul(grad_pair_2, mul_pair_2, mask_full, MODE_ZEROING);
  auto out_mul_grad_pair_2 = simd_inst::vmul(grad_pair_2, rms_pair_2, mask_full, MODE_ZEROING);
  simd_inst::vsts_norm(out_mul_grad_pair_2, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 6272)])), 0, mask_full);
  auto rms_grad_even_2 = simd_inst::vcadd(grad_mul_2, first_token_mask, MODE_ZEROING);
  auto rms_grad_odd_2 = simd_inst::vcadd(grad_mul_2, second_token_mask, MODE_ZEROING);
  auto denom_even_2 = simd_inst::vadds(sq_even_2, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto denom_odd_2 = simd_inst::vadds(sq_odd_2, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto sq_grad_even_2 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_even_2, rms_even_2, mask_full, MODE_ZEROING), denom_even_2, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  auto sq_grad_odd_2 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_odd_2, rms_odd_2, mask_full, MODE_ZEROING), denom_odd_2, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  simd_inst::vsts_1st(sq_grad_even_2, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9248)])), 0, mask_lane0);
  simd_inst::vsts_1st(sq_grad_odd_2, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9256)])), 0, mask_lane0);
  auto grad_pair_3 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 192)])), 0);
  auto mul_pair_3 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 3264)])), 0);
  auto sq_even_3 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10374)])), 0);
  auto sq_odd_3 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10375)])), 0);
  auto rms_even_3 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_even_3, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_odd_3 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_odd_3, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_pair_3 = simd_inst::vsel(rms_even_3, rms_odd_3, mask_first_token);
  auto grad_mul_3 = simd_inst::vmul(grad_pair_3, mul_pair_3, mask_full, MODE_ZEROING);
  auto out_mul_grad_pair_3 = simd_inst::vmul(grad_pair_3, rms_pair_3, mask_full, MODE_ZEROING);
  simd_inst::vsts_norm(out_mul_grad_pair_3, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 6336)])), 0, mask_full);
  auto rms_grad_even_3 = simd_inst::vcadd(grad_mul_3, first_token_mask, MODE_ZEROING);
  auto rms_grad_odd_3 = simd_inst::vcadd(grad_mul_3, second_token_mask, MODE_ZEROING);
  auto denom_even_3 = simd_inst::vadds(sq_even_3, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto denom_odd_3 = simd_inst::vadds(sq_odd_3, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto sq_grad_even_3 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_even_3, rms_even_3, mask_full, MODE_ZEROING), denom_even_3, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  auto sq_grad_odd_3 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_odd_3, rms_odd_3, mask_full, MODE_ZEROING), denom_odd_3, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  simd_inst::vsts_1st(sq_grad_even_3, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9264)])), 0, mask_lane0);
  simd_inst::vsts_1st(sq_grad_odd_3, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9272)])), 0, mask_lane0);
  auto grad_pair_4 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 256)])), 0);
  auto mul_pair_4 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 3328)])), 0);
  auto sq_even_4 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10376)])), 0);
  auto sq_odd_4 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10377)])), 0);
  auto rms_even_4 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_even_4, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_odd_4 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_odd_4, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_pair_4 = simd_inst::vsel(rms_even_4, rms_odd_4, mask_first_token);
  auto grad_mul_4 = simd_inst::vmul(grad_pair_4, mul_pair_4, mask_full, MODE_ZEROING);
  auto out_mul_grad_pair_4 = simd_inst::vmul(grad_pair_4, rms_pair_4, mask_full, MODE_ZEROING);
  simd_inst::vsts_norm(out_mul_grad_pair_4, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 6400)])), 0, mask_full);
  auto rms_grad_even_4 = simd_inst::vcadd(grad_mul_4, first_token_mask, MODE_ZEROING);
  auto rms_grad_odd_4 = simd_inst::vcadd(grad_mul_4, second_token_mask, MODE_ZEROING);
  auto denom_even_4 = simd_inst::vadds(sq_even_4, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto denom_odd_4 = simd_inst::vadds(sq_odd_4, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto sq_grad_even_4 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_even_4, rms_even_4, mask_full, MODE_ZEROING), denom_even_4, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  auto sq_grad_odd_4 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_odd_4, rms_odd_4, mask_full, MODE_ZEROING), denom_odd_4, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  simd_inst::vsts_1st(sq_grad_even_4, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9280)])), 0, mask_lane0);
  simd_inst::vsts_1st(sq_grad_odd_4, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9288)])), 0, mask_lane0);
  auto grad_pair_5 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 320)])), 0);
  auto mul_pair_5 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 3392)])), 0);
  auto sq_even_5 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10378)])), 0);
  auto sq_odd_5 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10379)])), 0);
  auto rms_even_5 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_even_5, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_odd_5 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_odd_5, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_pair_5 = simd_inst::vsel(rms_even_5, rms_odd_5, mask_first_token);
  auto grad_mul_5 = simd_inst::vmul(grad_pair_5, mul_pair_5, mask_full, MODE_ZEROING);
  auto out_mul_grad_pair_5 = simd_inst::vmul(grad_pair_5, rms_pair_5, mask_full, MODE_ZEROING);
  simd_inst::vsts_norm(out_mul_grad_pair_5, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 6464)])), 0, mask_full);
  auto rms_grad_even_5 = simd_inst::vcadd(grad_mul_5, first_token_mask, MODE_ZEROING);
  auto rms_grad_odd_5 = simd_inst::vcadd(grad_mul_5, second_token_mask, MODE_ZEROING);
  auto denom_even_5 = simd_inst::vadds(sq_even_5, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto denom_odd_5 = simd_inst::vadds(sq_odd_5, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto sq_grad_even_5 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_even_5, rms_even_5, mask_full, MODE_ZEROING), denom_even_5, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  auto sq_grad_odd_5 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_odd_5, rms_odd_5, mask_full, MODE_ZEROING), denom_odd_5, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  simd_inst::vsts_1st(sq_grad_even_5, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9296)])), 0, mask_lane0);
  simd_inst::vsts_1st(sq_grad_odd_5, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9304)])), 0, mask_lane0);
  auto grad_pair_6 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 384)])), 0);
  auto mul_pair_6 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 3456)])), 0);
  auto sq_even_6 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10380)])), 0);
  auto sq_odd_6 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10381)])), 0);
  auto rms_even_6 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_even_6, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_odd_6 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_odd_6, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_pair_6 = simd_inst::vsel(rms_even_6, rms_odd_6, mask_first_token);
  auto grad_mul_6 = simd_inst::vmul(grad_pair_6, mul_pair_6, mask_full, MODE_ZEROING);
  auto out_mul_grad_pair_6 = simd_inst::vmul(grad_pair_6, rms_pair_6, mask_full, MODE_ZEROING);
  simd_inst::vsts_norm(out_mul_grad_pair_6, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 6528)])), 0, mask_full);
  auto rms_grad_even_6 = simd_inst::vcadd(grad_mul_6, first_token_mask, MODE_ZEROING);
  auto rms_grad_odd_6 = simd_inst::vcadd(grad_mul_6, second_token_mask, MODE_ZEROING);
  auto denom_even_6 = simd_inst::vadds(sq_even_6, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto denom_odd_6 = simd_inst::vadds(sq_odd_6, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto sq_grad_even_6 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_even_6, rms_even_6, mask_full, MODE_ZEROING), denom_even_6, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  auto sq_grad_odd_6 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_odd_6, rms_odd_6, mask_full, MODE_ZEROING), denom_odd_6, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  simd_inst::vsts_1st(sq_grad_even_6, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9312)])), 0, mask_lane0);
  simd_inst::vsts_1st(sq_grad_odd_6, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9320)])), 0, mask_lane0);
  auto grad_pair_7 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 448)])), 0);
  auto mul_pair_7 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 3520)])), 0);
  auto sq_even_7 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10382)])), 0);
  auto sq_odd_7 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10383)])), 0);
  auto rms_even_7 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_even_7, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_odd_7 = simd_inst::vdiv_0ulp_ftz_true(one, simd_inst::vsqrt(simd_inst::vadds(simd_inst::vmul(sq_odd_7, inv_rms_group_size, mask_full, MODE_ZEROING), float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto rms_pair_7 = simd_inst::vsel(rms_even_7, rms_odd_7, mask_first_token);
  auto grad_mul_7 = simd_inst::vmul(grad_pair_7, mul_pair_7, mask_full, MODE_ZEROING);
  auto out_mul_grad_pair_7 = simd_inst::vmul(grad_pair_7, rms_pair_7, mask_full, MODE_ZEROING);
  simd_inst::vsts_norm(out_mul_grad_pair_7, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 6592)])), 0, mask_full);
  auto rms_grad_even_7 = simd_inst::vcadd(grad_mul_7, first_token_mask, MODE_ZEROING);
  auto rms_grad_odd_7 = simd_inst::vcadd(grad_mul_7, second_token_mask, MODE_ZEROING);
  auto denom_even_7 = simd_inst::vadds(sq_even_7, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto denom_odd_7 = simd_inst::vadds(sq_odd_7, float(0x1.4f8b588e368fp-10f/*1.280000e-03*/), mask_full, MODE_ZEROING);
  auto sq_grad_even_7 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_even_7, rms_even_7, mask_full, MODE_ZEROING), denom_even_7, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  auto sq_grad_odd_7 = simd_inst::vmul(simd_inst::vdiv_0ulp_ftz_true(simd_inst::vmul(rms_grad_odd_7, rms_odd_7, mask_full, MODE_ZEROING), denom_odd_7, mask_full, MODE_ZEROING), neg_half, mask_full, MODE_ZEROING);
  simd_inst::vsts_1st(sq_grad_even_7, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9328)])), 0, mask_lane0);
  simd_inst::vsts_1st(sq_grad_odd_7, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9336)])), 0, mask_lane0);
  simd_inst::mem_bar(VST_VLD);
  sq_grad_compact = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), mask_full, MODE_ZEROING);
  auto token_sq_grad = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9216)])), 0);
  auto token_mask = simd_inst::vcmps_eq(lane_idx, 0, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad, sq_grad_compact, token_mask);
  auto token_sq_grad_1 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9224)])), 0);
  auto token_mask_1 = simd_inst::vcmps_eq(lane_idx, 1, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_1, sq_grad_compact, token_mask_1);
  auto token_sq_grad_2 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9232)])), 0);
  auto token_mask_2 = simd_inst::vcmps_eq(lane_idx, 2, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_2, sq_grad_compact, token_mask_2);
  auto token_sq_grad_3 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9240)])), 0);
  auto token_mask_3 = simd_inst::vcmps_eq(lane_idx, 3, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_3, sq_grad_compact, token_mask_3);
  auto token_sq_grad_4 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9248)])), 0);
  auto token_mask_4 = simd_inst::vcmps_eq(lane_idx, 4, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_4, sq_grad_compact, token_mask_4);
  auto token_sq_grad_5 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9256)])), 0);
  auto token_mask_5 = simd_inst::vcmps_eq(lane_idx, 5, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_5, sq_grad_compact, token_mask_5);
  auto token_sq_grad_6 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9264)])), 0);
  auto token_mask_6 = simd_inst::vcmps_eq(lane_idx, 6, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_6, sq_grad_compact, token_mask_6);
  auto token_sq_grad_7 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9272)])), 0);
  auto token_mask_7 = simd_inst::vcmps_eq(lane_idx, 7, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_7, sq_grad_compact, token_mask_7);
  auto token_sq_grad_8 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9280)])), 0);
  auto token_mask_8 = simd_inst::vcmps_eq(lane_idx, 8, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_8, sq_grad_compact, token_mask_8);
  auto token_sq_grad_9 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9288)])), 0);
  auto token_mask_9 = simd_inst::vcmps_eq(lane_idx, 9, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_9, sq_grad_compact, token_mask_9);
  auto token_sq_grad_10 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9296)])), 0);
  auto token_mask_10 = simd_inst::vcmps_eq(lane_idx, 10, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_10, sq_grad_compact, token_mask_10);
  auto token_sq_grad_11 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9304)])), 0);
  auto token_mask_11 = simd_inst::vcmps_eq(lane_idx, 11, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_11, sq_grad_compact, token_mask_11);
  auto token_sq_grad_12 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9312)])), 0);
  auto token_mask_12 = simd_inst::vcmps_eq(lane_idx, 12, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_12, sq_grad_compact, token_mask_12);
  auto token_sq_grad_13 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9320)])), 0);
  auto token_mask_13 = simd_inst::vcmps_eq(lane_idx, 13, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_13, sq_grad_compact, token_mask_13);
  auto token_sq_grad_14 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9328)])), 0);
  auto token_mask_14 = simd_inst::vcmps_eq(lane_idx, 14, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_14, sq_grad_compact, token_mask_14);
  auto token_sq_grad_15 = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 128) + ((out_grad_ub_version_counter_1 % 6) * 128)) + 9336)])), 0);
  auto token_mask_15 = simd_inst::vcmps_eq(lane_idx, 15, mask_full);
  sq_grad_compact = simd_inst::vsel(token_sq_grad_15, sq_grad_compact, token_mask_15);
  simd_inst::vsts_norm(sq_grad_compact, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 64) + ((out_grad_ub_version_counter_1 % 6) * 64)) + 9984)])), 0, mask_full);
}

__simt_vf__ __launch_bounds__(32) inline void mhc_reduce_partials_and_rmsnorm_bwd_asc_kernel_simt_vf_0(__gm__ float* sqrsum, int32_t w, int32_t token_offset, __gm__ float* out_mul_grad, __gm__ float* out_grad, __gm__ float* out_mul, __gm__ float* sqrsum_grad) {
  float sqrsum_frag[1];
  float rms_grad_reducer[1];
  float rms_grad_frag[1];
  sqrsum_frag[0] = sqrsum[(((((int64_t)w) * (int64_t)896) + (((int64_t)((int32_t)block_idx)) * (int64_t)16)) + ((int64_t)token_offset))];
  float rms = (float(0x1p+0f/*1.000000e+00*/) / sqrtf(((sqrsum_frag[0] * float(0x1.999999999999ap-11f/*7.812500e-04*/)) + float(0x1.0c6f7a0b5ed8dp-20f/*1.000000e-06*/))));
  rms_grad_reducer[0] = float(0x0p+0f/*0.000000e+00*/);
  if (((int32_t)threadIdx.x) < 24) {
    out_mul_grad[((((((int64_t)w) * (int64_t)21504) + (((int64_t)((int32_t)block_idx)) * (int64_t)384)) + (((int64_t)token_offset) * (int64_t)24)) + ((int64_t)((int32_t)threadIdx.x)))] = (out_grad[((((((int64_t)w) * (int64_t)21504) + (((int64_t)((int32_t)block_idx)) * (int64_t)384)) + (((int64_t)token_offset) * (int64_t)24)) + ((int64_t)((int32_t)threadIdx.x)))] * rms);
    rms_grad_reducer[0] = (rms_grad_reducer[0] + (out_grad[((((((int64_t)w) * (int64_t)21504) + (((int64_t)((int32_t)block_idx)) * (int64_t)384)) + (((int64_t)token_offset) * (int64_t)24)) + ((int64_t)((int32_t)threadIdx.x)))] * out_mul[((((((int64_t)w) * (int64_t)21504) + (((int64_t)((int32_t)block_idx)) * (int64_t)384)) + (((int64_t)token_offset) * (int64_t)24)) + ((int64_t)((int32_t)threadIdx.x)))]));
  }
  rms_grad_reducer[0] = tl::AscendAllReduce<tl::SumOp, 32, 1, 0>::run(rms_grad_reducer[0]);
  rms_grad_frag[0] = rms_grad_reducer[0];
  if (((int32_t)threadIdx.x) == 0) {
    sqrsum_grad[(((((int64_t)w) * (int64_t)896) + (((int64_t)((int32_t)block_idx)) * (int64_t)16)) + ((int64_t)token_offset))] = (((rms_grad_frag[0] * rms) / (sqrsum_frag[0] + float(0x1.4f8b588e368fp-10f/*1.280000e-03*/))) / float(-0x1p+1f/*-2.000000e+00*/));
  }
}

extern "C" __global__ __vector__ void mhc_reduce_partials_and_rmsnorm_bwd_asc_kernel(__gm__ float* out_grad, __gm__ float* out_mul, __gm__ float* out_mul_grad, __gm__ float* sqrsum, __gm__ float* sqrsum_grad, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t out_grad_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(4));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(5));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(4));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(5));
  out_grad_ub_version_counter_1 = 0;
  for (int32_t w = 0; w < ((num_tokens + 895) / 896); ++w) {
    int8_t __cond_1 = ((int8_t)(bool)0);
    if (((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) {
      __cond_1 = ((int8_t)((((w * 896) + (((int32_t)block_idx) * 16)) + 16) <= num_tokens));
    }
    if ((((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) && ((bool)__cond_1)) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) + (out_grad_ub_version_counter_1 % 6))));
    }
    if (((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) {
      if ((bool)__cond_1) {
        asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512))]))), (__gm__ uint8_t*)((&(out_grad[((((int64_t)w) * (int64_t)21504) + (((int64_t)((int32_t)block_idx)) * (int64_t)384))]))), 16, 96, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 96, 128);
      }
      if ((bool)__cond_1) {
        asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 3072)]))), (__gm__ uint8_t*)((&(out_mul[((((int64_t)w) * (int64_t)21504) + (((int64_t)((int32_t)block_idx)) * (int64_t)384))]))), 16, 96, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 96, 128);
      }
      if ((bool)__cond_1) {
        asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 16) + ((out_grad_ub_version_counter_1 % 6) * 16)) + 10368)]))), (__gm__ uint8_t*)((&(sqrsum[((((int64_t)w) * (int64_t)896) + (((int64_t)((int32_t)block_idx)) * (int64_t)16))]))), 1, 64, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 64, 64);
      }
    }
    if ((((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) && ((bool)__cond_1)) {
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) + (out_grad_ub_version_counter_1 % 6))));
    }
    if ((((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) && ((bool)__cond_1)) {
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) + (out_grad_ub_version_counter_1 % 6))));
    }
    if ((((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) && ((bool)__cond_1)) {
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) + (out_grad_ub_version_counter_1 % 6))));
    }
    if (((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) {
      if ((bool)__cond_1) {
        mhc_reduce_partials_and_rmsnorm_bwd_asc_kernel_simd_vf_0(buf_dyn_shmem, out_grad_ub_version_counter_1);
      }
    }
    if ((((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) && ((bool)__cond_1)) {
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) + (out_grad_ub_version_counter_1 % 6))));
    }
    if ((((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) && ((bool)__cond_1)) {
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) + (out_grad_ub_version_counter_1 % 6))));
    }
    if (((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) {
      if (!((bool)__cond_1)) {
        for (int32_t token_offset = 0; token_offset < 16; ++token_offset) {
          if ((((w * 896) + (((int32_t)block_idx) * 16)) + token_offset) < num_tokens) {
            asc_vf_call<mhc_reduce_partials_and_rmsnorm_bwd_asc_kernel_simt_vf_0>(cce::dim3(32), sqrsum, w, token_offset, out_mul_grad, out_grad, out_mul, sqrsum_grad);
          }
        }
      }
    }
    if ((((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) && ((bool)__cond_1)) {
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) + (out_grad_ub_version_counter_1 % 6))));
    }
    if (((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) {
      if ((bool)__cond_1) {
        asc_copy_ub2gm_align((__gm__ uint8_t*)((&(out_mul_grad[((((int64_t)w) * (int64_t)21504) + (((int64_t)((int32_t)block_idx)) * (int64_t)384))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 512) + ((out_grad_ub_version_counter_1 % 6) * 512)) + 6144)]))), 16, 96, static_cast<asc_store_l2_cache_mode>(4), 96, 128);
      }
      if ((bool)__cond_1) {
        asc_copy_ub2gm_align((__gm__ uint8_t*)((&(sqrsum_grad[((((int64_t)w) * (int64_t)896) + (((int64_t)((int32_t)block_idx)) * (int64_t)16))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) * 64) + ((out_grad_ub_version_counter_1 % 6) * 64)) + 9984)]))), 1, 64, static_cast<asc_store_l2_cache_mode>(4), 64, 64);
      }
    }
    if ((((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) && ((bool)__cond_1)) {
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(((6 & ((out_grad_ub_version_counter_1 % 6) >> 31)) + (out_grad_ub_version_counter_1 % 6))));
    }
    if ((((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 15) >> 4)) && ((bool)__cond_1)) {
      out_grad_ub_version_counter_1 = (out_grad_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(4));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(5));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(4));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(5));
}

