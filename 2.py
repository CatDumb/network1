import socket
import threading
import protocols
import sys
import PySimpleGUI as sg


# global_aliases list stores the available peers aliases which this one can connect to
# it's natural to omit oneself from such list ( no "Talking To Myself" ^^)
# global_listeners list stores the corresponding listening socket on each equivalent global aliases
# this peer will use the values there to connect to them
global_aliases = []
global_listeners = []
conversation_list = []

# -----------LISTENER CONFIGURATION START----------
# setting up the peer's own listening socket (like a server)
# where other peers can connect to 
this_ip = socket.gethostbyname(socket.gethostname())
this_port = 15061
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
        receiving_thread = threading.Thread(target=receive_message, args=(conn, addr), daemon=True)
        sending_thread = threading.Thread(target=send_message, args=(conn,), daemon=True)
        receiving_thread.start()
        sending_thread.start()

def connect_to_others(raw_foreign_addr):
    # get ip and port from this string first
    # ('ip', port)
    raw_foreign_addr = raw_foreign_addr.strip("()")
    foreign_ip = raw_foreign_addr.split(', ')[0]
    foreign_ip = foreign_ip.replace("'", "")
    foreign_port = raw_foreign_addr.split(', ')[1]
    foreign_addr = (foreign_ip, int(foreign_port))
    new_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_client_socket.connect(foreign_addr)
    receiving_thread = threading.Thread(target=receive_message, args=(new_client_socket, foreign_addr), daemon=True)
    sending_thread = threading.Thread(target=send_message, args=(new_client_socket,), daemon=True)
    receiving_thread.start()
    sending_thread.start()


def receive_message(conn, addr):
    global window
    while True:
        client_message = conn.recv(1024).decode('utf-8')
        window['-CHATOUTPUT-'+sg.WRITE_ONLY_KEY].print(f'[{addr}]: ' + client_message)
        conversation_list.append(client_message)
        print(client_message)


def send_message(conn):
    global my_alias
    global window
    while True:
        message = input("Enter a message: ")
        conversation_list.append(f'[{my_alias}]: ' + message)
        window['-CHATOUTPUT-'+sg.WRITE_ONLY_KEY].print(f'[{my_alias}]: ' + message)
        conn.send(message.encode('utf-8'))


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


sg.theme("Green")
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
    [sg.Text("Click refresh to check out available people", key='-ONLINECOUNT-')],
    [
        sg.Listbox(
            values=[],
            size=(20, 10),
            key="onlinePeers",
            no_scrollbar=False,
            enable_events=True,
        )
    ],
    [sg.Button('Refresh'), sg.Button("Log off")]
]

message_layout = [
    [sg.Multiline(size=(65, 20), key='-CHATOUTPUT-'+sg.WRITE_ONLY_KEY)],
    [sg.Multiline(size=(70, 5), enter_submits=True, key='-QUERY-', do_not_clear=False),
           sg.Button('SEND', bind_return_key=True),
           sg.Button('CLEAR')]
]

chat_layout = [
    [
        sg.Column(
            onlinePeersLayout, element_justification="l", key="left_col", pad=(20, 20)
        ),
        sg.Column(layout=message_layout)
    ]
]
listening_thread = threading.Thread(target=on_new_connection, daemon=True)
listening_thread.start()
window = sg.Window(f"Chatatouille - {my_alias}", chat_layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == "Refresh":
        client_socket.send((protocols.REFRESH).encode('utf-8'))
        reply = client_socket.recv(2048).decode('utf-8')
        # print(reply)
        reply_to_list = reply.split(';;')
        to_be_tokenized = reply_to_list[1] # all the users are in here
        # print(to_be_tokenized)
        raw_user_list = to_be_tokenized.split('__')
        if reply_to_list[0] == protocols.REFRESH_UPDATE:
            for user in raw_user_list:
                # print(user)
                # print(user.partition('@')[0])
                # if the users in the update is not in the global alias list
                # then we add it. Skip self
                if (user.partition('@')[0] not in global_aliases and user != "" and user.partition('@')[0] != my_alias):
                    global_aliases.append(user.partition('@')[0])
                    global_listeners.append(user.partition('@')[2])
            for alias in global_aliases:
                if alias not in to_be_tokenized:
                    # print('uh oh')
                    index = global_aliases.index(alias)
                    global_aliases.remove(alias)
                    listener = global_listeners[index]
                    global_listeners.remove(listener)                    
        # print(global_aliases) #debug
        # print(global_listeners) #debug
        window.refresh()
        window['onlinePeers'].update(values=global_aliases)
        window['-ONLINECOUNT-'].update("Looks like no one is online :(" if len(global_aliases) == 0 else (f'{str(len(global_aliases))} friend is online! ^^'))
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
    elif event == 'CLEAR':
        window['-CHATOUTPUT-'].Update('You just pressed clear')
    elif event == 'SEND':
        print(event, values)
        query = values['-QUERY-'].rstrip()
        # EXECUTE YOUR COMMAND HERE
        #print('[Nho] {}'.format(query), flush=True)
        sg.cprint(values['-QUERY-'].rstrip())
    elif (event == sg.WIN_CLOSED or event == "Log off"):
        client_socket.send((protocols.DISCONNECT).encode('utf-8'))
        client_socket.close()
        break
    # elif event.startswith('Start'):
    #     threading.Thread(target=the_thread, args=(window,), daemon=True).start()
window.close()



# idea:
# can chat log be some sort of two dimensional array? or just array? where
# a client is in an index.
# whenever we chat we can update the data inside that index and when we switch to an arbitrary connection
# we get the index and we display as "log"? 