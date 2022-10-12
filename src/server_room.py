# Server Room Data
# Name: Matthew Jakeman
# UPI: mjak923

from config import INVALID_ID
from server import DIRECT_CHAT_ROOM_ID


class RoomMessage:
    text = None
    timestamp = None
    resource_id = INVALID_ID

    def __init__(self, text, timestamp):
        self.text = text
        self.timestamp = timestamp

    def add_resource(self, resource_id):
        self.resource_id = resource_id


class Room:
    authorized_clients = None
    title = None
    host_id = None
    room_id = None

    messages = []

    def __init__(self, room_id, title, host_id):
        self.room_id = room_id
        self.title = title
        self.host_id = host_id

        self.authorized_clients = set()

        # Direct chats do not have a host (host_id = DIRECT_CHAT_ROOM_ID)
        if host_id != DIRECT_CHAT_ROOM_ID:
            self.authorized_clients.add(host_id)

    def invite(self, client_id):
        # Reject invalid client IDs
        if client_id >= 0:
            self.authorized_clients.add(client_id)

    def send_message(self, room_message):
        self.messages.append(room_message)
