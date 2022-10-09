# SE364 A2 Client
# Name: Matthew Jakeman
# UPI: mjak923

from socket import *

from message import parse_message, NicknameMessage, ListClientsMessage, ClientDataMessage

# Target src properties
server_name = 'localhost'
server_port = 12000


def dispatch_message(server_socket, raw_message_data):
    message = parse_message(raw_message_data)

    if message is ClientDataMessage:
        print(f"Discovered client: {message.nickname}")
        pass

    error(f"Unsupported message: {message.message_type}")


# Set up client socket connection
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_name, server_port))

print('Connection established to src {}: {}'.format(server_name, server_port))

nick_message = NicknameMessage("Matthew")
client_socket.send(nick_message.__str__().encode())

list_clients_message = ListClientsMessage()
client_socket.send(list_clients_message.__str__().encode())

try:
    print("Quitting")
    #while True:
        #data = client_socket.recv(1024)
        #dispatch_message(client_socket, data.decode())

finally:
    # Cleanup
    client_socket.close()
