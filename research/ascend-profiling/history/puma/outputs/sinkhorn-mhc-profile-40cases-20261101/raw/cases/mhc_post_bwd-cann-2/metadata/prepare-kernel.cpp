#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
#include <tl_templates/ascend/simd_inst.h>
__simd_vf__ inline void mhc_post_bwd_asc_kernel_simd_vf_0(__ubuf__ uint8_t* buf_dyn_shmem) {
  vector_bool v = asc_create_mask_b32(PAT_ALL);
  auto zero = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v, MODE_ZEROING);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54784])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54848])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54912])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54976])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53760])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53824])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53888])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53952])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54016])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54080])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54144])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54208])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54272])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54336])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54400])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54464])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54528])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54592])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54656])), 0, v);
  simd_inst::vsts_norm(zero, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54720])), 0, v);
}

__simd_vf__ inline void mhc_post_bwd_asc_kernel_simd_vf_1(__ubuf__ uint8_t* buf_dyn_shmem, int32_t post_layer_mix_ub_version_counter_2, int32_t x_ub_version_counter_1) {
  vector_f32 post_mix[4];
  vector_f32 comb_mix[16];
  vector_f32 d_o_reg[4];
  vector_f32 d_x_reg;
  vector_f32 d_res_reg;
  vector_f32 post_acc_reg;
  vector_f32 d_comb_mix_mi[4];
  post_mix[0] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 8) + ((post_layer_mix_ub_version_counter_2 % 3) * 8)) + 55088)])), 0);
  post_mix[1] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 8) + ((post_layer_mix_ub_version_counter_2 % 3) * 8)) + 55089)])), 0);
  post_mix[2] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 8) + ((post_layer_mix_ub_version_counter_2 % 3) * 8)) + 55090)])), 0);
  post_mix[3] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 8) + ((post_layer_mix_ub_version_counter_2 % 3) * 8)) + 55091)])), 0);
  comb_mix[0] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55040)])), 0);
  comb_mix[1] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55041)])), 0);
  comb_mix[2] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55042)])), 0);
  comb_mix[3] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55043)])), 0);
  comb_mix[4] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55044)])), 0);
  comb_mix[5] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55045)])), 0);
  comb_mix[6] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55046)])), 0);
  comb_mix[7] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55047)])), 0);
  comb_mix[8] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55048)])), 0);
  comb_mix[9] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55049)])), 0);
  comb_mix[10] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55050)])), 0);
  comb_mix[11] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55051)])), 0);
  comb_mix[12] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55052)])), 0);
  comb_mix[13] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55053)])), 0);
  comb_mix[14] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55054)])), 0);
  comb_mix[15] = simd_inst::vlds_brc_elem<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55055)])), 0);
  for (int32_t c = 0; c < 40; ++c) {
    vector_bool v = asc_create_mask_b16(PAT_ALL);
    auto x_f32 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 2560) + ((x_ub_version_counter_1 % 3) * 2560)) + (c * 64)) + 92160)])), 0), v, PART_EVEN, MODE_ZEROING);
    d_o_reg[0] = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + (c * 64))])), 0), v, PART_EVEN, MODE_ZEROING);
    d_o_reg[1] = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 2560)])), 0), v, PART_EVEN, MODE_ZEROING);
    d_o_reg[2] = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 5120)])), 0), v, PART_EVEN, MODE_ZEROING);
    d_o_reg[3] = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 7680)])), 0), v, PART_EVEN, MODE_ZEROING);
    vector_bool v_1 = asc_create_mask_b32(PAT_ALL);
    d_x_reg = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_x_reg)), d_o_reg[0], post_mix[0], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_x_reg)), d_o_reg[1], post_mix[1], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_x_reg)), d_o_reg[2], post_mix[2], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_x_reg)), d_o_reg[3], post_mix[3], v_1, MODE_ZEROING);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(d_x_reg, v, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 2560) + ((x_ub_version_counter_1 % 3) * 2560)) + (c * 64)) + 99840)])), 0, v);
    post_acc_reg = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54784])), 0);
    simd_inst::vmula((&(post_acc_reg)), d_o_reg[0], x_f32, v_1, MODE_ZEROING);
    simd_inst::vsts_norm(post_acc_reg, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54784])), 0, v_1);
    post_acc_reg = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54848])), 0);
    simd_inst::vmula((&(post_acc_reg)), d_o_reg[1], x_f32, v_1, MODE_ZEROING);
    simd_inst::vsts_norm(post_acc_reg, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54848])), 0, v_1);
    post_acc_reg = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54912])), 0);
    simd_inst::vmula((&(post_acc_reg)), d_o_reg[2], x_f32, v_1, MODE_ZEROING);
    simd_inst::vsts_norm(post_acc_reg, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54912])), 0, v_1);
    post_acc_reg = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54976])), 0);
    simd_inst::vmula((&(post_acc_reg)), d_o_reg[3], x_f32, v_1, MODE_ZEROING);
    simd_inst::vsts_norm(post_acc_reg, (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54976])), 0, v_1);
    auto res_mi = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 30720)])), 0), v, PART_EVEN, MODE_ZEROING);
    d_comb_mix_mi[0] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53760])), 0);
    d_comb_mix_mi[1] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53824])), 0);
    d_comb_mix_mi[2] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53888])), 0);
    d_comb_mix_mi[3] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53952])), 0);
    d_res_reg = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[0], comb_mix[0], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[0])), d_o_reg[0], res_mi, v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[1], comb_mix[1], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[1])), d_o_reg[1], res_mi, v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[2], comb_mix[2], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[2])), d_o_reg[2], res_mi, v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[3], comb_mix[3], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[3])), d_o_reg[3], res_mi, v_1, MODE_ZEROING);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(d_res_reg, v, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 61440)])), 0, v);
    simd_inst::vsts_norm(d_comb_mix_mi[0], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53760])), 0, v_1);
    simd_inst::vsts_norm(d_comb_mix_mi[1], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53824])), 0, v_1);
    simd_inst::vsts_norm(d_comb_mix_mi[2], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53888])), 0, v_1);
    simd_inst::vsts_norm(d_comb_mix_mi[3], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53952])), 0, v_1);
    auto res_mi_1 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 33280)])), 0), v, PART_EVEN, MODE_ZEROING);
    d_comb_mix_mi[0] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54016])), 0);
    d_comb_mix_mi[1] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54080])), 0);
    d_comb_mix_mi[2] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54144])), 0);
    d_comb_mix_mi[3] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54208])), 0);
    d_res_reg = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[0], comb_mix[4], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[0])), d_o_reg[0], res_mi_1, v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[1], comb_mix[5], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[1])), d_o_reg[1], res_mi_1, v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[2], comb_mix[6], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[2])), d_o_reg[2], res_mi_1, v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[3], comb_mix[7], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[3])), d_o_reg[3], res_mi_1, v_1, MODE_ZEROING);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(d_res_reg, v, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 64000)])), 0, v);
    simd_inst::vsts_norm(d_comb_mix_mi[0], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54016])), 0, v_1);
    simd_inst::vsts_norm(d_comb_mix_mi[1], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54080])), 0, v_1);
    simd_inst::vsts_norm(d_comb_mix_mi[2], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54144])), 0, v_1);
    simd_inst::vsts_norm(d_comb_mix_mi[3], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54208])), 0, v_1);
    auto res_mi_2 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 35840)])), 0), v, PART_EVEN, MODE_ZEROING);
    d_comb_mix_mi[0] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54272])), 0);
    d_comb_mix_mi[1] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54336])), 0);
    d_comb_mix_mi[2] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54400])), 0);
    d_comb_mix_mi[3] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54464])), 0);
    d_res_reg = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[0], comb_mix[8], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[0])), d_o_reg[0], res_mi_2, v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[1], comb_mix[9], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[1])), d_o_reg[1], res_mi_2, v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[2], comb_mix[10], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[2])), d_o_reg[2], res_mi_2, v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[3], comb_mix[11], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[3])), d_o_reg[3], res_mi_2, v_1, MODE_ZEROING);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(d_res_reg, v, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 66560)])), 0, v);
    simd_inst::vsts_norm(d_comb_mix_mi[0], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54272])), 0, v_1);
    simd_inst::vsts_norm(d_comb_mix_mi[1], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54336])), 0, v_1);
    simd_inst::vsts_norm(d_comb_mix_mi[2], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54400])), 0, v_1);
    simd_inst::vsts_norm(d_comb_mix_mi[3], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54464])), 0, v_1);
    auto res_mi_3 = simd_inst::vcvt<float>(simd_inst::vlds_unpack<bfloat16_t>((__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 38400)])), 0), v, PART_EVEN, MODE_ZEROING);
    d_comb_mix_mi[0] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54528])), 0);
    d_comb_mix_mi[1] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54592])), 0);
    d_comb_mix_mi[2] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54656])), 0);
    d_comb_mix_mi[3] = simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54720])), 0);
    d_res_reg = simd_inst::vdup<float>(float(0x0p+0f/*0.000000e+00*/), v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[0], comb_mix[12], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[0])), d_o_reg[0], res_mi_3, v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[1], comb_mix[13], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[1])), d_o_reg[1], res_mi_3, v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[2], comb_mix[14], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[2])), d_o_reg[2], res_mi_3, v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_res_reg)), d_o_reg[3], comb_mix[15], v_1, MODE_ZEROING);
    simd_inst::vmula((&(d_comb_mix_mi[3])), d_o_reg[3], res_mi_3, v_1, MODE_ZEROING);
    simd_inst::vsts_pack_b32(simd_inst::vcvt<bfloat16_t>(d_res_reg, v, ROUND_R, RS_ENABLE, PART_EVEN, MODE_ZEROING), (__ubuf__ bfloat16_t*)(&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + (c * 64)) + 69120)])), 0, v);
    simd_inst::vsts_norm(d_comb_mix_mi[0], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54528])), 0, v_1);
    simd_inst::vsts_norm(d_comb_mix_mi[1], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54592])), 0, v_1);
    simd_inst::vsts_norm(d_comb_mix_mi[2], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54656])), 0, v_1);
    simd_inst::vsts_norm(d_comb_mix_mi[3], (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54720])), 0, v_1);
  }
}

