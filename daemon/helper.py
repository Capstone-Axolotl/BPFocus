from config import SERVER_IP, SERVER_PORT, SIGNALS
import requests
import json
import threading
import docker
import platform
import psutil
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

def get_metadata():
    uname = platform.uname()
    kernel_info = {
        'version': uname.version,
        'os': uname.system,
        'hostname': uname.node,
        'release': uname.release,
        'machine': uname.machine,
    }

    proc_cpu_info = {}
    with open('/proc/cpuinfo', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if ':' in line:
                info = line.split(':')
                key = info[0].strip()
                value = info[1].strip()
                proc_cpu_info[key] = value

    cpu_info = {
        'physical_cores': psutil.cpu_count(logical=False),
        'total_cores': psutil.cpu_count(logical=True),
        'vendor_id': proc_cpu_info['vendor_id'],
        'model_name': proc_cpu_info['model name']
    }

    memory = psutil.virtual_memory()
    net_if_addrs = psutil.net_if_addrs()

    network_info = []
    net_info = {}
    for interface, addresses in net_if_addrs.items():
        net_info[interface] = []
        for address in addresses:
            net_info[interface].append({
                'family': address.family.name,
                'address': address.address,
                'netmask': address.netmask,
                'broadcast': address.broadcast
            })

    for interface, addresses in net_info.items():
        interface_info = {
            'name': interface,
            'address': addresses[0]['address'],
            'netmask': addresses[0]['netmask']
        }
        if addresses[0]['family'] == 'AF_INET6':
            interface_info['address'] = addresses[0]['address'][:-len(interface) - 1]
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
                    'percent': disk_usage.percent
                })

    metadata = {
        'system_metadata': {
            'uptime': psutil.boot_time(),
            'kernel': kernel_info, 
            'cpu': cpu_info,
            'memory': {
                'total': memory.total,
            },
            'network': network_info,
            'disk': disk_info
        }
    }
    return metadata
