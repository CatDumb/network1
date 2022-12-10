import socket
import threading
import protocols
import PySimpleGUI as sg


# setting up the peer's own listening socket (like a server)
# where other peers can connect to 
this_ip = socket.gethostbyname(socket.gethostname())
this_port = 19024
this_addr = (this_ip, this_port)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(this_addr)


def receive_message(conn):
    while True:
        client_message = conn.recv(1024).decode()
        print(client_message)


def send_message(conn):
    while True:
        message = input("Enter a message: ")
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


def handle_client(conn, addr):
    print(f"client {addr} connected.")
    sending_thread = threading.Thread(target=send_message, args=(conn,))
    receiving_thread = threading.Thread(target=receive_message, args=(conn,))
    sending_thread.start()
    receiving_thread.start()


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# sending_thread = threading.Thread(target=send_message, args=(client_socket,))
# receiving_thread = threading.Thread(target=receive_message, args=(client_socket,))
# sending_thread.start()
# receiving_thread.start()


sg.theme("SandyBeach")
# PySimpleGUI uses camelCase, not pep8 like_this
# we'll try our best to not make mistakes!


# GUI to get server IP and port
central_ip = sg.popup_get_text("Enter server IP", "Welcome to Chatatouille - IP")
central_port = sg.popup_get_text("Enter server port", "Welcome to Chatatouille - Port")


# connect after getting ip and port
client_socket.connect((central_ip, int(central_port)))

# GUI to get chat alias
alias = sg.popup_get_text("Please enter your name", "Welcome to Chatatouille - Name")

status = do_login(alias)
onlinePeersLayout = [
    [sg.Text(status)],
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
    [sg.Text(key="receiver")],
    [
        sg.Listbox(
            values=["[binh]: Hello", "[nguyen]: Hi"],
            expand_x=True,
            size=(0, 15),
            key="chat_box",
            no_scrollbar=True,
        )
    ],
    [sg.Button("Upload"), sg.Input(), sg.Button("Send")],
]

chat_layout = [
    [
        sg.Column(message_layout, key="right_col"),
        sg.Column(
            onlinePeersLayout, element_justification="c", key="left_col", pad=(20, 20)
        ),
    ]
]

window = sg.Window(f"Chatatouille - {alias}", chat_layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == "Refresh":
        client_socket.send((protocols.REFRESH).encode('utf-8'))
    if (
        event == sg.WIN_CLOSED or event == "Logout"
    ):  # if user closes window or clicks cancel
        client_socket.send((protocols.DISCONNECT).encode('utf-8'))
        client_socket.close()
        break
    print("You entered ", values[0])
window.close()
