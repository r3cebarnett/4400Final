#!/usr/bin/python3

# CLI (Command Line Interface)
# Server to actively monitor connections
# Each client connection

import sys
import socket
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
        self.alive = False

        self.params = {
            'VOLTAGE': 1,
            'CURRENT': 2,
            'FREQ': 3,
            'THRESH': .1,
            'PERIOD': 5
        }

        self.values = {
            'VOLTAGE': -1,
            'CURRENT': -1,
            'FREQ': -1
        }

        self.name = None

        print(f"\n[+] Started thread for servicing {self.ip}:{self.port}")
    
    def stop(self):
        self.KILL = True
    
    def run(self):
        global threadList

        self.conn.settimeout(.5) # Half second timeout

        while True:
            try:
                data = self.conn.recv(1024)
                decoded = str(data, encoding='utf-8')
                print("\n[*] Server received", decoded)
                args = decoded.split(' ')
                if args[0].startswith('exit'):
                    print(f"\n[-] Stopping thread for servicing {self.ip}:{self.port}")
                    threadList.remove(self)
                    break
                elif args[0].startswith('alive'):
                    self.name = args[1]
                    print(f"\n[+] Received start request {self.ip}:{self.port}, {self.name}")
                    conv_params = [str(x) for x in [self.params['VOLTAGE'],
                                                self.params['CURRENT'], self.params['FREQ'],
                                                self.params['THRESH'], self.params['PERIOD']]]
                    msg = bytes(' '.join(conv_params), 'utf-8')
                    self.conn.sendall(msg)
                elif args[0].startswith('poll'):
                    print(f"\n[*] Received poll from {self.name}")
                    self.values['VOLTAGE'] = float(args[1])
                    self.values['CURRENT'] = float(args[2])
                    self.values['THRESH'] = float(args[3])
                else:
                    self.conn.sendall(bytes(f"Message Received, {self.ip}:{self.port}", encoding='utf-8'))
            except socket.timeout as e:
                if self.KILL:
                    print(f"\n[-] Stopping thread for servicing {self.ip}:{self.port}")
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
                (conn, (ip, port)) = self.s.accept()
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
listener.start()

print(f"Welcome to PowerUI v0.0.0.c (Alpha)")

while True:
    msg = input(">> ")
    if msg.lower() == "exit":
        print("[-] Exiting Program")

        listener.stop()
        listener.join()

        break
    elif msg.lower() == "status":
        for i in threadList:
            print(f"[*] {i.name} - {i.values['VOLTAGE']}/{i.values['CURRENT']}/{i.values['FREQ']}")
    else:
        print("[?] Functionality not supported!")