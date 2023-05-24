import os
FILE = "daemon.c"
CONFIG_PATH = os.path.expanduser('~/.axolotl_config')
SERVER_IP = ''
SERVER_PORT = ''
HOST_ID = False
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        data = f.read().split()
    SERVER_IP = data[0]
    SERVER_PORT = data[1]
    if len(data) == 3:
        HOST_ID = int(data[2])

else:
    SERVER_IP = '172.19.17.236'
    SERVER_PORT = '5000'
    with open(CONFIG_PATH, 'w') as f:
        f.write(SERVER_IP + ' ' + SERVER_PORT)

SIGNALS = [1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]

