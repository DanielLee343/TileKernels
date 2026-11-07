#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

/* Diagnostic only: host readback changes timing/cache; discard these profiles. */
typedef struct { unsigned index; uintptr_t addr; size_t len; char file[1024]; unsigned char *gold,*buf; long before; int before_rc; } watch;
typedef struct { uintptr_t origin,snapshot; uint64_t size; int policy; } section;
static unsigned watch_call;

/* ABI layout checked against the installed 26.2.0 binary and source; diagnostic only. */
int _ZNK13MemoryContext19RestoreFromSnapshotERKNS_10MemSectionEPv(void *ctx, const section *s, void *stream) {
    typedef int (*fn)(void *,const section *,void *);
    static fn real;
    if (!real) real=(fn)dlsym(RTLD_NEXT,"_ZNK13MemoryContext19RestoreFromSnapshotERKNS_10MemSectionEPv");
    if (!real) {fprintf(stderr,"WATCH missing RestoreFromSnapshot symbol\n");return 0;}
    int result=real(ctx,s,stream);
    const char *cfg=getenv("REPLAY_WATCH_CONFIG"), *log=getenv("REPLAY_WATCH_COVERAGE");
    if (!cfg || !log || !s || !s->origin || !s->snapshot) return result;
    FILE *f=fopen(cfg,"r");if(!f)return result;
    unsigned index;uintptr_t addr;size_t len;char file[1024];FILE *out=NULL;
    while(fscanf(f,"%u %lx %zu %1023s",&index,&addr,&len,file)==4) {
      if(addr>=s->origin && addr-s->origin<=s->size && len<=s->size-(addr-s->origin)) {
        if(!out)out=fopen(log,"a");
        if(out)fprintf(out,"%u %u %lx %lu %lx %d\n",watch_call,index,s->origin,s->size,s->snapshot,result);
      }
    }
    if(out)fclose(out);fclose(f);return result;
}

int _ZN13MemoryContext7RestoreEv(void *ctx) {
    typedef int (*restore_fn)(void *);
    typedef int (*sync_fn)(void);
    typedef int (*copy_fn)(void *, size_t, const void *, size_t, int);
    static restore_fn restore;
    if (!restore) restore=(restore_fn)dlsym(RTLD_NEXT,"_ZN13MemoryContext7RestoreEv");
    if (!restore) { fprintf(stderr,"WATCH missing restore symbol\n"); return 0; }
    const char *cfg=getenv("REPLAY_WATCH_CONFIG"), *log=getenv("REPLAY_WATCH_LOG");
    if (!cfg || !log) return restore(ctx);
    watch items[32]={0}; unsigned n=0;
    FILE *f=fopen(cfg,"r");
    if (f) {
      while (n<32 && fscanf(f,"%u %lx %zu %1023s",&items[n].index,&items[n].addr,&items[n].len,items[n].file)==4) {
        watch *w=&items[n]; w->gold=malloc(w->len);w->buf=malloc(w->len);
        FILE *b=fopen(w->file,"rb");
        if (!w->gold || !w->buf || !b || fread(w->gold,1,w->len,b)!=w->len) { if(b)fclose(b);free(w->gold);free(w->buf);break; }
        fclose(b);n++;
      }
      fclose(f);
    }
    sync_fn sync=(sync_fn)dlsym(RTLD_DEFAULT,"aclrtSynchronizeDevice");
    copy_fn copy=(copy_fn)dlsym(RTLD_DEFAULT,"aclrtMemcpy");
    int sync_before=sync?sync():-999;
    for (unsigned i=0;i<n;i++) {
      watch *w=&items[i];w->before=-1;
      w->before_rc=copy?copy(w->buf,w->len,(void*)w->addr,w->len,2):-999;
      if (!w->before_rc) {w->before=0;for(size_t j=0;j<w->len;j++)w->before+=w->buf[j]!=w->gold[j];}
    }
    int result=restore(ctx), sync_after=sync?sync():-999;
    FILE *out=fopen(log,"a");
    for (unsigned i=0;i<n;i++) {
      watch *w=&items[i];long after=-1;
      int rc=copy?copy(w->buf,w->len,(void*)w->addr,w->len,2):-999;
      if (!rc) {after=0;for(size_t j=0;j<w->len;j++)after+=w->buf[j]!=w->gold[j];}
      if(out)fprintf(out,"%u %u %d %d %d %d %d %zu %ld %ld\n",watch_call,w->index,result,sync_before,w->before_rc,sync_after,rc,w->len,w->before,after);
      free(w->gold);free(w->buf);
    }
    if(out)fclose(out);watch_call++;
    return result;
}
