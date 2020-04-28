#!/usr/bin/python3

import socket
import time
import random
import sys
import struct

HOST = "10.10.1.2"
PORT = 20202
BUF_SIZE = 1024

def get_data():
    v = float(input("Input Voltage: "))
    a = float(input("Input Amperage: "))
    f = float(input("Input Frequency: "))
    t = float(input("Input Threshold: "))
    p = float(input("Input Period: "))
    return(struct.pack("!ddddd", v, a, f, t, p))


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

cmd = str(input("Continue? Type 'exit' to quit: "))
#while not msg.startswith('exit'):
while not cmd.startswith('exit'):
    msg = get_data()
    #s.sendall(bytes(msg, encoding='utf-8'))
    s.sendall(msg)
    data = s.recv(BUF_SIZE)
    decoded = str(data, encoding='utf-8')
    if decoded.startswith('exit'):
        print("[-] Exiting now...")
        s.close()
        sys.exit(1)
    else:
        print("[+] Received data", str(data, encoding='utf-8'))
    cmd = str(input("Continue? Type 'exit' to quit: "))
    
s.sendall(bytes("exit", encoding='utf-8'))
s.close()
