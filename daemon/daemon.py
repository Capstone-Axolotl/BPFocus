#!/usr/bin/env python3
from bcc import BPF
from time import sleep, strftime
from config import *
from helper import *
import datetime
import psutil
import threading
import signal

# Load BPF program
max_pid = int(open("/proc/sys/kernel/pid_max").read())
b = BPF(src_file=FILE, cflags=["-DMAX_PID=%d" % max_pid])

print("Tracing Start...")
# CPU on-time Instrumentation
b.attach_kprobe(event_re="^finish_task_switch$|^finish_task_switch\.isra\.\d$", fn_name="sched_switch")

# Virtual File System Read/Write Instrumentation
b.attach_kprobe(event="vfs_read", fn_name="vfs_count_entry")
b.attach_kprobe(event="vfs_readv", fn_name="vfs_count_entry")
b.attach_kprobe(event="vfs_write", fn_name="vfs_count_entry")
b.attach_kprobe(event="vfs_writev", fn_name="vfs_count_entry")

b.attach_kretprobe(event="vfs_read", fn_name="vfs_count_exit")
b.attach_kretprobe(event="vfs_readv", fn_name="vfs_count_exit")
b.attach_kretprobe(event="vfs_write", fn_name="vfs_count_exit")
b.attach_kretprobe(event="vfs_writev", fn_name="vfs_count_exit")

# Send Metadata (Initialize done)
if HOST_ID:
    host_id = int(HOST_ID)
else:
    print("Send Metadata to Aggregator Server... ")
    host_id = post_data_sync('/insert_hw', get_metadata())
    with open(CONFIG_PATH, 'r') as f:
        data = f.read().split()

    with open(CONFIG_PATH, 'w') as f:
        f.write(f"{data[0]} {data[1]} {host_id}")

print(f"[*] ID: {host_id}")
post_data_async('/update_health', {}, host_id)

# trace until Ctrl-C
print("Docker Tracing Start...")
get_running_containers(host_id)
thread = threading.Thread(target=monitor_container_events, args=[host_id])
thread.start()

# Register Signal Handler
for sig in SIGNALS:
    signal.signal(sig, handle_exit)

print("Tracing Start...")
try:
    while True:
        sleep(0.5)
        mymap = b.get_table("mymap")
        v = mymap.values()
        current_time = datetime.datetime.now()
        physical_iosize = v[0].value
        logical_iosize = v[1].value
        network_traffic = v[2].value
        cpu_ontime = v[3].value
        mymap.clear()

        memory_percent = psutil.virtual_memory().percent
        print(f"[+] 현재 시각: {current_time}")
        if DEBUG:
            print(f"[*] CPU On-Time: {cpu_ontime}")
            print(f"[*] Memory Percent: {memory_percent}")
            print(f"[*] Network Traffic : {network_traffic}")
            print(f"[*] Logical I/O : {logical_iosize}")
            print(f"[*] Physical I/O : {physical_iosize}")
            print()
        data_performance = {
            'cpu_usg': cpu_ontime,
            'mem_usg': memory_percent,
            'disk_io': physical_iosize,
            'vfs_io': logical_iosize,
            'network': network_traffic
        }
        post_data_async('/insert_perform', data_performance, host_id)

        for cid in ids:
            if ids[cid]['status'] != 'running':
                continue

            system_cpu_usage = get_system_cpu_usage()
            container_stat_path = ids[cid]['stat']['paths']
            prev_usages = ids[cid]['stat']['prev_usages']
            prev_system_cpu_usage = prev_usages['system_cpu_usage']
            prev_total_cpu_usage = prev_usages['total_cpu_usage']
            prev_total_disk_usage = prev_usages['total_disk_usage']
            prev_total_network_output_usage = prev_usages['total_network_input_usage']
            prev_total_network_input_usage = prev_usages['total_network_output_usage']

            # CPU (per cpu도 가능)
            total_cpu_usage = int(read(container_stat_path['cpu'] + 'cpuacct.usage'))
            
            # Memory
            memory_usage = int(read(container_stat_path['memory'] + 'memory.usage_in_bytes'))
            memory_cache_usage = int(readlines(container_stat_path['memory'] + 'memory.stat')[0].split()[1])
            used_memory = memory_usage - memory_cache_usage
            memory_percent = round((used_memory / MEMORY_LIMIT) * 100.0, 2)
            

            # Disk (blkio.throttle.io_service_bytes)
            io_service_bytes_recursive = readlines(container_stat_path['disk'] + 'blkio.throttle.io_service_bytes_recursive')
            blkio_total_usage = int(io_service_bytes_recursive[-1].split()[1])
            
            if len(io_service_bytes_recursive[0].split()) == 2: # Total 0
                blkio_total_usage = 0
            else:
                blkio_read_usage = int(io_service_bytes_recursive[0].split()[2])
                blkio_write_usage = int(io_service_bytes_recursive[1].split()[2])
            
            # Network
            netns_stat_path = container_stat_path['network']
            net_input_bytes = int(read(netns_stat_path + 'rx_bytes'))
            net_output_bytes = int(read(netns_stat_path + 'tx_bytes'))

            data_con_performance = {
                'cpu': 0,
                'disk_io': 0,
                'network_input': 0,
                'network_output': 0
            }
            if prev_total_cpu_usage != 0:
                # nanoseconds (10^{-9})
                cpu_delta = (total_cpu_usage - prev_total_cpu_usage) / 1e7

                # HZ (10^{-2})
                system_cpu_delta = system_cpu_usage - prev_system_cpu_usage
                cpu_percent = round((cpu_delta / system_cpu_delta) * 100, 2)
                if DEBUG:
                    print(f"[*] cpu_delta : {cpu_delta}")
                    print(f"[*] system_cpu_delta : {system_cpu_delta}")
                    print(f"[*] CPU percent : {cpu_percent}%")
                data_con_performance['cpu'] = cpu_percent

            if DEBUG:
                print(f"[*] Memory percent : {memory_percent}%")
            data_con_performance['memory'] = memory_percent

            if prev_total_disk_usage != 0:
                disk_usage = blkio_total_usage - prev_total_disk_usage
                if DEBUG:
                    print(f"[*] Disk Usage : {disk_usage}")
                data_con_performance['disk_io'] = disk_usage

            if prev_total_network_output_usage != 0 or prev_total_network_input_usage != 0:
                network_input_usage = net_output_bytes - prev_total_network_output_usage
                network_output_usage = net_input_bytes - prev_total_network_input_usage
                if DEBUG:
                    print(f"[*] Network Input Usage : {network_input_usage}B")
                    print(f"[*] Network Output Usage : {network_output_usage}B")
                data_con_performance['network_input'] = network_input_usage
                data_con_performance['network_output'] = network_output_usage
                
            if DEBUG:
                print()
        
            post_data_async('/insert_container_perform', data_con_performance, host_id, cid)
            prev_usages['system_cpu_usage'] = system_cpu_usage
            prev_usages['total_cpu_usage'] = total_cpu_usage
            prev_usages['total_disk_usage'] = blkio_total_usage
            prev_usages['total_network_input_usage'] = net_output_bytes
            prev_usages['total_network_output_usage'] = net_input_bytes 

except KeyboardInterrupt:
    pass
