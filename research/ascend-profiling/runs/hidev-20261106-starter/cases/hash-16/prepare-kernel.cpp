#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
__simt_vf__ __launch_bounds__(128) inline void engram_hash_kernel_asc_kernel_simt_vf_0(int32_t num_tokens, int32_t w, __ubuf__ uint8_t* buf_dyn_shmem) {
  int64_t hash_local = (int64_t)0;
  if (((int32_t)threadIdx.x) < ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) {
    if ((bool)((__ubuf__ int8_t*)buf_dyn_shmem)[(((int32_t)threadIdx.x) + 18176)]) {
      #pragma unroll
      for (int32_t layer_idx = 0; layer_idx < 2; ++layer_idx) {
        #pragma unroll
        for (int32_t col = 0; col < 16; ++col) {
          ((__ubuf__ int32_t*)buf_dyn_shmem)[(((layer_idx * 2048) + (((int32_t)threadIdx.x) * 16)) + col)] = -1;
        }
      }
    } else {
      #pragma unroll
      for (int32_t layer_idx_1 = 0; layer_idx_1 < 2; ++layer_idx_1) {
        hash_local = (int64_t)0;
        #pragma unroll
        for (int32_t ngram_idx = 0; ngram_idx < 3; ++ngram_idx) {
          hash_local = (hash_local ^ (((int64_t)((__ubuf__ int32_t*)buf_dyn_shmem)[(((((int32_t)threadIdx.x) * 3) + ngram_idx) + 4096)]) * ((__ubuf__ int64_t*)buf_dyn_shmem)[(((layer_idx_1 * 3) + ngram_idx) + 2288)]));
          if (0 < ngram_idx) {
            #pragma unroll
            for (int32_t table_idx = 0; table_idx < 8; ++table_idx) {
              int64_t rmod = (hash_local % ((int64_t)((__ubuf__ int32_t*)buf_dyn_shmem)[((((layer_idx_1 * 16) + (ngram_idx * 8)) + table_idx) + 4472)]));
              ((__ubuf__ int32_t*)buf_dyn_shmem)[(((((layer_idx_1 * 2048) + (((int32_t)threadIdx.x) * 16)) + (ngram_idx * 8)) + table_idx) - 8)] = ((int32_t)((((((int64_t)0 <= ((int64_t)((__ubuf__ int32_t*)buf_dyn_shmem)[((((layer_idx_1 * 16) + (ngram_idx * 8)) + table_idx) + 4472)])) && ((int64_t)0 <= rmod)) || ((((int64_t)((__ubuf__ int32_t*)buf_dyn_shmem)[((((layer_idx_1 * 16) + (ngram_idx * 8)) + table_idx) + 4472)]) < (int64_t)0) && (rmod <= (int64_t)0))) ? rmod : (rmod + ((int64_t)((__ubuf__ int32_t*)buf_dyn_shmem)[((((layer_idx_1 * 16) + (ngram_idx * 8)) + table_idx) + 4472)]))) + ((int64_t)((__ubuf__ int32_t*)buf_dyn_shmem)[((((layer_idx_1 * 16) + (ngram_idx * 8)) + table_idx) + 4504)])));
            }
          }
        }
      }
    }
  }
}

extern "C" __global__ __vector__ void engram_hash_kernel_asc_kernel(__gm__ int8_t* image_token_mask, __gm__ int64_t* multipliers, __gm__ int32_t* ngram_token_ids, __gm__ int32_t* offsets, __gm__ int32_t* output, __gm__ int32_t* vocab_sizes, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ int64_t*)buf_dyn_shmem)[2288]))), (__gm__ uint8_t*)((&(multipliers[0]))), 1, 48, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 48, 48);
  asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ int32_t*)buf_dyn_shmem)[4480]))), (__gm__ uint8_t*)((&(vocab_sizes[0]))), 1, 128, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 128, 128);
  asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ int32_t*)buf_dyn_shmem)[4512]))), (__gm__ uint8_t*)((&(offsets[0]))), 1, 128, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 128, 128);
  asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(1));
  for (int32_t w = 0; w < ((num_tokens + 7167) / 7168); ++w) {
    if (((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 127) >> 7)) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ int32_t*)buf_dyn_shmem)[4096]))), (__gm__ uint8_t*)((&(ngram_token_ids[((((int64_t)w) * (int64_t)21504) + (((int64_t)((int32_t)block_idx)) * (int64_t)384))]))), 1, (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 12), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 12), (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 12));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ bool*)buf_dyn_shmem)[18176]))), (__gm__ uint8_t*)((&(((__gm__ bool*)image_token_mask)[((((int64_t)w) * (int64_t)7168) + (((int64_t)((int32_t)block_idx)) * (int64_t)128))]))), 1, min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))), min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))));
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(0));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(0));
      asc_vf_call<engram_hash_kernel_asc_kernel_simt_vf_0>(cce::dim3(128), num_tokens, w, buf_dyn_shmem);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(0));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(0));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(output[((((int64_t)w) * (int64_t)114688) + (((int64_t)((int32_t)block_idx)) * (int64_t)2048))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ int32_t*)buf_dyn_shmem)[0]))), 2, (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 64), static_cast<asc_store_l2_cache_mode>(4), (num_tokens * 64), 8192);
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
}

