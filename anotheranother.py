# for testing purposes

import socket
import threading
import protocols
import sys
import PySimpleGUI as sg


global_aliases = []
global_listeners = []


# -----------LISTENER CONFIGURATION START----------
# setting up the peer's own listening socket (like a server)
# where other peers can connect to 
this_ip = socket.gethostbyname(socket.gethostname())
this_port = 19026
this_addr = (this_ip, this_port)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(this_addr)
server_socket.listen()


# maintains connected peers
connections = []
# maintains connected aliases
aliases = []
# notice there is no client listeners list like in main server
# because when others connect to this node, they can already communicate
# there's no reason for the other end to "listen" to this
# -----------LISTENER CONFIGURATION END----------


# idea: other peers which connect to this will be stored in the connections
# and aliases list. When the user on this peer decides to chat with one of the
# users in that list, we find that user in the aliases list, get the index 
# (since they update concurrently) and locate the connection associated 
# with that index to start dropping shit into the connection stream 


# using a listbox to store the conversation
# can we use a list and append to that?
conversation_list = []


#def connect_to_others():


def listen_for_others():
    while True:
        conn, addr = server_socket.accept()
        print(f'[New connection] {addr} connected!')
        connections.append(conn)






def handle_client(conn, addr):
    print(f"client {addr} connected.")
    delimeter = " "
    connected = True
    sending_thread = threading.Thread(target=send_message, args=(conn,))
    receiving_thread = threading.Thread(target=receive_message, args=(conn,))
    sending_thread.start()
    receiving_thread.start()



def receive_message(conn):
    while True:
        client_message = conn.recv(1024).decode()
        conversation_list.append(client_message)
        print(client_message)


def send_message(conn):
    while True:
        message = input("Enter a message: ")
        conversation_list.append(message)
        conn.send(message.encode())


login_status = ''
def do_login(alias):
    msg = protocols.AUTHENTICATION + " " + alias + " " + this_ip + " " + str(this_port)
    client_socket.send(msg.encode("utf-8"))
    reply = client_socket.recv(1024).decode("utf-8")
    if reply == "11":
        print(type(reply))
        print(reply)
        print("hehehe connected okay, welcome!")
        return f"Welcome, {alias}"
    elif reply == "12":
        print(type(reply))
        print(reply)
        print("hehe welcome back")
        return f"Welcome back, {alias}"
    elif reply == "13":
        print("fuck off mate")
        return "The name you entered was chosen already!"


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# sending_thread = threading.Thread(target=send_message, args=(client_socket,))
# receiving_thread = threading.Thread(target=receive_message, args=(client_socket,))
# sending_thread.start()
# receiving_thread.start()


sg.theme("SandyBeach")
# PySimpleGUI uses camelCase, not pep8 like_this
# we'll try our best to not make mistakes!


# GUI to get server IP and port
central_ip = sg.popup_get_text("Enter server IP", "Welcome to Chatatouille")
central_port = sg.popup_get_text("Enter server port", "Welcome to Chatatouille")


# connect after getting ip and port
# if the server isn't on or whatever other reason
# we stop the process after displaying the error message in a popup
try:
    client_socket.connect((central_ip, int(central_port)))
except socket.error as e:
    sg.popup(e)
    sys.exit()
    

# GUI to get chat alias
my_alias = sg.popup_get_text("Please enter your name", "Welcome to Chatatouille")

status = do_login(my_alias)
onlinePeersLayout = [
    [
        sg.Listbox(
            values=[],
            size=(20, 10),
            key="onlinePeers",
            no_scrollbar=False,
            enable_events=True,
        )
    ],
    [sg.Button("Refresh")],
    [sg.Button("Logout", pad=((0, 0), (50, 20)))],
]

message_layout = [
    [
        sg.Listbox(
            values=conversation_list,
            expand_x=True,
            size=(0, 15),
            key="chat_box",
            no_scrollbar=True,
        )
    ],
    [sg.Input(), sg.Button("Send")],
]

chat_layout = [
    [
        sg.Column(message_layout, key="right_col"),
        sg.Column(
            onlinePeersLayout, element_justification="c", key="left_col", pad=(20, 20)
        ),
    ]
]

window = sg.Window(f"Chatatouille - {my_alias}", chat_layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == "Refresh":
        client_socket.send((protocols.REFRESH).encode('utf-8'))
        reply = client_socket.recv(2048).decode('utf-8')
        print(reply)
        reply_to_list = reply.split(';;')
        to_be_tokenized = reply_to_list[1] # all the users are in here
        print(to_be_tokenized)
        raw_user_list = to_be_tokenized.split('__')
        if reply_to_list[0] == protocols.REFRESH_UPDATE:
            for user in raw_user_list:
                print(user)
                print(user.partition('@')[0])
                # if the users in the update is not in the global alias list
                # then we add it. Skip self
                if (user.partition('@')[0] not in global_aliases and user != "" and user.partition('@')[0] != my_alias):
                    global_aliases.append(user.partition('@')[0])
                    global_listeners.append(user.partition('@')[2])
            for alias in global_aliases:
                if alias not in to_be_tokenized:
                    print('uh oh')
                    index = global_aliases.index(alias)
                    global_aliases.remove(alias)
                    listener = global_listeners[index]
                    global_listeners.remove(listener)                    
        # print(global_aliases) #debug
        # print(global_listeners) #debug
        window.refresh()
        window['onlinePeers'].update(values=global_aliases)
    elif event == "onlinePeers":
        selection = values[event]
        if selection:
            print(selection[0])
    elif (event == sg.WIN_CLOSED or event == "Logout"):
        client_socket.send((protocols.DISCONNECT).encode('utf-8'))
        client_socket.close()
        break
window.close()
