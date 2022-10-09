# SE364 A2 Client
# Name: Matthew Jakeman
# UPI: mjak923
import sys
from socket import *

import config
from message import MessageType, NicknameMessage, ListClientsMessage, ClientDiscoveryMessage
from socket_utils import send_message, recv_message


class Client:
    server_socket = None
    client_id = -1

    def __init__(self, address, port, nickname):
        # Set up client socket connection
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.connect((address, port))

        print('Connection established to src {}: {}'.format(address, port))

        nick_message = NicknameMessage(nickname)
        send_message(self.server_socket, nick_message)

        ack_message = recv_message(self.server_socket)
        self.client_id = ack_message.client_id

        list_clients_message = ListClientsMessage()
        send_message(self.server_socket, list_clients_message)

        # Make socket non-blocking
        self.server_socket.setblocking(False)

    def poll(self, dispatch_func):
        try:
            msg = recv_message(self.server_socket)
            dispatch_func(self.server_socket, msg)
        except BlockingIOError:
            pass

    def __del__(self):
        # Cleanup
        self.server_socket.close()


def default_dispatch(server_socket, message):
    if message.message_type is MessageType.CLIENT_DISCOVERY:
        print(f"Discovered client: {message.nickname}")
        return

    print(f"Unsupported message: {message.message_type}")


if __name__ == '__main__':
    nickname = 'Default'

    if len(sys.argv) > 1:
        nickname = sys.argv[1]

    client = Client(config.SERVER_HOST, config.SERVER_PORT, nickname)
    try:
        while True:
            client.poll(default_dispatch)
    finally:
        client.__del__()
