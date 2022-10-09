# SE364 A2 Client
# Name: Matthew Jakeman
# UPI: mjak923
import sys
from socket import *

from message import MessageType, NicknameMessage, ListClientsMessage, ClientDataMessage
from socket_utils import send_message, wait_message


class Client:
    server_socket = None

    def __init__(self, address, port, nickname):
        # Set up client socket connection
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.connect((address, port))

        print('Connection established to src {}: {}'.format(address, port))

        nick_message = NicknameMessage(nickname)
        send_message(self.server_socket, nick_message)

    def dispatch_message(self, message):

        if message.message_type is MessageType.CLIENT_DATA:
            print(f"Discovered client: {message.nickname}")
            return

        print(f"Unsupported message: {message.message_type}")

    def run(self):

        list_clients_message = ListClientsMessage()
        send_message(self.server_socket, list_clients_message)

        try:
            while True:
                msg = wait_message(self.server_socket)
                self.dispatch_message(msg)

        finally:
            # Cleanup
            self.server_socket.close()


# Target src properties
server_name = 'localhost'
server_port = 12000

nickname = 'Default'

if len(sys.argv) > 1:
    nickname = sys.argv[1]

client = Client(server_name, server_port, nickname)
client.run()
