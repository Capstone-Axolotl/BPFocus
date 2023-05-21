#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

struct data_t {
    u64 physical_iosize;
    u64 logical_iosize;
    u64 network_traffic;
};

// 1. Disk I/O
BPF_ARRAY(mymap, struct data_t, 3);
TRACEPOINT_PROBE(block, block_rq_issue)
{
    struct data_t *datap, data = {0, };
    u32 key = 0;
    datap = mymap.lookup(&key);
    if (datap != NULL) {
        data = *datap;
    }
    data.physical_iosize += (args->bytes / 1024);
    mymap.update(&key, &data);
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
        struct data_t *datap, data = {0, };
        u32 key = 1;
        datap = mymap.lookup(&key);
        if (datap != NULL) {
            data = *datap;
        }
        data.logical_iosize += (ret / 1024);
        mymap.update(&key, &data);
    }
    myfile.delete(&tid);
    return 0;
}

// 3. Network Traffic
TRACEPOINT_PROBE(net, napi_gro_receive_entry)
{
    struct data_t *datap, data = {0, };
    u32 key = 2;
    datap = mymap.lookup(&key);
    if (datap != NULL) {
        data = *datap;
    }
    data.network_traffic += args->len;
    mymap.update(&key, &data);
    return 0;
}

TRACEPOINT_PROBE(net, net_dev_xmit)
{
    struct data_t *datap, data = {0, };
    u32 key = 2;
    datap = mymap.lookup(&key);
    if (datap != NULL) {
        data = *datap;
    }
    data.network_traffic += args->len;
    mymap.update(&key, &data);
    return 0;
}