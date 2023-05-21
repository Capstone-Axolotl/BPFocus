import os
FILE = "daemon.c"
CONFIG_PATH = os.path.expanduser('~/.axolotl_config')
SERVER_IP = ''
SERVER_PORT = ''
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        SERVER_IP, SERVER_PORT = f.read().split()
else:
    SERVER_IP = input("IP of Aggregator Server: ")
    SERVER_PORT = input("PORT of Aggregator Server: ")
    with open(CONFIG_PATH, 'w') as f:
        f.write(SERVER_IP + ' ' + SERVER_PORT)

SIGNALS = [1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]

