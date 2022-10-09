# SE364 A2 Server
# Name: Matthew Jakeman
# UPI: mjak923

from socket import *
from threading import Thread

# Server properties
server_host = ''
server_port = 12000

# Start up src and listen
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((server_host, server_port))
server_socket.listen()

print("Server started listening localhost: {}".format(server_port))

connected_clients = {}


def broadcast(message):
    print(f"BROADCAST: {message}")
    for client in connected_clients:
        client.send(message.encode())


def terminate_client(client_socket):
    try:
        # Remove from connected clients
        socket_id = connected_clients[client_socket]
        connected_clients.pop(client_socket)

        # Broadcast disconnection message
        broadcast(f"Client {socket_id} disconnected")
    finally:
        client_socket.close()


def client_listener(client_socket):
    while True:
        # Continually receive from client until termination
        try:
            data = client_socket.recv(1024)
        except:
            terminate_client(client_socket)
            return


def register_client(client_socket):
    # Get unique id (server, port) for socket
    socket_id = client_socket.getpeername()

    # Add client connection to list
    connected_clients[client_socket] = socket_id
    broadcast(f"Client {socket_id} connected")

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
