#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void mhc_sinkhorn_fwd_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem, int32_t comb_in_ub_version_counter_1) {
  vector_f32 cur;
  vector_bool mask_full = asc_create_mask_b32(PAT_ALL);
  auto idx = simd_inst::vci<int32_t>(0, INC_ORDER);
  auto const_7 = simd_inst::vdup<int32_t>(7, mask_full, MODE_ZEROING);
  auto mod8 = simd_inst::vand(idx, const_7, mask_full, MODE_ZEROING);
  auto mask_lo = simd_inst::vcmps_lt(mod8, 4, mask_full);
  auto mask_hi = simd_inst::vcmps_ge(mod8, 4, mask_full);
  auto const_15 = simd_inst::vdup<int32_t>(15, mask_full, MODE_ZEROING);
  auto token2 = simd_inst::vshls(simd_inst::vshrs(idx, 4, mask_full, MODE_ZEROING), 1, mask_full, MODE_ZEROING);
  auto local = simd_inst::vand(idx, const_15, mask_full, MODE_ZEROING);
  auto local_div8 = simd_inst::vshrs(local, 3, mask_full, MODE_ZEROING);
  auto bcast_idx2 = simd_inst::vadd(token2, local_div8, mask_full, MODE_ZEROING);
  auto token_base_tidx = simd_inst::vshls(simd_inst::vshrs(idx, 4, mask_full, MODE_ZEROING), 4, mask_full, MODE_ZEROING);
  auto col = simd_inst::vand(idx, simd_inst::vdup<int32_t>(3, mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto col4 = simd_inst::vshls(col, 2, mask_full, MODE_ZEROING);
  auto t_idx = simd_inst::vadd(simd_inst::vadd(token_base_tidx, col4, mask_full, MODE_ZEROING), simd_inst::vshrs(local, 2, mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
  auto mat_0 = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((comb_in_ub_version_counter_1 & 3) * 64)])), 0);
      vector_f32 v_ = simd_inst::vcgmax(mat_0, mask_lo, MODE_ZEROING);
    vector_u32 v__1 = simd_inst::vselr((*(vector_u32 *)(&(v_))), (*(vector_u32 *)(&(bcast_idx2))));
      vector_f32 v__2 = simd_inst::vcgmax(mat_0, mask_hi, MODE_ZEROING);
    vector_u32 v__3 = simd_inst::vselr((*(vector_u32 *)(&(v__2))), (*(vector_u32 *)(&(bcast_idx2))));
  auto rmax_b_0 = simd_inst::vsel((*(vector_f32 *)(&(v__1))), (*(vector_f32 *)(&(v__3))), mask_lo);
  auto mat_1 = simd_inst::vexpdif(mat_0, rmax_b_0, mask_full);
      vector_f32 v__4 = simd_inst::vcgadd(mat_1, mask_lo, MODE_ZEROING);
    vector_u32 v__5 = simd_inst::vselr((*(vector_u32 *)(&(v__4))), (*(vector_u32 *)(&(bcast_idx2))));
      vector_f32 v__6 = simd_inst::vcgadd(mat_1, mask_hi, MODE_ZEROING);
    vector_u32 v__7 = simd_inst::vselr((*(vector_u32 *)(&(v__6))), (*(vector_u32 *)(&(bcast_idx2))));
  auto rsum_b_0 = simd_inst::vsel((*(vector_f32 *)(&(v__5))), (*(vector_f32 *)(&(v__7))), mask_lo);
  auto mat_2 = simd_inst::vdiv_0ulp_ftz_true(mat_1, rsum_b_0, mask_full, MODE_ZEROING);
  auto mat_3 = simd_inst::vadds(mat_2, float(0x1.5798ee2308c3ap-27f/*1.000000e-08*/), mask_full, MODE_ZEROING);
    vector_u32 v__8 = simd_inst::vselr((*(vector_u32 *)(&(mat_3))), (*(vector_u32 *)(&(t_idx))));
  auto tr_0 = (*(vector_f32 *)(&(v__8)));
      vector_f32 v__9 = simd_inst::vcgadd(tr_0, mask_lo, MODE_ZEROING);
    vector_u32 v__10 = simd_inst::vselr((*(vector_u32 *)(&(v__9))), (*(vector_u32 *)(&(bcast_idx2))));
      vector_f32 v__11 = simd_inst::vcgadd(tr_0, mask_hi, MODE_ZEROING);
    vector_u32 v__12 = simd_inst::vselr((*(vector_u32 *)(&(v__11))), (*(vector_u32 *)(&(bcast_idx2))));
  auto csum_b_0 = simd_inst::vsel((*(vector_f32 *)(&(v__10))), (*(vector_f32 *)(&(v__12))), mask_lo);
  auto tr_1 = simd_inst::vdiv_0ulp_ftz_true(tr_0, simd_inst::vadds(csum_b_0, float(0x1.5798ee2308c3ap-27f/*1.000000e-08*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
    vector_u32 v__13 = simd_inst::vselr((*(vector_u32 *)(&(tr_1))), (*(vector_u32 *)(&(t_idx))));
  auto mat_4 = (*(vector_f32 *)(&(v__13)));
  cur = mat_4;
  for (int32_t _step = 0; _step < 19; ++_step) {
        vector_f32 v__14 = simd_inst::vcgadd(cur, mask_lo, MODE_ZEROING);
      vector_u32 v__15 = simd_inst::vselr((*(vector_u32 *)(&(v__14))), (*(vector_u32 *)(&(bcast_idx2))));
        vector_f32 v__16 = simd_inst::vcgadd(cur, mask_hi, MODE_ZEROING);
      vector_u32 v__17 = simd_inst::vselr((*(vector_u32 *)(&(v__16))), (*(vector_u32 *)(&(bcast_idx2))));
    auto rsum_b = simd_inst::vsel((*(vector_f32 *)(&(v__15))), (*(vector_f32 *)(&(v__17))), mask_lo);
    cur = simd_inst::vdiv_0ulp_ftz_true(cur, simd_inst::vadds(rsum_b, float(0x1.5798ee2308c3ap-27f/*1.000000e-08*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
      vector_u32 v__18 = simd_inst::vselr((*(vector_u32 *)(&(cur))), (*(vector_u32 *)(&(t_idx))));
    auto tr = (*(vector_f32 *)(&(v__18)));
        vector_f32 v__19 = simd_inst::vcgadd(tr, mask_lo, MODE_ZEROING);
      vector_u32 v__20 = simd_inst::vselr((*(vector_u32 *)(&(v__19))), (*(vector_u32 *)(&(bcast_idx2))));
        vector_f32 v__21 = simd_inst::vcgadd(tr, mask_hi, MODE_ZEROING);
      vector_u32 v__22 = simd_inst::vselr((*(vector_u32 *)(&(v__21))), (*(vector_u32 *)(&(bcast_idx2))));
    auto csum_b = simd_inst::vsel((*(vector_f32 *)(&(v__20))), (*(vector_f32 *)(&(v__22))), mask_lo);
    auto tr_2 = simd_inst::vdiv_0ulp_ftz_true(tr, simd_inst::vadds(csum_b, float(0x1.5798ee2308c3ap-27f/*1.000000e-08*/), mask_full, MODE_ZEROING), mask_full, MODE_ZEROING);
      vector_u32 v__23 = simd_inst::vselr((*(vector_u32 *)(&(tr_2))), (*(vector_u32 *)(&(t_idx))));
    cur = (*(vector_f32 *)(&(v__23)));
  }
  simd_inst::vsts_norm(cur, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[(((comb_in_ub_version_counter_1 & 3) * 64) + 256)])), 0, mask_full);
}

