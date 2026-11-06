#include <tl_templates/ascend/common.h>
#include <tl_templates/ascend/debug.h>
__simt_vf__ __launch_bounds__(128) inline void engram_hash_kernel_asc_kernel_simt_vf_0(int32_t num_tokens, int32_t w, __ubuf__ uint8_t* buf_dyn_shmem) {
  int64_t hash_local = (int64_t)0;
  if (((int32_t)threadIdx.x) < ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) {
    #pragma unroll
    for (int32_t layer_idx = 0; layer_idx < 2; ++layer_idx) {
      hash_local = (int64_t)0;
      #pragma unroll
      for (int32_t ngram_idx = 0; ngram_idx < 4; ++ngram_idx) {
        hash_local = (hash_local ^ (((int64_t)((__ubuf__ int32_t*)buf_dyn_shmem)[(((((int32_t)threadIdx.x) * 4) + ngram_idx) + 6144)]) * ((__ubuf__ int64_t*)buf_dyn_shmem)[(((layer_idx * 4) + ngram_idx) + 3376)]));
        if (0 < ngram_idx) {
          #pragma unroll
          for (int32_t table_idx = 0; table_idx < 8; ++table_idx) {
            int64_t rmod = (hash_local % ((int64_t)((__ubuf__ int32_t*)buf_dyn_shmem)[((((layer_idx * 24) + (ngram_idx * 8)) + table_idx) + 6648)]));
            ((__ubuf__ int32_t*)buf_dyn_shmem)[(((((layer_idx * 3072) + (((int32_t)threadIdx.x) * 24)) + (ngram_idx * 8)) + table_idx) - 8)] = ((int32_t)((((((int64_t)0 <= ((int64_t)((__ubuf__ int32_t*)buf_dyn_shmem)[((((layer_idx * 24) + (ngram_idx * 8)) + table_idx) + 6648)])) && ((int64_t)0 <= rmod)) || ((((int64_t)((__ubuf__ int32_t*)buf_dyn_shmem)[((((layer_idx * 24) + (ngram_idx * 8)) + table_idx) + 6648)]) < (int64_t)0) && (rmod <= (int64_t)0))) ? rmod : (rmod + ((int64_t)((__ubuf__ int32_t*)buf_dyn_shmem)[((((layer_idx * 24) + (ngram_idx * 8)) + table_idx) + 6648)]))) + ((int64_t)((__ubuf__ int32_t*)buf_dyn_shmem)[((((layer_idx * 24) + (ngram_idx * 8)) + table_idx) + 6696)])));
          }
        }
      }
    }
  }
}

extern "C" __global__ __vector__ void engram_hash_kernel_asc_kernel(__gm__ int64_t* multipliers, __gm__ int32_t* ngram_token_ids, __gm__ int32_t* offsets, __gm__ int32_t* output, __gm__ int32_t* vocab_sizes, int32_t num_tokens) {
  asc_init();
  __ubuf__ uint8_t *buf_dyn_shmem = (__ubuf__ uint8_t *)0;
  asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
  asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ int64_t*)buf_dyn_shmem)[3376]))), (__gm__ uint8_t*)((&(multipliers[0]))), 1, 64, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 64, 64);
  asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ int32_t*)buf_dyn_shmem)[6656]))), (__gm__ uint8_t*)((&(vocab_sizes[0]))), 1, 192, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 192, 192);
  asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ int32_t*)buf_dyn_shmem)[6704]))), (__gm__ uint8_t*)((&(offsets[0]))), 1, 192, 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), 192, 192);
  asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(1));
  asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(1));
  for (int32_t w = 0; w < ((num_tokens + 7167) / 7168); ++w) {
    if (((w * 56) + ((int32_t)block_idx)) < ((num_tokens + 127) >> 7)) {
      asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
      asc_copy_gm2ub_align((__ubuf__ uint8_t*)((&(((__ubuf__ int32_t*)buf_dyn_shmem)[6144]))), (__gm__ uint8_t*)((&(ngram_token_ids[((((int64_t)w) * (int64_t)28672) + (((int64_t)((int32_t)block_idx)) * (int64_t)512))]))), 1, (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 16), 0, 0, 0, static_cast<asc_load_l2_cache_mode>(0), (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 16), (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 16));
      asc_sync_notify(PIPE_MTE2, PIPE_V, static_cast<event_t>(0));
      asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
      asc_sync_wait(PIPE_MTE2, PIPE_V, static_cast<event_t>(0));
      asc_vf_call<engram_hash_kernel_asc_kernel_simt_vf_0>(cce::dim3(128), num_tokens, w, buf_dyn_shmem);
      asc_sync_notify(PIPE_V, PIPE_MTE3, static_cast<event_t>(0));
      asc_sync_notify(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
      asc_sync_wait(PIPE_V, PIPE_MTE3, static_cast<event_t>(0));
      asc_copy_ub2gm_align((__gm__ uint8_t*)((&(output[((((int64_t)w) * (int64_t)172032) + (((int64_t)((int32_t)block_idx)) * (int64_t)3072))]))), (__ubuf__ uint8_t*)((&(((__ubuf__ int32_t*)buf_dyn_shmem)[0]))), 2, (min(128, ((num_tokens - (((int32_t)block_idx) * 128)) - (w * 7168))) * 96), static_cast<asc_store_l2_cache_mode>(4), (num_tokens * 96), 12288);
      asc_sync_notify(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
    }
  }
  asc_sync_wait(PIPE_MTE3, PIPE_V, static_cast<event_t>(0));
  asc_sync_wait(PIPE_V, PIPE_MTE2, static_cast<event_t>(0));
}

