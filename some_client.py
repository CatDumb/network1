import socket
import threading
import protocols
import sys
import PySimpleGUI as sg
import time


global_aliases = []
global_listeners = []
conversation_list = []

# -----------LISTENER CONFIGURATION START----------
# setting up the peer's own listening socket (like a server)
# where other peers can connect to 
this_ip = socket.gethostbyname(socket.gethostname())
this_port = 15060
this_addr = (this_ip, this_port)
listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listening_socket.bind(this_addr)
listening_socket.listen()


THREAD_EVENT = '-THREAD-'
cp = sg.cprint

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

# -----------CONNECT TO OTHER CONFIGURATION START----------
from_outer_aliases = []
from_outer_connections=[]


# where this peer connects to others
to_outer_connections = []
to_outer_aliases = []
conversation_list_in = []
conversation_list_out = []
def on_new_connection():
    while True:
        conn, addr = listening_socket.accept()
        print(f'{addr} connected')
        from_outer_connections.append(conn)

def connect_to_others(raw_foreign_addr):
    # get ip and port from this string first
    # ('ip', port)
    raw_foreign_addr = raw_foreign_addr.strip("()")
    foreign_ip = raw_foreign_addr.split(', ')[0]
    foreign_ip = foreign_ip.replace("'", "")
    # print('from functioasfasf: ' + foreign_ip)
    foreign_port = raw_foreign_addr.split(', ')[1]
    foreign_addr = (foreign_ip, int(foreign_port))
    # print('from function: ' + str(foreign_addr))
    new_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_client_socket.connect(foreign_addr)
    receiving_thread = threading.Thread(target=receive_message, args=(new_client_socket,), daemon=True)
    sending_thread = threading.Thread(target=send_message, args=(new_client_socket,), daemon=True)
    receiving_thread.start()
    sending_thread.start()


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


def the_thread(window):
    window.write_event_value('-THREAD-', (threading.current_thread().name, i))
    i += 1
# -----------CONNECT TO OTHER CONFIGURATION END----------



def listen_for_others():
    while True:
        conn, addr = listening_socket.accept()
        print(f'[New connection] {addr} connected!')
        connections.append(conn)


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
    [sg.Button('Refresh'), sg.Button("Logout")],
    [
        sg.Listbox(
            values=[],
            size=(20, 10),
            key="onlinePeers",
            no_scrollbar=False,
            enable_events=True,
        )
    ],
    #[sg.Button("Refresh")],
    #[sg.Button("Logout", pad=((0, 0), (50, 20)))],
]

message_layout = [
    [
        sg.Multiline(
            key = '-CHATOUT-',
            enable_events = True,
            size = (65,20),
            reroute_cprint=True
        )
    ],
    [sg.Text('Type your message: '), sg.Input(key='-IN-', size=(45,1))],
    [sg.B('Start a thread')]
]

chat_layout = [
    [
        sg.Column(message_layout, key="right_col"),
        sg.Column(
            onlinePeersLayout, element_justification="c", key="left_col", pad=(20, 20)
        ),
    ]
]
listening_thread = threading.Thread(target=on_new_connection, daemon=True)
listening_thread.start()
window = sg.Window(f"Chatatouille - {my_alias}", chat_layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    cp(event, values)
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
    elif event == THREAD_EVENT:
        cp(f'Data from the thread ')
        cp(f'{values[THREAD_EVENT]}')
    elif event == "onlinePeers":
        print(event)
        print(values)
        selection = values[event]
        if selection:
            # print(selection[0])
            # get the alias to connect to
            alias_to_connect = selection[0]
            # append that to list to track
            # ------
            to_outer_aliases.append(alias_to_connect)
            index = global_aliases.index(alias_to_connect)
            address_to_connect = global_listeners[index]
            # to_outer_connections.append(address_to_connect)
            # ------            
            # print(outward_connected_aliases)
            print('here: ' + address_to_connect)
            client_thread = threading.Thread(target=connect_to_others, args=(address_to_connect,), daemon=True)
            client_thread.start()


    elif (event == sg.WIN_CLOSED or event == "Logout"):
        client_socket.send((protocols.DISCONNECT).encode('utf-8'))
        client_socket.close()
        break
    # elif event.startswith('Start'):
    #     threading.Thread(target=the_thread, args=(window,), daemon=True).start()
window.close()
