# SE364 A2 Server
# Name: Matthew Jakeman
# UPI: mjak923

from socket import *
from threading import Thread
from traceback import print_exception

from message import *
from socket_utils import recv_message, send_message

import config


class ClientData:
    client_nick = None
    client_id = None

    def __init__(self, client_id):
        self.client_id = client_id


class Room:
    authorized_clients = None
    title = None
    host_id = None
    room_id = None

    def __init__(self, room_id, title, host_id):
        self.room_id = room_id
        self.title = title
        self.host_id = host_id
        self.authorized_clients = {host_id}

    def invite(self, client_id):
        self.authorized_clients.add(client_id)


class Server:
    connected_clients = {}
    server_socket = None

    server_rooms = []

    next_user_id = 0
    next_room_id = 0

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
        print(f"BROADCAST: {message.message_type.name}: {message.__str__()}")
        for client in self.connected_clients:
            send_message(client, message)

    def get_client_data(self, client_socket):
        return self.connected_clients[client_socket]

    def dispatch_message(self, client_socket, message):
        client_data = self.get_client_data(client_socket)

        if message.message_type is MessageType.LIST_CLIENTS:
            for client in self.connected_clients:
                other_client_data = self.get_client_data(client)

                new_msg = ClientDiscoveryMessage(other_client_data.client_id, other_client_data.client_nick)
                send_message(client_socket, new_msg)
            return

        if message.message_type is MessageType.LIST_ROOMS:
            for room in self.server_rooms:
                if client_data.client_id in room.authorized_clients:
                    new_msg = RoomDiscoveryMessage(room.title)
                    send_message(client_socket, new_msg)
            return

        if message.message_type is MessageType.ROOM_CREATE:
            if message.host_id is not client_data.client_id:
                print("Not authorised to create room")
                return

            new_room = Room(self.next_room_id, message.host_id, message.title)
            self.server_rooms.append(new_room)

            self.next_room_id += 1

            new_msg = AcknowledgeRoomCreateMessage(new_room.room_id)
            send_message(client_socket, new_msg)
            return

        if message.message_type is MessageType.ROOM_INVITE:
            for room in self.server_rooms:
                if room.room_id is message.room_id:
                    room.invite(message.client_id)

                    # TODO: Notify
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
                msg = recv_message(client_socket)
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
        nick_message = recv_message(client_socket)

        if not isinstance(nick_message, NicknameMessage):
            error("ERROR: Client socket did not provide nickname - quitting")
            client_socket.close()
            return

        # TODO: Ensure nickname is unique

        # Create new client id
        client_data = ClientData(self.next_user_id)
        self.next_user_id += 1

        client_data.client_nick = nick_message.nickname

        # Acknowledge client and assign id
        ack_message = AcknowledgeClientMessage(client_data.client_id)
        send_message(client_socket, ack_message)

        # Broadcast client discovery message
        # This must be done before adding the current client to the connection list
        self.broadcast(ClientDiscoveryMessage(client_data.client_id, client_data.client_nick))

        # Add client connection to list
        self.connected_clients[client_socket] = client_data
        print(f"STATUS: {client_data.client_nick} connected to the server")

        # Dispatch new thread with listener function
        thread = Thread(target=self.client_listener, args=(client_socket,))
        thread.daemon = True
        thread.start()


if __name__ == '__main__':
    # Server properties
    server = Server(config.SERVER_HOST, config.SERVER_PORT)
    server.run()
