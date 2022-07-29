"""
    Sample code for Multi-Threaded Server
    Python 3
    Usage: python3 server.py localhost 12000
    coding: utf-8
    
    Author: Joel Huang 
    Starter code sourced from Wei Song
"""
from socket import *
from threading import Thread
import sys, select
import json
import os
from datetime import datetime

# acquire server host and port from command line parameter
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 TCPServer3.py SERVER_PORT NUM_CONSECUTIVE_FAILED_ATTEMPTS ======\n")
    exit(0)
if int(sys.argv[2]) > 5 or int(sys.argv[2]) < 1:
    print("\n===== Error usage: Invalid number of allowed failed consecutive attempt: number. The valid value of argument number is an integer between 1 and 5\n")
    exit(0)
serverHost = "localhost"
serverPort = int(sys.argv[1])
number_of_consecutive_failed_attempts = int(sys.argv[2])
serverAddress = (serverHost, serverPort)

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

# define structure for users and the time they login
clientStatus = {}

"""
    Define multi-thread class for client
    This class would be used to define the instance for each connection from each client
    For example, client-1 makes a connection request to the server, the server will call
    class (ClientThread) to define a thread for client-1, and when client-2 make a connection
    request to the server, the server will call class (ClientThread) again and create a thread
    for client-2. Each client will be runing in a separate therad, which is the multi-threading
"""
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False

        self.blockedSince = datetime.timestamp(datetime.now())
        # clientStatus[clientAddress] = self.blockedSince
        
        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        
    def run(self):
        message = 'Hello'
        
        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(1024)
            # message = data.decode()
            message = json.loads(data.decode('utf-8'))
            
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if message == '':
                self.clientAlive = False
                print("===== the user disconnected - ", clientAddress)
                break
            
            # handle message from the client
            if message['type'] == 'login':
                print("[recv] New login request")
                self.process_login(message)
            elif message['type'] == 'logout':
                print("[recv] Logout requested")
                message = 'logout user'
                print("[send] " + message)
                self.clientAlive = False
                continue
            elif message == 'download':
                print("[recv] Download request")
                message = 'download filename'
                print("[send] " + message)
                self.clientSocket.send(message.encode())
            else:
                print("[recv] " + message)
                print("[send] Cannot understand this message")
                message = 'Cannot understand this message'
                self.clientSocket.send(message.encode())
    
    """
        You can create more customized APIs here, e.g., logic for processing user authentication
        Each api can be used to handle one specific function, for example:
        def process_login(self):
            message = 'user credentials request'
            self.clientSocket.send(message.encode())
    """
    def process_login(self, message):
        credentials = {}
        with open('credentials.txt') as file:
            for user in file.readlines():
                pairs = user.split(' ')
                credentials[pairs[0]] = pairs[1].strip()

        # print(credentials)
        # print(message)

        # Blocking of user
        if 'block' in message and message['block'] == True:
            self.clientAlive = False
            dt = datetime.now()
            ts = datetime.timestamp(dt)
            self.blockedSince = dt
            print(self.blockedSince)
            clientStatus[message['username']] = ts
            print(clientStatus)
            return

        if message['username'] in credentials:
            
            # Logic underneath deals with blocked user first
            dt = datetime.now()
            ts = datetime.timestamp(dt)
            if message['username'] in clientStatus and ts - clientStatus[message['username']] < 10:
                print('logged in b4 10 secoinds cuz')
                message = 'LOCKED USER'
                print(message)
                self.clientAlive = False
                self.clientSocket.send(message.encode())
                return

            if message['password'] == credentials[message['username']]: 
                print("CORRECT Credentials")
                message = 'AUTHENTICATED'
                print(message)
                self.clientSocket.send(message.encode())
                # print(clientStatus)
            else:
                print("INCORRECT Password")
                # message = 'INVALID CREDENTIALS'
                message = str(number_of_consecutive_failed_attempts)
                print(message)
                self.clientSocket.send(message.encode())
        else:
            # print("INCORRECT Credentials")
            # message = 'INVALID CREDENTIALS'
            message = str(number_of_consecutive_failed_attempts)
            print(message)
            self.clientSocket.send(message.encode())

        # message = 'user credentials request'
        # print('[send] ' + message)
        # self.clientSocket.send(message.encode())
    
    def process_logout(self, message):
        message = 'logout requested'
        print('[send] ' + message)
        self.clientAlive = False
        self.clientSocket.send(message.encode())


print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")


while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt)
    clientThread.start()
