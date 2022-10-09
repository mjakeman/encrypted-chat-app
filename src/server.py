# SE364 A2 Server
# Name: Matthew Jakeman
# UPI: mjak923

from socket import *
from threading import Thread
from traceback import print_exception

from message import Message, NicknameMessage, ListClientsMessage, ClientDataMessage
from socket_utils import wait_message, send_message


class ClientData:
    client_nick = None
    client_id = None

    def __init__(self, client_id, client_nick):
        self.client_nick = client_nick
        self.client_id = client_id


class Server:
    connected_clients = {}
    server_socket = None

    def __init__(self, host, port):
        # Start up src and listen
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()

        print("Server started listening localhost: {}".format(port))

    def run(self):
        try:
            while True:
                # Wait for connection
                incoming_client, _ = self.server_socket.accept()
                self.register_client(incoming_client)
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.server_socket.close()

    def broadcast(self, message):
        assert message is Message

        print(f"BROADCAST: {message.__str__()}")
        for client in self.connected_clients:
            send_message(client, message)

    def get_client_data(self, client_socket):
        return self.connected_clients[client_socket]

    def dispatch_message(self, client_socket, message):
        if message is ListClientsMessage:
            for other_client in self.connected_clients:
                if other_client is not client_socket:
                    client_data = self.get_client_data(other_client)

                    new_msg = ClientDataMessage(client_data.client_nick)
                    send_message(client_socket, new_msg)
            return

        print(f"Unsupported message: {message.message_type.name}")

    def terminate_client(self, client_socket):
        try:
            # Remove from connected clients
            client_data = self.connected_clients[client_socket]
            self.connected_clients.pop(client_socket)

            # Broadcast disconnection message
            print(f"STATUS: Client at {client_data.client_id} with nickname '{client_data.client_nick}' disconnected")
        finally:
            client_socket.close()

    def client_listener(self, client_socket):
        while True:
            # Continually receive from client until termination
            try:
                msg = wait_message(client_socket)
                if msg is None:
                    self.terminate_client(client_socket)
                    return

                self.dispatch_message(client_socket, msg)
            except Exception as e:
                print_exception(e)
                self.terminate_client(client_socket)
                return

    def register_client(self, client_socket):
        # Get unique id (server, port) for socket
        socket_id = client_socket.getpeername()
        print(f"STATUS: Incoming connection from {socket_id}")

        # Get nickname from client
        nick_message = wait_message(client_socket)

        if not isinstance(nick_message, NicknameMessage):
            error("ERROR: Client socket did not provide nickname - quitting")
            client_socket.close()
            return

        # Add client connection to list
        client_data = ClientData(socket_id, nick_message.nickname)
        self.connected_clients[client_socket] = client_data
        print(f"STATUS: {client_data.client_nick} connected to the server")

        # Dispatch new thread with listener function
        thread = Thread(target=self.client_listener, args=(client_socket,))
        thread.daemon = True
        thread.start()


# Server properties
server_host = ''
server_port = 12000

server = Server(server_host, server_port)
server.run()