extern "C" __global__ __vector__ void mhc_sinkhorn_fwd_asc_kernel(__gm__ float* comb_res_mix, __gm__ float* comb_res_mix_out, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t comb_in_ub_version_counter_1 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
  comb_in_ub_version_counter_1 = 0;
  for (int32_t w = 0; w < ((((((((((num_tokens + 3) >> 2) - 1) / max(1, min(8, ((num_tokens + 3) >> 2)))) + (((((num_tokens + 3) >> 2) - 1) % max(1, min(8, ((num_tokens + 3) >> 2)))) >> 31)) + 1) * max(1, min(8, ((num_tokens + 3) >> 2)))) + 55) / 56) + ((((((((((num_tokens + 3) >> 2) - 1) / max(1, min(8, ((num_tokens + 3) >> 2)))) + (((((num_tokens + 3) >> 2) - 1) % max(1, min(8, ((num_tokens + 3) >> 2)))) >> 31)) + 1) * max(1, min(8, ((num_tokens + 3) >> 2)))) + 55) % 56) >> 31)); ++w) {
    if ((((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 3) >> 2)))) * max(1, min(8, ((num_tokens + 3) >> 2)))) + (((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 3) >> 2))))) < ((num_tokens + 3) >> 2)) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>((comb_in_ub_version_counter_1 & 3)));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((comb_in_ub_version_counter_1 & 3) * 64)]))), (__gm__ uint8_t*)((&(comb_res_mix[((((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)3) >> (int64_t)2)))) * max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)3) >> (int64_t)2)))) * (int64_t)64) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)3) >> (int64_t)2)))) * (int64_t)64))]))), 1, (min(4, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 3) >> 2)))) * max(1, min(8, ((num_tokens + 3) >> 2)))) * 4)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 3) >> 2)))) * 4)), 0)) * 64), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(4, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 3) >> 2)))) * max(1, min(8, ((num_tokens + 3) >> 2)))) * 4)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 3) >> 2)))) * 4)), 0)) * 64), (min(4, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 3) >> 2)))) * max(1, min(8, ((num_tokens + 3) >> 2)))) * 4)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 3) >> 2)))) * 4)), 0)) * 64));
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>((comb_in_ub_version_counter_1 & 3)));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>((comb_in_ub_version_counter_1 & 3)));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>((comb_in_ub_version_counter_1 & 3)));
      mhc_sinkhorn_fwd_asc_kernel_simd_vf_0(buf_dyn_shmem, comb_in_ub_version_counter_1);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>((comb_in_ub_version_counter_1 & 3)));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>((comb_in_ub_version_counter_1 & 3)));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>((comb_in_ub_version_counter_1 & 3)));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(comb_res_mix_out[((((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) / max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)3) >> (int64_t)2)))) * max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)3) >> (int64_t)2)))) * (int64_t)64) + ((((((int64_t)w) * (int64_t)56) + ((int64_t)((int32_t)block_idx))) % max((int64_t)1, min((int64_t)8, ((((int64_t)num_tokens) + (int64_t)3) >> (int64_t)2)))) * (int64_t)64))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[(((comb_in_ub_version_counter_1 & 3) * 64) + 256)]))), 1, (min(4, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 3) >> 2)))) * max(1, min(8, ((num_tokens + 3) >> 2)))) * 4)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 3) >> 2)))) * 4)), 0)) * 64), static_cast<asc_store_l2_cache_mode>(4), (min(4, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 3) >> 2)))) * max(1, min(8, ((num_tokens + 3) >> 2)))) * 4)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 3) >> 2)))) * 4)), 0)) * 64), (min(4, max(((num_tokens - (((((w * 56) + ((int32_t)block_idx)) / max(1, min(8, ((num_tokens + 3) >> 2)))) * max(1, min(8, ((num_tokens + 3) >> 2)))) * 4)) - ((((w * 56) + ((int32_t)block_idx)) % max(1, min(8, ((num_tokens + 3) >> 2)))) * 4)), 0)) * 64));
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>((comb_in_ub_version_counter_1 & 3)));
      comb_in_ub_version_counter_1 = (comb_in_ub_version_counter_1 + 1);
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
}

