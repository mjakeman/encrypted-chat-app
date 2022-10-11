# SE364 A2 Client
# Name: Matthew Jakeman
# UPI: mjak923

import sys
from socket import *

from config import INVALID_ID, SERVER_HOST, SERVER_PORT
from message import MessageType, NicknameMessage
from socket_utils import send_message, recv_message


class Client:
    server_socket = None
    client_id = INVALID_ID

    def __init__(self, address, port, nickname):
        # Set up client socket connection
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.connect((address, port))

        print('Connection established to src {}: {}'.format(address, port))

        nick_message = NicknameMessage(nickname)
        send_message(self.server_socket, nick_message)

        ack_message = recv_message(self.server_socket)
        self.client_id = ack_message.client_id

    def poll(self, dispatch_func):

        msg = None

        # Make socket non-blocking
        self.server_socket.setblocking(False)

        # Attempt to receive message
        try:
            msg = recv_message(self.server_socket)
        except BlockingIOError:
            pass

        # Make socket blocking
        self.server_socket.setblocking(True)

        if msg is not None:
            dispatch_func(self.server_socket, msg)

    def send_message(self, message):
        send_message(self.server_socket, message)

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

    client = Client(SERVER_HOST, SERVER_PORT, nickname)
    try:
        while True:
            client.poll(default_dispatch)
    finally:
        client.__del__()
