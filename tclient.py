#!/usr/bin/python3

import socket

HOST = "10.10.1.2"
PORT = 20202
BUF_SIZE = 1024

msg = input(">> ")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while not msg.startswith('exit'):
    s.sendall(msg)
    data = s.recv(BUF_SIZE)
    print("[+] Received data", data)
    msg = input(">> ")

s.close()