import socket
import threading
import protocols
import database


# every socket for each client will be stored here
CONNECTIONS = []
# the alias (username) of each currently connected peer will be stored here
PEER_ALIASES = []
# the listening socket of each currently connected peer will be stored here
PEER_LISTENERS = []

# setting up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP IPv4
server_ip = socket.gethostbyname(socket.gethostname()) # gets the IP of the host machine
server_port = 6999  # arbitrary non-privileged port for connecting
server_socket.bind((server_ip, server_port))


def handle_client(conn):
    delimeter = " "
    connected = True
    while connected:
        initial_string = conn.recv(2048).decode("utf-8")
        initial_string_list = initial_string.split(delimeter)
        protocol = initial_string_list[0]
        # handles user login/authentication/registration
        if protocol == protocols.AUTHENTICATION:
            user_alias = initial_string_list[1]
            user_listener_ip = initial_string_list[2]
            user_listener_port = initial_string_list[3]
            if user_alias in PEER_ALIASES:
                # an alias with the same name is already connected
                # error code 13
                conn.send(str(13).encode("utf-8"))
            # if not in alias (not connected yet)
            # then we authenticate the alias
            reply = database.authenticate(user_alias)
            if reply == 11:
                # code 11: the alias wasn't in the database
                # we create the alias and send welcome msg
                print(f"{user_alias} just connected!")
                PEER_ALIASES.append(user_alias)
                user_listener = (user_listener_ip, int(user_listener_port))
                PEER_LISTENERS.append(user_listener)
                # print(aliases)
                # print(client_listeners)
                conn.send(str(reply).encode("utf-8"))
            elif reply == 12:
                # code 12: the alias already in database
                # we send welcome back message
                print(f"{user_alias} just connected!")
                PEER_ALIASES.append(user_alias)
                user_listener = (user_listener_ip, int(user_listener_port))
                PEER_LISTENERS.append(user_listener)
                # print(aliases)
                # print(client_listeners)
                conn.send(str(reply).encode("utf-8"))
        elif protocol == protocols.REFRESH:
            reply = ""
            for index, name in enumerate(PEER_ALIASES):
                # client_name "AT" client_address, makes sense?
                name_addr_tuple = name + "@" + str(PEER_LISTENERS[index])
                reply += name_addr_tuple + "__"
            reply = protocols.REFRESH_UPDATE + ";;" + reply
            # print('[DEBUG - reply message]: ', reply)
            conn.send(str(reply).encode("utf-8"))
        elif protocol == protocols.DISCONNECT:
            index = CONNECTIONS.index(conn)
            CONNECTIONS.remove(conn)
            alias = PEER_ALIASES[index]
            PEER_ALIASES.remove(alias)
            listener = PEER_LISTENERS[index]
            PEER_LISTENERS.remove(listener)
            # shows who just disconnected
            debug_message = f"{alias} just disconnected!"
            print(debug_message)
            break


server_socket.listen()
# print to the debug console the address
print(f"Server is on and listening on {server_ip}:{server_port}")
while True:
    connection_socket, addr = server_socket.accept()
    print(f"[New connection] {addr} connected!")
    CONNECTIONS.append(connection_socket)
    print(f"Current connection count: {len(CONNECTIONS)}")
    client_thread = threading.Thread(target=handle_client, args=(connection_socket,))
    client_thread.start()
