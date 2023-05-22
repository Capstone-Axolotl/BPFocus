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
myid = 13
'''
print("Send Metadata to Aggregator Server... ")
myid = post_host_metadata('/insert_hw', get_metadata())
print(f"[*] Get ID from Aggregator Server : {myid}")

# trace until Ctrl-C
print("Docker Tracing Start...")
get_running_containers()
thread = threading.Thread(target=monitor_container_events)
thread.start()
'''

# Register Signal Handler
for sig in SIGNALS:
    signal.signal(sig, handle_exit)

print("Tracing Start...")
try:
    sleep(1)
    '''
    data_container = {
        'container_init': []
    }
    for id in ids:
        data_container['container_init'].append({id: ids[id]})
    postData('/', data_container)
    '''

    while True:
        sleep(0.5)
        mymap = b.get_table("mymap")
        v = mymap.values()
        current_time = datetime.datetime.now()
        physical_iosize = v[0].physical_iosize
        logical_iosize = v[1].logical_iosize
        network_traffic = v[2].network_traffic
        mymap.clear()

        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent

        print(f"[+] 현재 시각: {current_time}")
        print(f"[*] CPU Percent: {cpu_percent}")
        print(f"[*] Memory Percent: {memory_percent}")
        print(f"[*] Network Traffic : {network_traffic}")
        print(f"[*] Logical I/O : {logical_iosize}")
        print(f"[*] Physical I/O : {physical_iosize}")
        print()
        data_performance = {
            'id': myid,
            'cpu_usg': cpu_percent,
            'mem_usg': memory_percent,
            'disk_io': physical_iosize,
            'vfs_io': logical_iosize,
            'network': network_traffic
        }
        
        postData('/insert_perform', data_performance)
        
        '''
        for id in ids:
            if ids[id]['status'] != 'running':
                continue
            system_cpu_usage = int(read(HOST_CPU_PATH + 'cpuacct.usage'))
            container_stat_path = ids[id]['stat']['paths']
            prev_usages = ids[id]['stat']['prev_usages']
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
            blkio_read_usage = int(io_service_bytes_recursive[0].split()[2])
            blkio_write_usage = int(io_service_bytes_recursive[1].split()[2])
            
            # Network
            netns_stat_path = container_stat_path['network']
            net_input_bytes = int(read(netns_stat_path + 'rx_bytes'))
            net_output_bytes = int(read(netns_stat_path + 'tx_bytes'))

            print(f"[=] Container Id : {id}")
            data_performance = {
                'container_performance': {}
            }
            if prev_total_cpu_usage != 0:
                cpu_delta = total_cpu_usage - prev_total_cpu_usage
                system_cpu_delta = system_cpu_usage - prev_system_cpu_usage
                cpu_percent = round((cpu_delta / system_cpu_delta) * NUMBER_OF_CPUS * 100, 2)
                print(f"[*] cpu_delta : {cpu_delta}")
                print(f"[*] system_cpu_delta : {system_cpu_delta}")
                print(f"[*] CPU percent : {cpu_percent}%")
                data_performance['container_performance']['cpu'] = cpu_percent
            
            # print(f"[*] memory_usage : {memory_usage / 1024 ** 2}")
            # print(used_memory / 1024 ** 2)
            print(f"[*] Memory percent : {memory_percent}%")
            data_performance['container_performance']['memory'] = memory_percent

            if prev_total_disk_usage != 0:
                disk_usage = blkio_total_usage - prev_total_disk_usage
                print(f"[*] Disk Usage : {disk_usage}")
                data_performance['container_performance']['disk_io'] = disk_usage

            if prev_total_network_output_usage != 0 or prev_total_network_input_usage != 0:
                network_input_usage = net_output_bytes - prev_total_network_output_usage
                network_output_usage = net_input_bytes - prev_total_network_input_usage
                print(f"[*] Network Input Usage : {network_input_usage}B")
                print(f"[*] Network Output Usage : {network_output_usage}B")
                data_performance['container_performance']['network_input'] = network_input_usage
                data_performance['container_performance']['network_output'] = network_output_usage
                
            print()
        
            postData('/', data_performance)
            prev_usages['system_cpu_usage'] = system_cpu_usage
            prev_usages['total_cpu_usage'] = total_cpu_usage
            prev_usages['total_disk_usage'] = blkio_total_usage
            prev_usages['total_network_input_usage'] = net_output_bytes
            prev_usages['total_network_output_usage'] = net_input_bytes 
        '''

except KeyboardInterrupt:
    data_down = {
        'exception': 'KeyboardInterrupt' # 정상 종료
    }
    postData('/', data_down)
