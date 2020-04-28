#!/usr/bin/python3

import socket
import time
import random
import sys
from threading import Thread, Lock

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
    'FREQ': -1
}

params_lock = Lock()
values_lock = Lock()

class DataRandomizer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.KILL = False
    
    def stop(self):
        self.KILL = True

    def run(self):
        global params
        global params_lock
        global values
        global values_lock

        while not self.KILL:
            # Randomize Values, TODO place lock on values and param
            local_thresh = 0
            with params_lock:
                local_thresh = params['THRESH']
            with values_lock:
                values['VOLTAGE'] = values['VOLTAGE'] * random.uniform(1 - local_thresh, 1 + local_thresh)
                values['CURRENT'] = values['CURRENT'] * random.uniform(1 - local_thresh, 1 + local_thresh)
                values['FREQ'] = values['FREQ'] * random.uniform(1 - local_thresh, 1 + local_thresh)


class PollingThread(Thread):
    def __init__(self, conn, period):
        Thread.__init__(self)
        self.period = period
        self.KILL = False
        self.conn = conn
    
    def stop(self):
        self.KILL = True

    def setPeriod(self, period):
        self.period = period
    
    def run(self):
        global values
        global values_lock

        while not self.KILL:
            time.sleep(self.period)
            self.sendPoll()

            with values_lock:
                msg = bytes(f"poll {values['VOLTAGE']} {values['CURRENT']} {values['FREQ']}", 'utf-8')
            
            self.conn.sendall(msg)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Send Notice Me Senpai Message :3
s.sendall(bytes('alive' + ' ' + CLIENT_NAME, encoding='utf-8'))
print("[+] Sent join request to server")

# Get params back from server, should lock here until it's given..
recv_data = s.recv(BUF_SIZE)
data_raw = str(recv_data, 'utf-8')
params_raw = [float(x) for x in data_raw.split(' ')]
params['VOLTAGE'] = params_raw[0]
params['CURRENT'] = params_raw[1]
params['FREQ'] = params_raw[2]
params['THRESH'] = params_raw[3]
params['PERIOD'] = params_raw[4]
print("[+] Received param information from server, starting normal op")

# Spawn the threads for watching data, making data, listening for server requests, and polling
random.seed(time.time())
data_thread = DataRandomizer()
data_thread.run()
#polling_thread = PollingThread(params['PERIOD'])

# Give me test information
print('=== PARAMS ===')
print('voltage', params['VOLTAGE'])
print('current', params['CURRENT'])
print('freq', params['FREQ'])
print('thresh', params['THRESH'])
print('period', params['PERIOD'])

s.sendall(bytes('exit', encoding='utf-8'))
s.close()
print("[-] Sent quit request")