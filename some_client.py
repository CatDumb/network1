import socket
import threading
import protocols
import sys
import PySimpleGUI as sg
import my_helper
import os
from pathlib import Path

# global_aliases list stores the available peers aliases which this one can connect to
# it's natural to omit oneself from such list ( no "Talking To Myself" ^^)
# global_listeners list stores the corresponding listening socket on each equivalent global aliases
# this peer will use the values there to connect to them
current_target_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CURRENT_ALIAS = ""

GLOBAL_ALIASES = []
GLOBAL_LISTENERS = []
CONVERSATION_LIST = []
conversation_list = []
CONVO_DICT = {}
CONNECTION_DICTIONARY = {}
BUFFER = 16384
# -----------LISTENER CONFIGURATION START----------
# setting up the peer's own listening socket (like a server)
# where other peers can connect to
this_ip = socket.gethostbyname(socket.gethostname())
this_port = 15060
this_addr = (this_ip, this_port)
listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listening_socket.bind(this_addr)
listening_socket.listen()

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
FROM_OUTER_CONNECTIONS = []
FROM_OUTER_ALIASES = []
from_outer_aliases = []
from_outer_connections = []


# where this peer connects to others
TO_OUTER_CONNECTIONS = []
TO_OUTER_ALIASES = []

to_outer_connections = []
to_outer_aliases = []
conversation_list_in = []
conversation_list_out = []


def on_new_connection():
    while True:
        conn, addr = listening_socket.accept()
        print(f"{addr} connected")
        FROM_OUTER_CONNECTIONS.append(conn)
        listening_thread = threading.Thread(
            target=receive_message,
            args=(
                conn,
                addr,
                "in",
            ),
            daemon=True,
        )
        sending_thread = threading.Thread(
            target=send_message, args=(conn,), daemon=True
        )
        listening_thread.start()
        sending_thread.start()


def connect_to_others(raw_foreign_addr):
    foreign_addr = my_helper.get_address_from_string(raw_foreign_addr=raw_foreign_addr)
    new_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_client_socket.bind((this_ip, 0))
    new_client_socket.connect(foreign_addr)
    print("[DEBUG] From connect to others function: ", new_client_socket)
    to_outer_connections.append(new_client_socket)
    current_target_connection = new_client_socket
    receiving_thread = threading.Thread(
        target=receive_message,
        args=(
            new_client_socket,
            foreign_addr,
            "out",
        ),
        daemon=True,
    )
    sending_thread = threading.Thread(
        target=send_message, args=(new_client_socket,), daemon=True
    )
    receiving_thread.start()
    sending_thread.start()


def receive_message(conn, addr, in_or_out):
    recv_file_name = ""
    recv_file_size = ""
    file_data = ""
    client_message = conn.recv(BUFFER).decode("utf-8")
    client_msg_list = client_message.split("__")
    client_alias = client_msg_list[1]
    CONNECTION_DICTIONARY[client_alias] = conn
    # print('[DEBUG] after send event', CONNECTION_DICTIONARY[client_alias])
    if in_or_out == "in":
        if client_alias not in FROM_OUTER_ALIASES:
            FROM_OUTER_ALIASES.append(client_alias)
        print("FROM_OUTER_ALIASES", FROM_OUTER_ALIASES)
    elif in_or_out == "out":
        if client_alias not in TO_OUTER_ALIASES:
            TO_OUTER_ALIASES.append(client_alias)
        print("TO_OUTER_ALIASES :", TO_OUTER_ALIASES)
    while True:
        actual_chat_msg = conn.recv(BUFFER).decode("utf-8")
        actual_chat_msg_list = actual_chat_msg.split("__")
        print('[debug receiving idx 0]', actual_chat_msg_list[0])
        print('[debug receiving idx 1]', actual_chat_msg_list[1])
        client_message_content = actual_chat_msg_list[1]
        if client_message_content == protocols.FILETRANSFER:
            if len(actual_chat_msg_list) > 2:
                print('[debug receiving idx 1]', actual_chat_msg_list[2])
                if actual_chat_msg_list[2] == protocols.FILETRANSEND:
                    CONVO_DICT[client_alias] += f"{client_alias} sent a file." + "<!>"
                elif actual_chat_msg_list[2] == protocols.ADVERTISEFILE:                    
                    print('[debug receiving idx 3]', actual_chat_msg_list[3])
                    recv_file_name = actual_chat_msg_list[3]
                    print('[debug receiving idx 4]', actual_chat_msg_list[4])
                    recv_file_size = actual_chat_msg_list[4]
                    # file = open(recv_file_name, "wb")
                    print("[DEBUG FILE RECV]: ", recv_file_name)
                    print("[DEBUG FILE RECV]: ", recv_file_size)
                elif actual_chat_msg_list[2] == protocols.FILECONTENT:
                    file_data = actual_chat_msg_list[3]
                if file_data != "":
                    print(file_data)
        client_message_content = f"[{client_alias}]: " + client_message_content
        if client_alias not in CONVO_DICT:
            CONVO_DICT[client_alias] = ""
        if protocols.FILETRANSFER not in client_message_content:
            print(client_message_content)
            print("got this")
            CONVO_DICT[client_alias] += client_message_content + "<!>"
        print("[debug]: ", CONVO_DICT[client_alias])
        if client_alias == CURRENT_ALIAS:
            window["-CHATOUTPUT-" + sg.WRITE_ONLY_KEY].update("")
            window["-CHATOUTPUT-" + sg.WRITE_ONLY_KEY].print(
                "\n".join(CONVO_DICT[client_alias].split("<!>"))
            )


