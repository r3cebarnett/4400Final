#!/usr/bin/python3

# CLI (Command Line Interface)
# Server to actively monitor connections
# Each client connection

import socket
from threading import Thread
from socketserver import ThreadingMixIn


# Class for handling Clients
class ClientThread(Thread):
    def __init__(self, ip, port, conn):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        print(f"\n[+] Started thread for servicing {self.ip}:{self.port}")
    
    def run(self):
        while True:
            data = self.conn.recv(1024)
            print("Server received", data)
            if str(data).startswith("exit"):
                break
            self.conn.sendall(f"Message Received, {self.ip}:{self.port}")


# Class for handling User IO
class UserInterface(Thread):
    def __init__(self):
        Thread.__init__(self)
        print(f"Welcome to PowerUI v0.0.0.b (Alpha)")

    def run(self):
        while True:
            msg = input(">> ")
            if msg.lower() == "exit":
                break
            else:
                print("[?] Functionality not supported!")


# Main Server Part
HOST = "10.10.1.2"
PORT = "20202"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))

uiThread = UserInterface()
uiThread.start()

clientThreads = []

while True:
    s.listen(4)
    (conn, (ip, port)) = s.accept()
    newconn = ClientThread(ip, port, conn)
    newconn.start()
    clientThreads.append(newconn)

uiThread.join()
for i in clientThreads:
    i.join()