# SE364 A2 Client
# Name: Matthew Jakeman
# UPI: mjak923
import select
import ssl
import sys
from socket import *

from config import INVALID_ID, SERVER_HOST, SERVER_PORT, CERTFILE
from message import MessageType, NicknameMessage
from socket_utils import send_message, recv_message


class Client:
    server_socket = None
    client_id = INVALID_ID

    poller = None

    def __init__(self, address, port, nickname):
        # Create SSL Context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(CERTFILE)
        context.check_hostname = True

        # Wrap regular socket
        raw_socket = socket(AF_INET, SOCK_STREAM)
        raw_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket = context.wrap_socket(raw_socket, server_hostname=address)

        # Setup client socket connection
        self.server_socket.connect((address, port))

        self.poller = select.poll()
        self.poller.register(self.server_socket, select.POLLIN)

        print('Connection established to src {}: {}'.format(address, port))

        nick_message = NicknameMessage(nickname)
        send_message(self.server_socket, nick_message)

        ack_message = recv_message(self.server_socket)
        self.client_id = ack_message.client_id

        if self.client_id == INVALID_ID:
            raise Exception("Nickname is already taken")

    def poll(self, dispatch_func):
        # Poll socket for messages
        events = self.poller.poll(0)

        # Process messages
        for sock, event in events:
            if event and select.POLLIN:
                msg = recv_message(self.server_socket)
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
    print("Did you mean to run app.py?")