def send_message(conn):
    introduction_msg = protocols.INTRODUCE + "__" + my_alias
    conn.send(introduction_msg.encode("utf-8"))


# -----------CONNECT TO OTHER CONFIGURATION END----------
login_status = ""


def do_login(alias):
    msg = protocols.AUTHENTICATION + " " + alias + " " + this_ip + " " + str(this_port)
    client_socket.send(msg.encode("utf-8"))
    reply = client_socket.recv(BUFFER).decode("utf-8")
    if reply == "11":
        return f"Welcome, {alias}"
    elif reply == "12":
        return f"Welcome back, {alias}"
    elif reply == "13":
        return "The name you entered was chosen already!"


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# it's festive season!
sg.theme("DarkRed1")


font = ("Consolas", 14)
sg.set_options(font=font)


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

login_status = do_login(my_alias)


onlinePeersLayout = [
    [sg.Text(login_status)],
    [sg.Text("Click refresh to check out available people", key="-ONLINECOUNT-")],
    [
        sg.Listbox(
            values=[],
            size=(20, 10),
            key="-ONLINEPEERS-",
            no_scrollbar=False,
            enable_events=True,
        )
    ],
    [sg.Button("Refresh", key="-GETFRIENDS-"), sg.Button("Log off")],
]

message_layout = [
    [sg.Text(key="-CURRENTALIAS-")],
    [sg.Multiline(size=(40, 20), key="-CHATOUTPUT-" + sg.WRITE_ONLY_KEY)],
    [
        sg.Multiline(
            size=(35, 2),
            enter_submits=True,
            key="-QUERY-",
            do_not_clear=False,
            no_scrollbar=True,
        ),
        sg.Button("Send", bind_return_key=True, key="-SENDBUTTON-"),
    ],
    [
        sg.Text("File", size=(5, 1), key="-FILEBROWSELABEL-"),
        sg.Input(key="-FILEBROWSENAMESHOW-", size=(10, 1)),
        sg.FileBrowse(key="-FILEBROWSEBUTTON-"),
        sg.Button("Send File", key="-SENDFILE-"),
    ],
]

chat_layout = [
    [
        sg.Column(onlinePeersLayout, element_justification="c", pad=(20, 20)),
        sg.Column(layout=message_layout, element_justification="c", pad=(20, 20)),
    ]
]
listening_thread = threading.Thread(target=on_new_connection, daemon=True)
listening_thread.start()
window = sg.Window(f"Chatatouille - {my_alias}", chat_layout)


