FILE = "daemon.c"
SERVER_IP = "192.168.65.196"
SERVER_PORT = 8080
SIGNALS = [1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]

def get_metadata():
    import platform, psutil, json
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
