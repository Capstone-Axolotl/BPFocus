#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
#include <linux/sched.h>

typedef struct entry_key {
    u32 pid;
    u32 cpu;
} entry_key_t;

BPF_HASH(start, entry_key_t, u64, MAX_PID);
BPF_ARRAY(mymap, u64, 4);
static inline void store_start(u32 tgid, u32 pid, u32 cpu, u64 ts)
{
    if (pid == 0)
        return;
    entry_key_t entry_key = { .pid = pid, .cpu = (pid == 0 ? cpu : 0xFFFFFFFF) };
    start.update(&entry_key, &ts);
}

static inline void update_hist(u32 tgid, u32 pid, u32 cpu, u64 ts)
{
    if (pid == 0)
        return;

    entry_key_t entry_key = { .pid = pid, .cpu = (pid == 0 ? cpu : 0xFFFFFFFF) };
    u64 *tsp = start.lookup(&entry_key);
    if (tsp == 0)
        return;

    if (ts < *tsp) {
        // Probably a clock issue where the recorded on-CPU event had a
        // timestamp later than the recorded off-CPU event, or vice versa.
        return;
    }
    u64 delta = ts - *tsp;
    delta /= 1000;

    u32 key = 3;
    u64 *val = mymap.lookup(&key);
    if (val) {
        lock_xadd(val, delta);
    }
}

int sched_switch(struct pt_regs *ctx, struct task_struct *prev)
{
    u64 ts = bpf_ktime_get_ns();
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 tgid = pid_tgid >> 32, pid = pid_tgid;
    u32 cpu = bpf_get_smp_processor_id();

    u32 prev_pid = prev->pid;
    u32 prev_tgid = prev->tgid;
    update_hist(prev_tgid, prev_pid, cpu, ts);
    store_start(tgid, pid, cpu, ts);
    return 0;
}

// 1. Disk I/O
TRACEPOINT_PROBE(block, block_rq_issue)
{
    u32 key = 0;
    u64 *val = mymap.lookup(&key);
    if (val) {
        lock_xadd(val, args->bytes / 1024);
    }
    return 0;
}

// 2. VFS I/O
BPF_ARRAY(myfile, struct file *, MAX_PID);
int vfs_count_entry(struct pt_regs *ctx)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 tid = pid_tgid;
    struct file *fp = (struct file *)PT_REGS_PARM1(ctx);
    myfile.update(&tid, &fp);
    return 0;
}

int vfs_count_exit(struct pt_regs *ctx)
{
    s64 ret = PT_REGS_RC(ctx);
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 tid = pid_tgid;
    struct file **fpp = myfile.lookup(&tid);
    if (fpp == NULL)
        return 0;
    
    struct file *fp = *fpp;
    if (ret >= 0) {
        u32 key = 1;
        u64 *val = mymap.lookup(&key);
        if (val) {
            lock_xadd(val, ret / 1024);
        }
    }
    myfile.delete(&tid);
    return 0;
}

// 3. Network Traffic
TRACEPOINT_PROBE(net, napi_gro_receive_entry)
{
    u32 key = 2;
    u64 *val = mymap.lookup(&key);
    if (val) {
        lock_xadd(val, args->len);
    }
    return 0;
}

TRACEPOINT_PROBE(net, net_dev_xmit)
{
    u32 key = 2;
    u64 *val = mymap.lookup(&key);
    if (val) {
        lock_xadd(val, args->len);
    }
    return 0;
}
