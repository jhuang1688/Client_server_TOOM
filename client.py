"""
    Python 3
    Usage: python3 client.py localhost 12000
    coding: utf-8
    
    Author: Joel Huang 
    Starter code sourced from Wei Song
"""
from socket import *
import sys
import json
import os

COMMANDS = ['BCM', 'ATU', 'SRB', 'SRM', 'RDM', 'OUT']

def login(username, password, clientSocket):
    message = {
        'type': 'login',
        'username': username,
        'password': password,
        'clientIP': clientIP,
        'clientUDP': client_udp_port,
    }
    clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))

    unsuccessfulLogin = 0
    while True:
        serverResponse = clientSocket.recv(1024)
        response = serverResponse.decode('utf-8')
        #print('>>>>>>>>>>>>>>>>>>>>>>')
        #print(response)
        if response == 'AUTHENTICATED':
            print('> Welcome to the TOOM!')
            break
        elif response == 'LOCKED USER':
            print('> Your account is blocked due to multiple login failures. Please try again later')
            clientSocket.close()
            exit()
        else:
            unsuccessfulLogin += 1
            # print(f'num attempts allowed: ' + str(response))
            # print(int(response))
            # print("unsuccessfulLogin = " + str(unsuccessfulLogin))
            if unsuccessfulLogin == int(response):
                print('Invalid Password. Your account has been blocked. Please try again later')
                message['block'] = True
                clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))
                exit()
            # print(response)
            print('> Invalid Password. Please try again')
            newpassword = input('> Password: ')
            message['password'] = newpassword
            clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))
            continue
        # elif response == 'INVALID CREDENTIALS':
        #     unsuccessfulLogin += 1
        #     print("unsuccessfulLogin = " + str(unsuccessfulLogin))
        #     if unsuccessfulLogin == 3:
        #         print('Invalid Password. Your account has been blocked. Please try again later')
        #         exit()
        #     # print(response)
        #     print('> Invalid Password. Please try again')
        #     newpassword = input('> Password: ')
        #     message['password'] = newpassword
        #     clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))
        #     continue

    return

def logout(username, clientSocket):
    message = {
        'type':'logout',
        'username': username
    }
    clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))
    #print(tempid)
    print('Bye ' + username + '!')
    clientSocket.close()
    exit()

def broadcastMessage(username, clientSocket, messageToBroadcast):
    message = {
        'type': 'BCM',
        'username': username,
        'messageToBroadcast': messageToBroadcast,
    }
    clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))

def displayActiveUsers(username, clientSocket):
    message = {
        'type': 'ATU',
        'username': username,
    }
    clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))

    while True:
        serverResponse = clientSocket.recv(1024)
        response = json.loads(serverResponse.decode('utf-8'))
        # print(type(response))
        users = response['otherActiveUsers']
        if len(users) == 0:
            print('No active users active.')
        for user in users:
            if user[0] == username:
                continue
            print(f'    > {user[0]}, active since {user[1]}')
        break

def separateRoomBuilding():
    pass

def separateRoomMessage():
    pass

def readMessage():
    pass

def connectToServer(host, port, client_udp_port):
    clientIP = host
    serverPort = port
    # define a socket for the client side, it would be used to communicate with the server
    clientSocket = socket(AF_INET, SOCK_STREAM)
    # build connection with the server and send message to it
    clientSocket.connect((clientIP, serverPort))

    # Login attempts
    username = input('> Username: ')
    password = input('> Password: ')
    
    login(username, password, clientSocket)

    while True:
        command = input("> Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT): ")

        if command[0:3] not in COMMANDS:
            print("> Error. Invalid command!")
        elif command[0:3] == 'OUT':
            logout(username, clientSocket)
        elif command[0:3] == 'BCM':
            if command == 'BCM':
                print('> Please write a message')
                continue
            messageToBroadcast = command.split(' ', 1)[1]
            # print(messageToBroadcast)
            broadcastMessage(username, clientSocket, messageToBroadcast)
        elif command[0:3] == 'ATU':
            displayActiveUsers(username, clientSocket)
        elif command[0:3] == 'SRB':
            separateRoomBuilding()
        elif command[0:3] == 'SRM':
            separateRoomMessage()
        elif command[0:3] == 'RDM':
            readMessage()
        
    # close the socket
    clientSocket.close()

if __name__ == '__main__':
    #Server would be running on the same host as Client
    if len(sys.argv) != 4:
        print("\n===== Error usage, python3 TCPClient3.py SERVER_IP SERVER_PORT CLIENT_UDP_PORT ======\n")
        exit(0)
    clientIP = sys.argv[1]
    serverPort = int(sys.argv[2])
    client_udp_port = int(sys.argv[3])
    # serverAddress = (clientIP, serverPort)
    connectToServer(clientIP, serverPort, client_udp_port)
