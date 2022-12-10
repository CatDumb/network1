import socket
import threading
import protocols
import database


connections = []
aliases = []
client_listeners = []


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = socket.gethostbyname(socket.gethostname())
server_port = 16996
server_socket.bind((server_ip, server_port))


def handle_client(conn, addr):
    delimeter = " "
    connected = True
    while connected:
        initial_string = conn.recv(2048).decode('utf-8')
        initial_string_list = initial_string.split(delimeter)
        protocol = initial_string_list[0]
        # handles user login/authentication/registration, you name it
        if protocol == protocols.AUTHENTICATION:
            user_alias = initial_string_list[1]
            user_listener_ip = initial_string_list[2]
            user_listener_port = initial_string_list[3]
            if user_alias in aliases:
                # an alias with the same name is already connected
                # error code 13
                conn.send(str(13).encode('utf-8'))
            # if not in alias (not connected yet)
            # then we authenticate the alias
            reply = database.authenticate(user_alias)
            if reply == 11:
                # code 11: the alias wasn't in the database
                # we create the alias and send welcome msg
                aliases.append(user_alias)
                user_listener = (user_listener_ip, int(user_listener_port))
                client_listeners.append(user_listener)
                print(aliases)
                print(client_listeners)
                conn.send(str(reply).encode('utf-8'))
            elif reply == 12:
                # code 12: the alias already in database
                # we send welcome back message
                aliases.append(user_alias)
                user_listener = (user_listener_ip, int(user_listener_port))
                client_listeners.append(user_listener)
                print(aliases)
                print(client_listeners)
                conn.send(str(reply).encode('utf-8'))
        elif protocol == protocols.REFRESH:
            reply = ''
            for index, name in enumerate(aliases):
                # client_name "AT" client_address, makes sense?
                name_addr_tuple = name + '@' + str(client_listeners[index])
                reply += name_addr_tuple + '; '
            conn.send(str(reply).encode('utf-8'))
        elif protocol == protocols.DISCONNECT:
            index = connections.index(conn)
            connections.remove(conn)
            alias = aliases[index]
            aliases.remove(alias)
            break


server_socket.listen()
print(f'Server is on and listening on {server_ip}:{server_port}')
while True:
    connection_socket, addr = server_socket.accept()
    print(f'[New connection] {addr} connected!')
    connections.append(connection_socket)    
    print(f"Current connection count: {len(connections)}")
    client_thread = threading.Thread(
        target=handle_client, args=(connection_socket, addr))
    client_thread.start()
