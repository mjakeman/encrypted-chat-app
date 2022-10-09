# SE364 A2 Client
# Name: Matthew Jakeman
# UPI: mjak923

from socket import *

from message import parse_message, NicknameMessage, ListClientsMessage, ClientDataMessage
from socket_utils import send_message, wait_message

# Target src properties
server_name = 'localhost'
server_port = 12000


def dispatch_message(server_socket, message):

    if message is ClientDataMessage:
        print(f"Discovered client: {message.nickname}")
        pass

    print(f"Unsupported message: {message.message_type}")


# Set up client socket connection
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_name, server_port))

print('Connection established to src {}: {}'.format(server_name, server_port))

nick_message = NicknameMessage("Matthew")
send_message(client_socket, nick_message)

list_clients_message = ListClientsMessage()
send_message(client_socket, list_clients_message)

try:
    while True:
        msg = wait_message(client_socket)
        dispatch_message(client_socket, msg)

finally:
    # Cleanup
    client_socket.close()
