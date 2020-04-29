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

PSUList = [1, 2, None]
PSU = PSUList[0]

params_lock = Lock()
values_lock = Lock()
PSU_lock = Lock()

class DataRandomizer(Thread):
    def __init__(self, conn):
        Thread.__init__(self)
        self.KILL = False
        self.conn = conn
        self.SYSTEM_FAILURE = False
    
    def sysfail(self):
        return self.SYSTEM_FAILURE
    
    def stop(self):
        self.KILL = True

    def run(self):
        global params
        global params_lock
        global values
        global values_lock
        global PSUList
        global PSU_lock

        var = .00001

        while not self.KILL:
            local_thresh = 0
            with params_lock:
                local_thresh = params['THRESH']
                local_v = params['VOLTAGE']
                local_a = params['CURRENT']
                local_f = params['FREQ']

            calc_v = local_v * random.uniform(1 - local_thresh - var, 1 + local_thresh + var)
            calc_a = local_a * random.uniform(1 - local_thresh - var, 1 + local_thresh + var)
            calc_f = local_f * random.uniform(1 - local_thresh - var, 1 + local_thresh + var)

            with values_lock:
                values['VOLTAGE'] = calc_v
                values['CURRENT'] = calc_a
                values['FREQ'] = calc_f
            
            psu_flag = False
            if (calc_v < local_v * (1 - local_thresh) or calc_v > local_v * (1 + local_thresh)):
                # Breach of voltage
                print(f"Breach of voltage detected: {calc_v}! Cfg: {local_v} +/- {local_thresh}")
                psu_flag = True
            elif (calc_a < local_a * (1 - local_thresh) or calc_a > local_a * (1 + local_thresh)):
                # Breach of current
                print(f"Breach of current detected: {calc_a}! Cfg: {local_a} +/- {local_thresh}")
                psu_flag = True
            elif (calc_f < local_f * (1 - local_thresh) or calc_f > local_f * (1 + local_thresh)):
                # Breach of frequency
                print(f"Breach of frequency detected: {calc_f}! Cfg: {local_f} +/- {local_thresh}")
                psu_flag = True
            
            if psu_flag:
                self.conn.sendall(bytes(f'alert {PSUList[0]} {PSUList[1]}', 'utf-8'))
                with PSU_lock:
                    PSUList.remove(PSUList[0])
            
            with PSU_lock:
                if PSUList[0] == None:
                    self.SYSTEM_FAILURE = True
                    break


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

            if self.KILL:
                break

            with values_lock:
                str_msg = f"poll {values['VOLTAGE']} {values['CURRENT']} {values['FREQ']}"
            
            print(str_msg)
            msg = bytes(str_msg, 'utf-8')
            try:
                self.conn.sendall(msg)
            except BrokenPipeError:
                continue

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

# Give me test information
print('=== PARAMS ===')
print('voltage', params['VOLTAGE'])
print('current', params['CURRENT'])
print('freq', params['FREQ'])
print('thresh', params['THRESH'])
print('period', params['PERIOD'])

# Spawn the threads for watching data, making data, listening for server requests, and polling
random.seed(time.time())
data_thread = DataRandomizer(s)
data_thread.start()
polling_thread = PollingThread(s, params['PERIOD'])
polling_thread.start()

s.settimeout(.5)
while True:
    try:
        if data_thread.sysfail():
            print("[-] Stopping all processes")
            s.sendall(bytes('exit', encoding='utf-8'))
            break

        raw_data = s.recv(BUF_SIZE)
        args = str(raw_data, 'utf-8').split(' ')
        if args[0] == 'exit':
            print("[-] Stopping all processes")
            break
        elif args[0] == 'addPower':
            new_psu = int(args[1])
            if new_psu not in PSUList:
                PSUList.insert(-1, int(args[1]))
        elif args[0] == 'delPower':
            try:
                old_psu = int(args[1])
                with PSU_lock:
                    PSUList.remove(old_psu)
            except ValueError:
                continue
        elif args[0] == 'listPower':
            with PSU_lock:
                s.sendall(bytes('listPower ' +', '.join([str(x) for x in PSUList[:-1]]), 'utf-8'))
        elif args[0] == 'changeParam':
            newVolt = float(args[1])
            newCurr = float(args[2])
            newFreq = float(args[3])
            newThresh = float(args[4])
            newPeriod = float(args[5])

            with params_lock:
                if newVolt > 0:
                    params['VOLTAGE'] = newVolt
                if newCurr > 0:
                    params['CURRENT'] = newCurr
                if newFreq > 0:
                    params['FREQ'] = newFreq
                if newThresh > 0:
                    params['THRESH'] = newThresh
                if newPeriod > 0:
                    params['PERIOD'] = newPeriod
        else:
            continue
    except socket.timeout:
        continue
    except KeyboardInterrupt:
        print("[-] Stopping all processes")
        s.sendall(bytes('exit', encoding='utf-8'))
        break

data_thread.stop()
data_thread.join()
polling_thread.stop()
polling_thread.join()
s.close()