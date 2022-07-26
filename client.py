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
import datetime

from _thread import *

COMMANDS = ['BCM', 'ATU', 'SRB', 'SRM', 'RDM', 'OUT', 'UDP']

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
        if response == 'AUTHENTICATED':
            print('> Welcome to the TOOM!')
            break
        elif response == 'LOCKED USER':
            print('> Your account is blocked due to multiple login failures. Please try again later')
            clientSocket.close()
            exit()
        else:
            unsuccessfulLogin += 1
            if unsuccessfulLogin == int(response):
                print('Invalid Password. Your account has been blocked. Please try again later')
                message['block'] = True
                clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))
                exit()
            print('> Invalid Password. Please try again')
            newpassword = input('> Password: ')
            message['password'] = newpassword
            clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))
            continue
    return

def logout(username, clientSocket):
    message = {
        'type':'logout',
        'username': username
    }
    clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))
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
        users = response['otherActiveUsers']
        if len(users) == 0:
            print('No other users active.')
        for user in users:
            if user[0] == username:
                continue
            print(f'    > {user[0]}, {user[2]}; {user[3]}; active since {user[1]}')
        break

def separateRoomBuilding(username, separateRoomUsers, clientSocket):
    message = {
        'type': 'SRB',
        'username': username,
        'separateRoomUsers': separateRoomUsers,
    }
    clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))

    while True:
        serverResponse = clientSocket.recv(1024)
        response = json.loads(serverResponse.decode('utf-8'))

        if response['type'] == 'FAIL':
            if 'exists' in response:
                roomid = response['id']
                print(f'A separate room (ID: {roomid}) already created for these users')
                break
            print('One or more users are not active')
            break
        else:
            print(response['message'])
            break

def separateRoomMessage(username, roomID, messageToSend, clientSocket):
    message = {
        'type': 'SRM',
        'username': username,
        'roomID': roomID,
        'messageToSend': messageToSend,
    }
    clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))
    
    while True:
        serverResponse = clientSocket.recv(1024)
        response = json.loads(serverResponse.decode('utf-8'))
        print(response['message'])
        break

def readBroadcastMessage(username, messageType, timestamp, clientSocket):
    message = {
        'type': 'RDM b',
        'username': username,
        'messageType': messageType,
        'timestamp': timestamp,
    }
    clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))

    while True:
        serverResponse = clientSocket.recv(1024)
        response = json.loads(serverResponse.decode('utf-8'))

        readMessages = response['readMessages']
        if len(readMessages) == 0:
            print("    > No missed broadcasted messages!")
        else:
            print(f"Messages broadcasted since {timestamp}:")
            for line in readMessages:
                seq = line[0]
                time = line[1]
                user = line[2]
                message = line[3]
                message = message.replace('\n', '')
                print(f"    #{seq}; {user}: {message} at {time}")
        break

def readSepRoomMessage(username, messageType, timestamp, clientSocket):
    message = {
        'type': 'RDM s',
        'username': username,
        'messageType': messageType,
        'timestamp': timestamp,
    }
    clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))

    while True:
        serverResponse = clientSocket.recv(1024)
        response = json.loads(serverResponse.decode('utf-8'))
        readMessages = response['readMessages']
        if len(readMessages) == 0:
            print("    > No missed separate room messages!")
        else:
            for room in readMessages:
                roomID = room[0]
                print(f'room-{roomID}:')
                if len(room[1]) == 0:
                    print(f'    No new messages in room {roomID}')
                    continue
                for msg in room[1]:
                    seq = msg[0]
                    time = msg[1]
                    user = msg[2]
                    message = msg[3]
                    message = message.replace('\n', '')
                    print(f"    #{seq}; {user}: {message} at {time}")
        break

def uploadFile(username, user, filename, clientSocket):
    message = {
        'type': 'UDP',
        'userToRetrieve': user,
    }
    clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))
    response = {}
    while True:
        serverResponse = clientSocket.recv(1024)
        response = json.loads(serverResponse.decode('utf-8'))
        break

    # print(response)
    sendFile(username, response['userIP'], response['userUDP'], filename)

def sendFile(username, ip, port, filename):
    serverIP = ip
    serverPort = int(port)
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    # clientSocket.connect((serverIP, serverPort))

    # message = f'{filename}'
    message = {
        'filename': filename,
        'recvUser': username,
    }
    # print(message)
    # clientSocket.send(bytes(message,encoding='utf-8'))
    clientSocket.sendto(bytes(json.dumps(message),encoding='utf-8'),(serverIP, serverPort))
    clientSocket.close()
    return

def createReceiverServer(ip, port):
    serverIP = ip
    serverPort = int(port)

    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((serverIP, serverPort))
    try:
        start_new_thread(receiveFile, (serverSocket, ))
        # print('thread created')
        # print(serverIP)
        # print(serverPort)
    except:
        print('Thread not started')

def receiveFile(serverSocket):
    # print('\nready to recv')
    while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        response = json.loads(message.decode('utf-8'))
        # print(response)
        filename = response['filename']
        user = response['recvUser']
        print(f'\n> Received {filename} from {user}')
        print("> Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT or UDP): ")
        # break

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

    # Create UDP receiver server
    createReceiverServer(clientIP, client_udp_port)

    while True:
        command = input("> Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT or UDP): ")

        if command[0:3] == 'OUT':
            logout(username, clientSocket)
        elif command[0:3] == 'BCM':
            if command == 'BCM':
                print('> Please write a message')
                continue
            messageToBroadcast = command.split(' ', 1)[1]
            broadcastMessage(username, clientSocket, messageToBroadcast)
        elif command[0:3] == 'ATU':
            displayActiveUsers(username, clientSocket)
        elif command[0:3] == 'SRB':
            if len(command) == 3:
                print('Must add users to separate room service')
                continue
            separateRoomUsers = (command.split(' ', 1)[1]).split(' ')
            separateRoomBuilding(username, separateRoomUsers, clientSocket)
        elif command[0:3] == 'SRM':
            if len(command) == 3 or len(command.split(' ')) < 3:
                print('Must have room ID and message to send')
                continue
            srm = command.split(' ', 2)
            roomID = srm[1]
            messageToSend = srm[2]
            separateRoomMessage(username, roomID, messageToSend, clientSocket)
        elif command[0:3] == 'RDM':
            if len(command) == 3:
                print('Must have message type and timestamp')
                continue
            rdm = command.split(' ', 2)
            messageType = rdm[1]
            timestamp = rdm[2]
            try:
                datetime.datetime.strptime(timestamp, '%d %b %Y %H:%M:%S')
            except ValueError:
                print("This is the incorrect date string format")
                print("Please enter in the form dd MON HH:MM:SS")
                continue
            if messageType == 'b':
                readBroadcastMessage(username, messageType, timestamp, clientSocket)
            if messageType == 's':
                readSepRoomMessage(username, messageType, timestamp, clientSocket)
        elif command[0:3] == 'UDP':
            if len(command) == 3:
                print('Must have user and file name')
                continue
            udp = command.split(' ', 2)
            user = udp[1]
            filename = udp[2]
            try:
                f = open(f"{filename}")
                # Do something with the file
                uploadFile(username, user, filename, clientSocket)
            except IOError:
                print("File not accessible")
                continue
        else:
            print("> Error. Invalid command!")
            
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
