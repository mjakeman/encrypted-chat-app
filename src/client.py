# SE364 A2 Client
# Name: Matthew Jakeman
# UPI: mjak923

from socket import *

from message import NicknameMessage

# Target src properties
server_name = 'localhost'
server_port = 12000

# Set up client socket connection
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_name, server_port))

print('Connection established to src {}: {}'.format(server_name, server_port))

nick_message = NicknameMessage("Matthew")
client_socket.send(nick_message.__str__().encode())

# Cleanup
client_socket.close()