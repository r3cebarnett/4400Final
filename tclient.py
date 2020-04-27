#!/usr/bin/python3

import socket
import time
import random
import sys

HOST = "10.10.1.2"
PORT = 20202
BUF_SIZE = 1024

msg = input(">> ")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

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
