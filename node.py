## a client-server running as a process
## each peer is a process of such kind
## the node utilizes multithreading
## each socket for each new connection (serves multi-chat)
## server on one thread, client on another thread
## server listens to multiple clients; clients connect to ONE other server

import socket
import threading 
import os
import sys

FORMAT = "utf-8"
HEADER = 64
DISCONNECT_MESSAGE = "!DISCONNECT"
central_ip = '192.168.210.113'
central_port = 12512
central_addr = (central_ip, central_port)


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client_socket.send(send_length)
    client_socket.send(message)
    print(client_socket.recv(2048).decode(FORMAT))


def handle_client(conn, addr):
    print(f"[NEW PEER] {addr} connected!")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            conn.send("Msg received".encode(FORMAT))

    conn.close()



## we need a listening socket for OTHER PEERS to connect to
this_ip = socket.gethostbyname(socket.gethostname())
this_port = 12569

this_addr = (this_ip, this_port)
listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listening_socket.bind(this_addr)

## every peer has to LISTEN for connections from other peers
def listen_for_others():
    listening_socket.listen()
    while True:
        conn, addr = listening_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

## we need to connect THIS PEER into the central server
def connect_to_central():
    client_socket.connect(central_addr)
    is_connected = True
    send(str(this_addr))
    while is_connected:
        message = input("[client]: ")
        send(message)
        if message == DISCONNECT_MESSAGE:
            is_connected = False
            os._exit()




if __name__ == "__main__":
    central_server_thread = threading.Thread(target=connect_to_central)
    central_server_thread.start()
    listening_thread = threading.Thread(target=listen_for_others)
    listening_thread.start()
