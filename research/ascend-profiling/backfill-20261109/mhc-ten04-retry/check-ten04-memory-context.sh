echo __TEN04_MEMORY_CONTEXT_BEGIN__
free -h;ulimit -l
for f in /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory.current /sys/fs/cgroup/memory.events;do test ! -r "$f" || { echo "$f";cat "$f"; };done
npu-smi info -t proc-mem -i 0 2>&1 | head -n 35
ps -eo pid,ppid,rss,stat,args --sort=-rss | head -n 12 | cut -c1-240
echo __TEN04_MEMORY_CONTEXT_END__
