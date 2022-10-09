# SE364 A2 Server
# Name: Matthew Jakeman
# UPI: mjak923

from socket import *
from threading import Thread

from message import parse_message, Message, MessageType, NicknameMessage, ListClientsMessage

# Server properties
server_host = ''
server_port = 12000

# Start up src and listen
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((server_host, server_port))
server_socket.listen()

print("Server started listening localhost: {}".format(server_port))

connected_clients = {}


class ClientData:
    client_nick = None
    client_id = None

    def __init__(self, client_id, client_nick):
        self.client_nick = client_nick
        self.client_id = client_id


def broadcast(message):
    assert message is Message

    print(f"BROADCAST: {message.__str__()}")
    for client in connected_clients:
        client.send(message.__str__().encode())


def get_client_data(client_socket):
    return connected_clients[client_socket]


def dispatch_message(client_socket, raw_message_data):
    message = parse_message(raw_message_data)

    if message is ListClientsMessage:
        for other_client in connected_clients:
            if other_client is not client_socket:
                client_data = get_client_data(other_client)
                client_socket.send(client_data.client_nick.encode())
        pass

    error(f"Unsupported message: {message.message_type}")


def terminate_client(client_socket):
    try:
        # Remove from connected clients
        client_data = connected_clients[client_socket]
        connected_clients.pop(client_socket)

        # Broadcast disconnection message
        print(f"STATUS: Client at {client_data.client_id} with nickname '{client_data.client_nick}' disconnected")
    finally:
        client_socket.close()


def client_listener(client_socket):
    while True:
        # Continually receive from client until termination
        try:
            data = client_socket.recv(1024)
            dispatch_message(client_socket, data.decode())
        except:
            terminate_client(client_socket)
            return


def register_client(client_socket):
    # Get unique id (server, port) for socket
    socket_id = client_socket.getpeername()
    print(f"STATUS: Incoming connection from {socket_id}")

    # Get nickname from client
    data = client_socket.recv(1024).decode()
    nick_message = parse_message(data)

    if nick_message is not NicknameMessage:
        error("ERROR: Client socket did not provide nickname - quitting")
        client_socket.close()
        pass

    # Add client connection to list
    client_data = ClientData(socket_id, nick_message.nickname)
    connected_clients[client_socket] = client_data
    print(f"STATUS: {client_data.client_nick} connected to the server")

    # Dispatch new thread with listener function
    thread = Thread(target=client_listener, args=(client_socket,))
    thread.daemon = True
    thread.start()


try:
    while True:
        # Wait for connection
        incoming_client, _ = server_socket.accept()
        register_client(incoming_client)
except KeyboardInterrupt:
    print("Shutting down...")
finally:
    server_socket.close()