__simd_vf__ inline void mhc_post_bwd_asc_kernel_simd_vf_2(__ubuf__ uint8_t* buf_dyn_shmem) {
  vector_bool v = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54784])), 0), v, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55128])), 0, v);
  vector_bool v_1 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54848])), 0), v_1, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55129])), 0, v_1);
  vector_bool v_2 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54912])), 0), v_2, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55130])), 0, v_2);
  vector_bool v_3 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54976])), 0), v_3, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55131])), 0, v_3);
  vector_bool v_4 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53760])), 0), v_4, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55112])), 0, v_4);
  vector_bool v_5 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53824])), 0), v_5, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55113])), 0, v_5);
  vector_bool v_6 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53888])), 0), v_6, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55114])), 0, v_6);
  vector_bool v_7 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[53952])), 0), v_7, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55115])), 0, v_7);
  vector_bool v_8 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54016])), 0), v_8, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55116])), 0, v_8);
  vector_bool v_9 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54080])), 0), v_9, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55117])), 0, v_9);
  vector_bool v_10 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54144])), 0), v_10, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55118])), 0, v_10);
  vector_bool v_11 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54208])), 0), v_11, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55119])), 0, v_11);
  vector_bool v_12 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54272])), 0), v_12, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55120])), 0, v_12);
  vector_bool v_13 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54336])), 0), v_13, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55121])), 0, v_13);
  vector_bool v_14 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54400])), 0), v_14, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55122])), 0, v_14);
  vector_bool v_15 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54464])), 0), v_15, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55123])), 0, v_15);
  vector_bool v_16 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54528])), 0), v_16, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55124])), 0, v_16);
  vector_bool v_17 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54592])), 0), v_17, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55125])), 0, v_17);
  vector_bool v_18 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54656])), 0), v_18, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55126])), 0, v_18);
  vector_bool v_19 = asc_create_mask_b32(PAT_ALL);
  simd_inst::vsts_1st(simd_inst::vcadd(simd_inst::vlds_norm<float>((__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[54720])), 0), v_19, MODE_ZEROING), (__ubuf__ float*)(&(((__ubuf__ float*)buf_dyn_shmem)[55127])), 0, v_19);
}

