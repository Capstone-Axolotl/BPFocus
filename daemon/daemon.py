#!/usr/bin/env python3
from bcc import BPF
from time import sleep
from config import FILE, SERVER_IP, SERVER_PORT, SIGNALS, get_metadata
import datetime
import requests
import psutil
import threading
import json
import platform
import signal
import sys
import os
import docker

def postData(path='/', data=None) -> None:
    """
    Send json format data to server
    """
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(data)
    url = 'http://' + SERVER_IP + ':' + str(SERVER_PORT) + path
    def send_request():
        try:
            response = requests.post(url, headers=headers, data=json_data)
            if response.status_code == 200:
                print('Data sent successfully')
            else:
                print('Failed to send data')
        except requests.exceptions.ConnectionError:
            print('[*] Aggregator Server is down')

    thread = threading.Thread(target=send_request)
    thread.start()

def handle_exit(signal, frame):
    """
    Handle signal and send signal number to server
    """
    print(f"시그널 {signal} 수신, 프로그램 종료")
    data_signal = {'exception': {
        'signal': signal
    }}
    postData('/', data_signal)


ids = {}
def monitor_container_events():
    global ids
    client = docker.from_env()
    containers = client.containers.list()
    for cnt in containers:
        ids[cnt.id] = {
            'name': cnt.name,
            'image': cnt.image.tags[0]
        }

    events = client.events(decode=True)
    for event in events:
        if 'status' in event and 'id' in event:
            container_id = event['id']
            status = event['status']
            attr = event['Actor']['Attributes']
            if status == 'start':
                ids[container_id] = {
                    'name': attr['name'],
                    'image': attr['image']
                }
                print(f"[+] Container Started: {container_id}")
                data_container = {
                    'container': {
                        'status': status,
                        'id': container_id,
                        'information': ids[container_id]
                    }
                }
                postData('/', data_container)

            if status == 'die':
                print(f"[-] Container Died: {container_id}")
                data_container = {
                    'container': {
                        'status': status,
                        'id': container_id,
                        'information': ids[container_id]
                    }
                }
                postData('/', data_container)
                del ids[container_id]




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
postData('/', get_metadata())

# Register Signal Handler
for sig in SIGNALS:
    signal.signal(sig, handle_exit)

# trace until Ctrl-C
print("Tracing Start...")
thread = threading.Thread(target=monitor_container_events)
thread.start()
try:
    sleep(1)
    data_container = {
        'container_init': []
    }
    for id in ids:
        data_container['container_init'].append({id: ids[id]})
    postData('/', data_container)
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
            'performance': {
                'cpu': cpu_percent,
                'memory': memory_percent,
                'disk_io': physical_iosize,
                'vfs_io': logical_iosize,
                'network': network_traffic
            }
        }

        postData('/', data_performance)

except KeyboardInterrupt:
    data_down = {
        'exception': 'KeyboardInterrupt' # 정상 종료
    }
    postData('/', data_down)