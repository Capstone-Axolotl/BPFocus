from config import SERVER_IP, SERVER_PORT, SIGNALS
from pyroute2 import IPRoute, NetNS
import requests
import json
import threading
import docker
import platform
import psutil

def read(path):
    with open(path) as f:
        return f.read()

def readlines(path):
    with open(path) as f:
        return [c.rstrip('\n') for c in f.readlines()]

def post_host_metadata(path='/', data=None) -> None:
    myid = -1

    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(data)
    url = 'http://' + SERVER_IP + ':' + str(SERVER_PORT) + path
    try:
        response = requests.post(url, headers=headers, data=json_data)
        if response.status_code == 200:
            print('Data sent successfully')
            myid = int(response.text)
        else:
            print('Failed to send data')
    except requests.exceptions.ConnectionError:
        print('[*] Aggregator Server is down')

    return myid

def postData(path='/', data=None) -> None:
    """
    Send json format data to server
    """
    global ID

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
            print(response.text)
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
client = docker.from_env()
def monitor_container_events():
    global ids
    containers = client.containers.list()
    for cnt in containers:
        ids[cnt.id]['name'] = cnt.name
        ids[cnt.id]['image'] = cnt.image.tags[0]
        
    events = client.events(decode=True)
    for event in events:
        if 'status' in event and 'id' in event:
            container_id = event['id']
            status = event['status']
            attr = event['Actor']['Attributes']
            if status == 'start':
                ids[container_id]['name'] = attr['name']
                ids[container_id]['image'] = attr['image']
                ids[container_id]['status'] = status
                for container in client.containers.list():
                    if container_id == container.id:
                        pid = container.attrs['State']['Pid']
                        with NetNS(f"/proc/{pid}/ns/net") as ns:
                            links = ns.get_links()
                            for link in links:
                                if link.get_attr('IFLA_IFNAME') == 'eth0':
                                    index = link.get_attr('IFLA_LINK')
                                    veth = ip.get_links(index)[0]
                                    cpu_stat_path = f"/sys/fs/cgroup/cpu,cpuacct/docker/{container_id}/"
                                    memory_stat_path = f"/sys/fs/cgroup/memory/docker/{container_id}/"
                                    netns_stat_path = f"/sys/class/net/{veth.get_attr('IFLA_IFNAME')}/statistics/"
                                    disk_stat_path = f"/sys/fs/cgroup/blkio/docker/{container_id}/"
                                    container_stat = {
                                        'id': container_id,
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
                                    ids[container_id]['stat'] = container_stat

                print(f"[+] Container Started: {container_id}")
                data_container = {
                    'container': {
                        'status': 'running',
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
                ids[container_id]['status'] = status

HOST_CPU_PATH = "/sys/fs/cgroup/cpu,cpuacct/"
output_string = read(HOST_CPU_PATH + 'cpuacct.usage_percpu')
output_list = [int(x) for x in output_string.split()]
NUMBER_OF_CPUS = sum(1 for x in output_list if x != 0)
MEMORY_LIMIT = psutil.virtual_memory().total
def get_running_containers():
    ip = IPRoute()
    for container in client.containers.list():
        container_id = container.id
        print(f"[*] container id : {container_id}")
        pid = container.attrs['State']['Pid']
        with NetNS(f"/proc/{pid}/ns/net") as ns:
            links = ns.get_links()
            for link in links:
                if link.get_attr('IFLA_IFNAME') == 'eth0':
                    index = link.get_attr('IFLA_LINK')
                    veth = ip.get_links(index)[0]
                    cpu_stat_path = f"/sys/fs/cgroup/cpu,cpuacct/docker/{container_id}/"
                    memory_stat_path = f"/sys/fs/cgroup/memory/docker/{container_id}/"
                    netns_stat_path = f"/sys/class/net/{veth.get_attr('IFLA_IFNAME')}/statistics/"
                    disk_stat_path = f"/sys/fs/cgroup/blkio/docker/{container_id}/"
                    container_stat = {
                        'id': container_id,
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
                    ids[container_id] = {
                        'name': container.name,
                        'image': container.image.tags[0],
                        'status': container.status
                    }
                    # print(ids[container_id])
                    data_container = {
                        'container': {
                            'status': 'running',
                            'id': container_id,
                            'information': ids[container_id]
                        }
                    }
                    ids[container_id]['stat'] = container_stat
                    postData('/', data_container)

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
            'disk_info': disk_info
    }
    
    return metadata
