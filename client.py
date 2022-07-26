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

COMMANDS = ['BCM', 'ATU', 'SRB', 'SRM', 'RDM', 'OUT']

def handleLogin(username, password, clientSocket):
    message = {
        'type': 'login',
        'username': username,
        'password': password,
    }
    clientSocket.send(bytes(json.dumps(message),encoding='utf-8'))
    # clientSocket.sendall(message.encode())
    data = clientSocket.recv(1024)
    receivedMessage = data.decode()
    
    pass

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

    print("> Welcome to TOOM!")
    
    handleLogin(username, password, clientSocket)

    while True:
        command = input("> Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT): ")

        if command not in COMMANDS:
            print("> Error. Invalid command!")
        
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
