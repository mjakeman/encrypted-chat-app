# SE364 A2 Server
# Name: Matthew Jakeman
# UPI: mjak923

import os
import socket
import ssl
import traceback

from socket import *
from threading import Thread
from traceback import print_exception

from message import *
from server_client import ClientData
from server_room import RoomMessage, Room
from socket_utils import recv_message, send_message

from config import INVALID_ID, SERVER_PORT, SERVER_HOST, DIRECT_CHAT_ROOM_ID, RESOURCE_LOCATION, CERTFILE, KEYFILE


class Server:
    connected_clients = {}
    server_socket = None

    server_rooms = []
    images = []

    next_user_id = 0
    next_room_id = 0
    next_resource_id = 0

    def __init__(self, host, port):
        # Create SSL Context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

        # Setup certificate and shared ciphers
        context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)
        context.load_verify_locations(CERTFILE)

        # Wrap regular socket
        raw_socket = socket(AF_INET, SOCK_STREAM)
        raw_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket = context.wrap_socket(raw_socket, server_side=True)

        # Start up src and listen
        self.server_socket.bind((host, port))
        self.server_socket.listen()

        print("Server started listening localhost: {}".format(port))

    def run(self):
        try:
            while True:
                try:
                    # Wait for connection
                    incoming_client, _ = self.server_socket.accept()
                    self.register_client(incoming_client)
                except Exception as e:
                    traceback.print_exception(e)
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.server_socket.close()

    def ensure_resource_dir(self):
        if not os.path.exists(RESOURCE_LOCATION):
            os.mkdir(RESOURCE_LOCATION)

    def get_resource(self, resource_id):
        self.ensure_resource_dir()
        resource_name = os.path.join(RESOURCE_LOCATION, f"{resource_id}.png")

        with open(resource_name, "rb") as image:
            file = image.read()
            return bytearray(file)

    def create_resource(self, data):
        resource_id = self.next_resource_id
        self.next_resource_id += 1

        self.ensure_resource_dir()
        resource_name = os.path.join(RESOURCE_LOCATION, f"{resource_id}.png")

        with open(resource_name, "wb") as image:
            image.write(data)
            return resource_id

    def broadcast(self, message):
        print(f"BROADCAST: {message.message_type.name}: {message.__str__()}")
        for client in self.connected_clients:
            send_message(client, message)

    def get_client_data(self, client_socket):
        return self.connected_clients[client_socket]

    def get_client_data_for_id(self, client_id):
        for client in self.connected_clients:
            if self.connected_clients[client].client_id is client_id:
                return self.connected_clients[client]

        return None

    def get_client_socket_for_id(self, client_id):
        for client in self.connected_clients:
            if self.connected_clients[client].client_id is client_id:
                return client

        return None

    def create_room(self, title, host_id):
        new_room = Room(self.next_room_id, title, host_id)
        self.server_rooms.append(new_room)

        self.next_room_id += 1

        return new_room

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
                if room.host_id is DIRECT_CHAT_ROOM_ID:
                    continue

                if client_data.client_id in room.authorized_clients:
                    owner_name = self.get_client_data_for_id(room.host_id).client_nick
                    new_msg = RoomDiscoveryMessage(room.room_id, room.title, room.host_id, owner_name)
                    send_message(client_socket, new_msg)
            return

        if message.message_type is MessageType.LIST_ROOM_MEMBERS:
            room = self.server_rooms[message.room_id]

            new_msg = RoomMembershipDiscoveryMessage(room.host_id, room.authorized_clients)
            send_message(client_socket, new_msg)

        if message.message_type is MessageType.ROOM_CREATE:
            if message.host_id is not client_data.client_id:
                print("Not authorised to create room")
                return

            new_room = self.create_room(message.title, message.host_id)
            new_msg = AcknowledgeRoomCreateMessage(new_room.room_id)
            send_message(client_socket, new_msg)
            return

        if message.message_type is MessageType.ROOM_INVITE:

            for room in self.server_rooms:
                if room.room_id is message.room_id:

                    # Only host can invite people
                    if room.host_id is not client_data.client_id:
                        return

                    room.invite(message.client_id)

                    owner_name = self.get_client_data_for_id(room.host_id).client_nick
                    new_msg = RoomDiscoveryMessage(room.room_id, room.title, room.host_id, owner_name)
                    send_message(self.get_client_socket_for_id(message.client_id), new_msg)

                    for client_id in room.authorized_clients:
                        dest_socket = self.get_client_socket_for_id(client_id)
                        new_msg = RoomMembershipDiscoveryMessage(room.host_id, room.authorized_clients)
                        send_message(dest_socket, new_msg)
            return

        if message.message_type is MessageType.INITIATE_USER_CHAT:
            other_user_data = self.get_client_data_for_id(message.user_id)

            if client_data.user_room_map.get(message.user_id) is None:
                new_room = self.create_room("Direct Chat", DIRECT_CHAT_ROOM_ID)
                room_id = new_room.room_id

                # Invite both users
                new_room.invite(client_data.client_id)
                new_room.invite(message.user_id)

                # Set room in user room maps
                client_data.user_room_map[message.user_id] = room_id
                other_user_data.user_room_map[client_data.client_id] = room_id
            else:
                room_id = client_data.user_room_map[message.user_id]

            new_msg = AcknowledgeUserChatMessage(room_id, other_user_data.client_id, other_user_data.client_nick)
            send_message(client_socket, new_msg)
            return

        if message.message_type is MessageType.ROOM_MESSAGE_SEND:
            text = message.text
            timestamp = message.timestamp
            room_id = message.room_id

            room = self.server_rooms[room_id]
            msg = RoomMessage(text, timestamp)

            # Add resource if relevant
            if message.resource_id is not INVALID_ID:
                msg.add_resource(message.resource_id)

            room.send_message(msg)

            new_msg = RoomEntryBroadcastMessage(room_id, text, timestamp, client_data.client_id, message.resource_id)

            # Send a message to all authorised clients
            for member_id in room.authorized_clients:
                member_socket = self.get_client_socket_for_id(member_id)
                send_message(member_socket, new_msg)

            return

        if message.message_type == MessageType.RESOURCE_CREATE:
            resource_id = self.create_resource(message.data)

            new_msg = AcknowledgeResourceMessage(resource_id)
            send_message(client_socket, new_msg)
            return

        if message.message_type == MessageType.RESOURCE_FETCH:
            data = self.get_resource(message.resource_id)

            new_msg = ResourceTransferMessage(data)
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

        for cmp in self.connected_clients:
            test_nick = self.connected_clients[cmp].client_nick
            if nick_message.nickname == test_nick:
                ack_message = AcknowledgeClientMessage(INVALID_ID)
                send_message(client_socket, ack_message)
                return

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
    server = Server(SERVER_HOST, SERVER_PORT)
    server.run()
