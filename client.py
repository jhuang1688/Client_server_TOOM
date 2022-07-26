"""
    Python 3
    Usage: python3 TCPClient3.py localhost 12000
    coding: utf-8
    
    Author: Wei Song (Tutor for COMP3331/9331)
"""
from socket import *
import sys

def handleLogin(username, password, clientSocket):
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
    

    while True:
        input("> Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT): ")
        
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
