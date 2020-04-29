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
    
    def sendCommand(self, cmd):
        self.conn.sendall(cmd)
    
    def stop(self):
        self.KILL = True
    
    def run(self):
        global threadList

        self.conn.settimeout(.5) # Half second timeout

        while True:
            try:
                data = self.conn.recv(1024)
                decoded = str(data, encoding='utf-8')
                print("\n[*] Server received {", decoded, "}")
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
                    #print(f"\n[*] Received poll from {self.name}")
                    self.values['VOLTAGE'] = float(args[1])
                    self.values['CURRENT'] = float(args[2])
                    self.values['THRESH'] = float(args[3])

                elif args[0].startswith('alert'):
                    print(f"\n[!] Breach detected on {self.name}, switching from {args[1]} to {args[2]}")

                elif args[0].startswith('listPower'):
                    print(f"Power devices from {self.name}: {args[1:]}")

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
    args = input(">> ").split(' ')
    if args[0] == "exit":
        print("[-] Exiting Program")

        listener.stop()
        listener.join()

        break
    elif args[0] == "status":
        if args[1] == "all":
            for index, i in zip(threadList, range(len(threadList))):
                print(f"[{index}] {i.name} - {i.values['VOLTAGE']}/{i.values['CURRENT']}/{i.values['FREQ']}")
        else:
            try:
                index = int(args[1])
                i = threadList[index]
                print(f"[{index}] {i.name} - {i.values['VOLTAGE']}/{i.values['CURRENT']}/{i.values['FREQ']}")
            except:
                print(f"Error selecting index {i}")

    elif args[0] == "addPower":
        try:
            psu = int(args[2])
        except:
            print("Invalid PSU")
        
        if args[1] == 'all':
            for i in threadList:
                i.sendCommand(bytes(f'addPower {psu}', 'utf-8'))
        else:
            try:
                index = int(args[i])
                threadList[index].sendCommand(bytes(f'addPower {psu}', 'utf-8'))
            except:
                print("Invalid index")
    elif args[0] == "delPower":
        try:
            msg = bytes(f"delPower {int(args[2])}", 'utf-8')
            if args[1] == 'all':
                for i in threadList:
                    i.sendCommand(msg)
            else:
                threadList[int(args[1])].sendCommand(msg)
        except:
            print("Malformed command")
    elif args[0] == "listPower":
        try:
            msg = bytes(f"listPower", 'utf-8')
            if args[1] == 'all':
                for i in threadList:
                    i.sendCommand(msg)
            else:
                threadList[int(args[1])].sendCommand(msg)
        except:
            print("Malformed command")
    elif args[0] == "changeParam":
        try:
            newVolt = float(args[2])
            newCurr = float(args[3])
            newFreq = float(args[4])
            newThresh = float(args[5])
            newPeriod = float(args[6])
            msg = bytes(f"changeParam {newVolt} {newCurr} {newFreq} {newThresh} {newPeriod}")
            if args[1] == 'all':
                for i in threadList:
                    i.sendCommand(msg)
            else:
                threadList[int(args[1])].sendCommand(msg)
    else:
        print("[?] Functionality not supported!")