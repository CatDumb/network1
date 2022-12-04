## serves the intermediary role between nodes.
##
## using PEP8(Python Enhancement Proposal) naming convention
## where function and variable names are lowercase with words
## separated by underscores
import socket
import threading

HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"


server_ip = socket.gethostbyname(socket.gethostname())
server_port = 12512
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_addr = (server_ip, server_port)
server_socket.bind(server_addr)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                print(f'[DISCONNECTED] {addr} has disconnected from central server.')
                connected = False

            print(f"[{addr}] {msg}")
            conn.send("Msg received".encode(FORMAT))

    conn.close()

def start():
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {server_ip}:{server_port}")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()