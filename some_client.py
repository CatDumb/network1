import socket
import threading

FORMAT = 'utf-8'
#SERVER_IP = socket.gethostbyname(socket.gethostname())
#SERVER_PORT = 19050
#server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_socket.bind((SERVER_IP, SERVER_PORT))


def receive_message(conn):
    while True:
        client_message = conn.recv(1024).decode()
        print(client_message)

def send_message(conn):
    while True:
        message = input("Enter a message: ")
        conn.send(message.encode())


def handle_client(conn, addr):
    print(f'client {addr} connected.')
    sending_thread = threading.Thread(target=send_message, args=(conn,))
    receiving_thread = threading.Thread(target=receive_message, args=(conn,))
    sending_thread.start()
    receiving_thread.start()


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.210.113', 19050))
sending_thread = threading.Thread(target=send_message, args=(client_socket,))
receiving_thread = threading.Thread(target=receive_message, args=(client_socket,))
sending_thread.start()
receiving_thread.start()