extern "C" __global__ __vector__ void mhc_post_bwd_asc_kernel(__gm__ float* comb_res_mix, __gm__ float* d_comb_res_mix, __gm__ bfloat16_t* d_o, __gm__ float* d_post_layer_mix, __gm__ bfloat16_t* d_residual, __gm__ bfloat16_t* d_x, __gm__ float* post_layer_mix, __gm__ bfloat16_t* residual, __gm__ bfloat16_t* x, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  int32_t x_ub_version_counter_1 = 0;
  int32_t post_layer_mix_ub_version_counter_2 = 0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(4));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(5));
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
  x_ub_version_counter_1 = 0;
  post_layer_mix_ub_version_counter_2 = 0;
  for (int32_t w = 0; w < ((num_tokens + 55) / 56); ++w) {
    if (((w * 56) + ((int32_t)block_idx)) < num_tokens) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) + (post_layer_mix_ub_version_counter_2 % 3)) + 3)));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 16) + ((post_layer_mix_ub_version_counter_2 % 3) * 16)) + 55040)]))), (__gm__ uint8_t*)((&(comb_res_mix[((((int64_t)w) * (int64_t)896) + (((int64_t)((int32_t)block_idx)) * (int64_t)16))]))), 1, 64, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 64, 64);
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) * 8) + ((post_layer_mix_ub_version_counter_2 % 3) * 8)) + 55088)]))), (__gm__ uint8_t*)((&(post_layer_mix[((((int64_t)w) * (int64_t)224) + (((int64_t)((int32_t)block_idx)) * (int64_t)4))]))), 1, 16, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 16, 16);
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) + (post_layer_mix_ub_version_counter_2 % 3)) + 3)));
      mhc_post_bwd_asc_kernel_simd_vf_0(buf_dyn_shmem);
      for (int32_t pid_h = 0; pid_h < 2; ++pid_h) {
        asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
        asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 2560) + ((x_ub_version_counter_1 % 3) * 2560)) + 92160)]))), (__gm__ uint8_t*)((&(x[(((((int64_t)w) * (int64_t)286720) + (((int64_t)((int32_t)block_idx)) * (int64_t)5120)) + (((int64_t)pid_h) * (int64_t)2560))]))), 1, 5120, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 5120, 5120);
        asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[(((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240))]))), (__gm__ uint8_t*)((&(d_o[(((((int64_t)w) * (int64_t)1146880) + (((int64_t)((int32_t)block_idx)) * (int64_t)20480)) + (((int64_t)pid_h) * (int64_t)2560))]))), 4, 5120, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 10240, 5120);
        asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + 30720)]))), (__gm__ uint8_t*)((&(residual[(((((int64_t)w) * (int64_t)1146880) + (((int64_t)((int32_t)block_idx)) * (int64_t)20480)) + (((int64_t)pid_h) * (int64_t)2560))]))), 4, 5120, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 10240, 5120);
        asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
        if (pid_h == 0) {
          asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) + (post_layer_mix_ub_version_counter_2 % 3)) + 3)));
        }
        asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
        asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
        mhc_post_bwd_asc_kernel_simd_vf_1(buf_dyn_shmem, post_layer_mix_ub_version_counter_2, x_ub_version_counter_1);
        asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
        asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
        if (pid_h == 1) {
          asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>((((3 & ((post_layer_mix_ub_version_counter_2 % 3) >> 31)) + (post_layer_mix_ub_version_counter_2 % 3)) + 3)));
        }
        asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
        asc_copy_ub2gm_align((__gm__ uint8_t*)((&(d_x[(((((int64_t)w) * (int64_t)286720) + (((int64_t)((int32_t)block_idx)) * (int64_t)5120)) + (((int64_t)pid_h) * (int64_t)2560))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 2560) + ((x_ub_version_counter_1 % 3) * 2560)) + 99840)]))), 1, 5120, static_cast<asc_store_l2_cache_mode>(4), 5120, 5120);
        asc_copy_ub2gm_align((__gm__ uint8_t*)((&(d_residual[(((((int64_t)w) * (int64_t)1146880) + (((int64_t)((int32_t)block_idx)) * (int64_t)20480)) + (((int64_t)pid_h) * (int64_t)2560))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ bfloat16_t*)buf_dyn_shmem)[((((3 & ((x_ub_version_counter_1 % 3) >> 31)) * 10240) + ((x_ub_version_counter_1 % 3) * 10240)) + 61440)]))), 4, 5120, static_cast<asc_store_l2_cache_mode>(4), 10240, 5120);
        asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(((3 & ((x_ub_version_counter_1 % 3) >> 31)) + (x_ub_version_counter_1 % 3))));
        x_ub_version_counter_1 = (x_ub_version_counter_1 + 1);
      }
      post_layer_mix_ub_version_counter_2 = (post_layer_mix_ub_version_counter_2 + 1);
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
      mhc_post_bwd_asc_kernel_simd_vf_2(buf_dyn_shmem);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(3));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(3));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(d_post_layer_mix[((((int64_t)w) * (int64_t)224) + (((int64_t)((int32_t)block_idx)) * (int64_t)4))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[55128]))), 1, 16, static_cast<asc_store_l2_cache_mode>(4), 16, 16);
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(d_comb_res_mix[((((int64_t)w) * (int64_t)896) + (((int64_t)((int32_t)block_idx)) * (int64_t)16))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ float*)buf_dyn_shmem)[55112]))), 1, 64, static_cast<asc_store_l2_cache_mode>(4), 64, 64);
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(2));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(1));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(2));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(3));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(4));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(5));
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(3));
}