def popup_text(filename, text):

    layout = [
        [
            sg.Multiline(text, size=(80, 25)),
        ],
    ]
    win = sg.Window(filename, layout, modal=True, finalize=True)

    while True:
        event, values = win.read()
        if event == sg.WINDOW_CLOSED:
            break
    win.close()


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    print(event, values)
    if event == "-GETFRIENDS-":
        client_socket.send((protocols.REFRESH).encode("utf-8"))
        reply = client_socket.recv(BUFFER).decode("utf-8")
        # print(reply)
        reply_to_list = reply.split(";;")
        print(reply_to_list)
        to_be_tokenized = reply_to_list[1]  # all the users are in here
        # print(to_be_tokenized)
        raw_user_list = to_be_tokenized.split("__")
        if reply_to_list[0] == protocols.REFRESH_UPDATE:
            for user in raw_user_list:
                # print(user)
                # print(user.partition('@')[0])
                # if the users in the update is not in the global alias list
                # then we add it. Skip self
                if (
                    user.partition("@")[0] not in GLOBAL_ALIASES
                    and user != ""
                    and user.partition("@")[0] != my_alias
                ):
                    GLOBAL_ALIASES.append(user.partition("@")[0])
                    GLOBAL_LISTENERS.append(user.partition("@")[2])
            for alias in GLOBAL_ALIASES:
                if alias not in to_be_tokenized:
                    # print('uh oh')
                    index = GLOBAL_ALIASES.index(alias)
                    GLOBAL_ALIASES.remove(alias)
                    listener = GLOBAL_LISTENERS[index]
                    GLOBAL_LISTENERS.remove(listener)
        # print(global_aliases) #debug
        # print(global_listeners) #debug
        window.refresh()
        window["-ONLINEPEERS-"].update(values=GLOBAL_ALIASES)
        window["-ONLINECOUNT-"].update(
            "Looks like no one is online right now:("
            if len(GLOBAL_ALIASES) == 0
            else (f"{str(len(GLOBAL_ALIASES))} friend(s) online now! ^_^")
        )
    elif event == "-ONLINEPEERS-":
        # print(event)
        # print(values)
        selection = values[event]
        if selection:
            # print(selection[0])
            # get the alias to connect to
            alias_to_connect = selection[0]
            CURRENT_ALIAS = alias_to_connect
            # append that to list to track
            # ------
            # if alias_to_connect in FROM_OUTER_ALIASES:

            # TO_OUTER_ALIASES.append(alias_to_connect)
            index = GLOBAL_ALIASES.index(alias_to_connect)
            address_to_connect = GLOBAL_LISTENERS[index]
            # to_outer_connections.append(address_to_connect)
            # ------
            # print(outward_connected_aliases)
            # tuple_address = my_helper.get_address_from_string(address_to_connect)
            # if tuple_address in to_outer_connections:
            #    current_target_connection = tuple_address
            # print('here: ' + address_to_connect)
            # else:
            # to_outer_connections.append(tuple_address)
            # CURRENT_ALIAS = alias_to_connect
            if CURRENT_ALIAS not in CONVO_DICT:
                CONVO_DICT[CURRENT_ALIAS] = ""
            # (for debugging) print(f'[{CURRENT_ALIAS} to me]: '+ f'\n[{CURRENT_ALIAS} to me]: '.join(CONVO_DICT[CURRENT_ALIAS].split("<!>")))
            if CONVO_DICT[CURRENT_ALIAS] != "":
                window["-CHATOUTPUT-" + sg.WRITE_ONLY_KEY].update("")
                window["-CHATOUTPUT-" + sg.WRITE_ONLY_KEY].print(
                    f"\n".join(CONVO_DICT[CURRENT_ALIAS].split("<!>"))
                )

            window["-CURRENTALIAS-"].update(f"Now chatting with {alias_to_connect}")
            client_thread = threading.Thread(
                target=connect_to_others, args=(address_to_connect,), daemon=True
            )
            client_thread.start()
    elif event == "-SENDFILE-":
        # CONNECTION_DICTIONARY[CURRENT_ALIAS].send((protocols.FILETRANSBEGIN).encode('utf-8'))
        filename = values["-FILEBROWSENAMESHOW-"]
        CONNECTION_DICTIONARY[CURRENT_ALIAS].send(
            (protocols.PEERSEND + "__" + protocols.FILETRANSFER).encode("utf-8")
        )
        if Path(filename).is_file():
            try:
                with open(filename, "rb") as f:
                    filesize = os.path.getsize(filename)
                    # print(filesize)
                    base_filename = os.path.basename(filename)
                    sent_filename = f"received_{base_filename}"
                    filesend_msg = f"{my_alias} sent a file: {base_filename}"
                    CONVO_DICT[CURRENT_ALIAS] += filesend_msg + "<!>"
                    window["-CHATOUTPUT-" + sg.WRITE_ONLY_KEY].print(filesend_msg)
                    advertise_msg = protocols.PEERSEND + "__" + protocols.FILETRANSFER + "__" +protocols.ADVERTISEFILE + "__"+ sent_filename+ "__" + str(filesize)
                    CONNECTION_DICTIONARY[CURRENT_ALIAS].send(advertise_msg.encode('utf-8'))
                    print("[File send debug]", sent_filename)
                    data = f.read()
                    data_to_send = protocols.PEERSEND + '__' + protocols.FILETRANSFER + '__' + protocols.FILECONTENT + '__' + str(data)
                    CONNECTION_DICTIONARY[CURRENT_ALIAS].sendall(data_to_send.encode('utf-8'))
                    CONNECTION_DICTIONARY[CURRENT_ALIAS].send((protocols.PEERSEND + '__' + protocols.FILETRANSFER + '__' + protocols.FILETRANSEND).encode('utf-8'))
                    # CONNECTION_DICTIONARY[CURRENT_ALIAS].send((protocols.FILETRANSEND).encode('utf-8'))
                    # CONNECTION_DICTIONARY[CURRENT_ALIAS].send
                # popup_text(filename, text)
            except Exception as e:
                print("error", e)
    elif event == "-SENDBUTTON-":
        global query
        print(event, values)
        query = ""
        query = values["-QUERY-"].rstrip()
        # EXECUTE YOUR COMMAND HERE
        # print('[Nho] {}'.format(query), flush=True)
        # print(values["-QUERY-"].rstrip())
        query_to_print = f"[{my_alias}]: " + query
        CONVO_DICT[CURRENT_ALIAS] += query_to_print + "<!>"
        window["-CHATOUTPUT-" + sg.WRITE_ONLY_KEY].print(query_to_print)
        print("[DEBUG] after send event", CONNECTION_DICTIONARY[CURRENT_ALIAS])
        CONNECTION_DICTIONARY[CURRENT_ALIAS].send(
            (protocols.PEERSEND + "__" + query).encode("utf-8")
        )

    elif event == sg.WIN_CLOSED or event == "Log off":
        client_socket.send((protocols.DISCONNECT).encode("utf-8"))
        client_socket.close()
        break
window.close()
