#!/usr/bin/python3
import random
import socket
import time
import sys
import threading
import struct

# Parameters Check
if len(sys.argv) != 4:
    sys.stderr.write("Incorrect usage:\n./tclient.py <DEVICE> <IP> <PORT>\n")
    sys.exit(-1)

DEVICE = sys.argv[1]
HOST = sys.argv[2]
PORT = int(sys.argv[3])
BUF_SIZE = 1024

print(DEVICE)
print(HOST)
print(PORT)

#Connect to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Get initial params
data_raw = s.recv(BUF_SIZE)
data = struct.unpack('!ddddd',data_raw)
VOLTAGE = data[0]
AMPERAGE = data[1]
FREQ = data[2]
THRESHOLD = data[3]
PERIOD = data[4]

s.close()
#Send Device Info
data = s.recv(BUF_SIZE)
random.seed(time.time())
while(True):
    print(random.random())
    time.sleep(period)
