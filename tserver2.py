#!/usr/bin/python3

# CLI (Command Line Interface)
# Server to actively monitor connections
# Each client connection

import sys
import socket
import struct
from threading import Thread
from socketserver import ThreadingMixIn

threadList = []

# Class for handling Clients
class ClientThread(Thread):
    def __init__(self, ip, port, conn):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        self.KILL = False
        print(f"\n[+] Started thread for servicing {self.ip}:{self.port}")
    
    def stop(self):
        self.KILL = True
    
    def run(self):
        global threadList

        self.conn.settimeout(.5) # Half second timeout

        while True:
            try:
                data = self.conn.recv(1024)
                print("Server received", str(data, encoding='utf-8'))
                if str(data, encoding='utf-8').startswith('exit'):
                    print(f"\n[-] Stopping thread for servicing {self.ip}:{self.port}")
                    threadList.remove(self)
                    break
                self.conn.sendall(bytes(f"Message Received, {self.ip}:{self.port}", encoding='utf-8'))
            except socket.timeout as e:
                if self.KILL:
                    print(f"\n[-] Stopping thread for servicing {self.ip}:{self.port}")
                    self.conn.sendall(bytes(f"Disconnecting from server", encoding='utf-8'))
                    self.conn.sendall(bytes(f"exit", encoding='utf-8'))
                    return
                else:
                    continue


class ClientListener(Thread):
    def __init__(self, HOST, PORT):
        Thread.__init__(self)
        self.HOST = HOST
        self.PORT = PORT
        self.KILL = False
    
    def stop(self):
        self.KILL = True
    
    def run(self):
        global threadList

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, PORT))
        self.s.settimeout(.5)

        while True:
            try:
                self.s.listen()
                (conn, (ip, port)) = s.accept()
                newconn = ClientThread(ip, port, conn)
                newconn.start()
                threadList.append(newconn)
            except socket.timeout as e:
                # Some sort of timeout
                if self.KILL:
                    print(f"\n[-] Stopping thread for listening for clients")
                    for i in threadList:
                        i.stop()
                        i.join()
                    return
                else:
                    continue


## MAIN ##
HOST = "10.10.1.2"
PORT = 20202

listener = ClientListener(HOST, PORT)

print(f"Welcome to PowerUI v0.0.0.c (Alpha)")

while True:
    msg = input(">> ")
    if msg.lower() == "exit":
        print("[-] Exiting Program")

        listener.stop()
        listener.join()

        break
    else:
        print("[?] Functionality not supported!")