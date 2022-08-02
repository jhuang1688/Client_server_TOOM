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

import re

# acquire server host and port from command line parameter
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 TCPServer3.py SERVER_PORT NUM_CONSECUTIVE_FAILED_ATTEMPTS ======\n")
    exit(0)
if int(sys.argv[2]) > 5 or int(sys.argv[2]) < 1:
    print("\n===== Error usage: Invalid number of allowed failed consecutive attempt: number. The valid value of argument number is an integer between 1 and 5\n")
    exit(0)
serverHost = "127.0.0.1"
serverPort = int(sys.argv[1])
number_of_consecutive_failed_attempts = int(sys.argv[2])
serverAddress = (serverHost, serverPort)

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

# Clear .txt logs
open('userlog.txt', 'w').close()
open('messagelog.txt', 'w').close()

# define structure for users and the time they login, and messages and their timestamps
global clientStatus, activeUsers, messages, rooms
clientStatus = {}
activeUsers = []
messages = []
rooms = []

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

        # self.messageCount = 0
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
                # message = 'logout user'
                self.clientAlive = False
                user = message['username']
                print(f'> ' + user + ' has logged out')
                self.process_logout(message)
                continue
            elif message['type'] == 'BCM':
                print("[recv] Broadcast message requested")
                self.broadcastMessage(message)
                # self.clientSocket.send(message.encode())
            elif message['type'] == 'ATU':
                print("[recv] Download Active Users requested")
                self.sendUsersToClient(message)
                # print("[send] " + message)
                # self.clientSocket.send(message.encode())
            elif message['type'] == 'SRB':
                print("[recv] Separate room creation requested")
                self.createRoom(message)
                # print("[send] " + message)
                # self.clientSocket.send(message.encode())
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

        # Blocking of user
        if 'block' in message and message['block'] == True:
            self.clientAlive = False
            dt = datetime.now()
            ts = datetime.timestamp(dt)
            self.blockedSince = dt
            clientStatus[message['username']] = ts
            return

        if message['username'] in credentials:
            # Logic underneath deals with blocked user first
            dt = datetime.now()
            ts = datetime.timestamp(dt)
            if message['username'] in clientStatus and ts - clientStatus[message['username']] < 10:
                self.clientAlive = False
                self.clientSocket.send(response.encode())
                return

            if message['password'] == credentials[message['username']]: 
                dt = datetime.now()
                ts = datetime.timestamp(dt)

                user = message['username']
                formatTimestamp = dt.strftime('%d %b %Y %H:%M:%S')
                clientIP = message['clientIP']
                clientUDP = message['clientUDP']

                activeUsers.append((user, formatTimestamp, clientIP, clientUDP))
                response = 'AUTHENTICATED'
                self.clientSocket.send(response.encode())

                # Userlog things
                open('userlog.txt', 'w').close()
                with open('userlog.txt', mode='a') as log:
                    i = 0
                    seqNum = 1
                    while i < len(activeUsers):
                        appendToUserLog = f'{seqNum}; {activeUsers[i][1]}; {activeUsers[i][0]}; {activeUsers[i][2]}; {activeUsers[i][3]}'
                        log.write(appendToUserLog + '\n')
                        i += 1
                        seqNum += 1
            else:
                response = str(number_of_consecutive_failed_attempts)
                print(response)
                self.clientSocket.send(response.encode())
        else:
            response = str(number_of_consecutive_failed_attempts)
            print(response)
            self.clientSocket.send(response.encode())

    def process_logout(self, message):
        global activeUsers
        activeUsers = list(filter(lambda x: x[0] != message['username'], activeUsers))
        # print("active users: " + str(activeUsers))
        open('userlog.txt', 'w').close()
        with open('userlog.txt', mode='a') as log:
            i = 0
            seqNum = 1
            while i < len(activeUsers):
                # appendToUserLog = f'{activeUsers[i]}'
                appendToUserLog = f'{seqNum}; {activeUsers[i][1]}; {activeUsers[i][0]}; {activeUsers[i][2]}; {activeUsers[i][3]}'
                log.write(appendToUserLog + '\n')
                i += 1
                seqNum += 1

    def broadcastMessage(self, message):
        dt = datetime.now()
        ts = datetime.timestamp(dt)

        formatTimestamp = dt.strftime('%d %b %Y %H:%M:%S')
        messages.append(message)
        count = len(messages)
        user = message['username']
        messageToBroadcast = message['messageToBroadcast']

        print(f'> {user} broadcasted BCM #{count} "{messageToBroadcast}" at {formatTimestamp}.')

        appendToMessageLog = f'{count}; {formatTimestamp}; {user}; {messageToBroadcast}'
        with open('messagelog.txt', mode='a') as log:
          log.write(appendToMessageLog + '\n')

    def sendUsersToClient(self, message):
        global activeUsers

        otherActiveUsers = list(filter(lambda x: x[0] != message['username'], activeUsers))
        print("other users " + str(otherActiveUsers))
        print("all active users " + str(activeUsers))

        response = {
            'otherActiveUsers': otherActiveUsers,
        }
        print(response)
        self.clientSocket.send(bytes(json.dumps(response),encoding='utf-8'))
    
    def createRoom(self, message):
        global rooms, activeUsers

        separateRoomUsers = message['separateRoomUsers']
        for user in separateRoomUsers:
            if user not in list(zip(*activeUsers))[0] or user == message['username']:
                response = {
                    'type': 'FAIL',
                }
                self.clientSocket.send(bytes(json.dumps(response),encoding='utf-8'))
                return

        # Add user who requested back into room
        separateRoomUsers.append(message['username'])
        
        for room in rooms:
            if all(elem in room[1]  for elem in separateRoomUsers):
                print(f'Separate chat room has been created, room ID: {room[0]}, already created for these users')
                response = {
                    'type': 'FAIL',
                    'exists': True,
                    'id': room[0]
                }
                self.clientSocket.send(bytes(json.dumps(response),encoding='utf-8'))
                return
        
        rooms.append((len(rooms) + 1, separateRoomUsers))

        response = {
            'type': 'SUCCESS',
        }
        self.clientSocket.send(bytes(json.dumps(response),encoding='utf-8'))

        f = open(f'SR_{len(rooms)}_messagelog.txt', 'w')
        open(f'SR_{len(rooms)}_messagelog.txt', 'w').close()

print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")

while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt)
    clientThread.start()

def removeSeparateRoomLog(dir, pattern):
    for f in os.listdir(dir):
        if re.search("SR_+\dmessagelog.txt", f):
            os.remove(os.path.join(dir, f))