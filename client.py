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
    }
    clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))

    unsuccessfulLogin = 0
    while True:
        receivedSentence = clientSocket.recv(1024)
        received = receivedSentence.decode('utf-8')
        #print('>>>>>>>>>>>>>>>>>>>>>>')
        #print(received)
        if received == 'AUTHENTICATED':
            print('> Welcome to the TOOM!')
            break
        elif received == 'INVALID CREDENTIALS':
            unsuccessfulLogin += 1
            print("unsuccessfulLogin = " + str(unsuccessfulLogin))
            print('number_of_consecutive_failed_attempts = ' + os.getenv('ALLOWED_FAILS'))
            # if unsuccessfulLogin == 3:
            if unsuccessfulLogin == os.getenv('allowed_fails'):
                print('Invalid Password. Your account has been blocked. Please try again later')
                exit()
            # print(received)
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
    #print(tempid)
    print('Bye ' + username + '!')
    clientSocket.close()
    exit()

def connectToServer(host, port, client_udp_port):
    serverHost = host
    serverPort = port
    # define a socket for the client side, it would be used to communicate with the server
    clientSocket = socket(AF_INET, SOCK_STREAM)
    # build connection with the server and send message to it
    clientSocket.connect((serverHost, serverPort))

    # Login attempts
    username = input('> Username: ')
    password = input('> Password: ')
    
    login(username, password, clientSocket)

    while True:
        command = input("> Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT): ")

        if command not in COMMANDS:
            print("> Error. Invalid command!")
        elif command == 'OUT':
            logout(username, clientSocket)
        
    # close the socket
    clientSocket.close()

if __name__ == '__main__':
    #Server would be running on the same host as Client
    if len(sys.argv) != 4:
        print("\n===== Error usage, python3 TCPClient3.py SERVER_IP SERVER_PORT CLIENT_UDP_PORT ======\n")
        exit(0)
    serverHost = sys.argv[1]
    serverPort = int(sys.argv[2])
    client_udp_port = int(sys.argv[3])
    # serverAddress = (serverHost, serverPort)
    connectToServer(serverHost, serverPort, client_udp_port)
