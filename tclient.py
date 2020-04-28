#!/usr/bin/python3

import socket
import time
import random
import sys
import struct

HOST = "10.10.1.2"
PORT = 20202
BUF_SIZE = 1024

CLIENT_NAME = 'TestMachine'



params = {
    'VOLTAGE': -1,
    'CURRENT': -1,
    'FREQ': -1,
    'THRESH': -1,
    'PERIOD': -1
}

values = {
    'VOLTAGE': -1,
    'CURRENT': -1,
    'FREQ': -1,
    'THRESH': -1,
    'PERIOD': -1
}

#msg = input(">> ")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

"""
while not msg.startswith('exit'):
    s.sendall(bytes(msg, encoding='utf-8'))
    data = s.recv(BUF_SIZE)
    decoded = str(data, encoding='utf-8')
    if decoded.startswith('exit'):
        print("[-] Exiting now...")
        s.close()
        sys.exit(1)
    else:
        print("[+] Received data", str(data, encoding='utf-8'))
        msg = input(">> ")
    
s.sendall(bytes("exit", encoding='utf-8'))
s.close()
"""

# Send Notice Me Senpai Message :3
s.sendall(bytes('alive' + ' ' + CLIENT_NAME, encoding='utf-8'))
print("[+] Sent join request to server")

# Get params back from server, should lock here until it's given..
recv_data = s.recv(BUF_SIZE)
params_raw = struct.unpack('!ddddd', recv_data)
params['VOLTAGE'] = params_raw[0]
params['CURRENT'] = params_raw[1]
params['FREQ'] = params_raw[2]
params['THRESH'] = params_raw[3]
params['PERIOD'] = params_raw[4]
print("[+] Received param information from server, starting normal op")

# Spawn the threads for watching data, making data, listening for server requests, and polling
"""
data_thread = DataRandomizer()
polling_thread = PollingThread(params['PERIOD'])
"""

# Give me test information
print('=== PARAMS ===')
print('voltage', params['VOLTAGE'])
print('current', params['CURRENT'])
print('freq', params['FREQ'])
print('thresh', params['THRESH'])
print('period', params['PERIOD'])

s.sendall(bytes('exit', encoding='utf-8'))
print("[-] Sent quit request")