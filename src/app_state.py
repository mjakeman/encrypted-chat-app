# Qt GUI (App State)
# Name: Matthew Jakeman
# UPI: mjak923

from PyQt5.QtGui import QStandardItemModel, QStandardItem

from config import INVALID_ID


class AppState:
    clients = {}
    rooms = {}

    clients_model = QStandardItemModel()
    rooms_model = QStandardItemModel()

    client_thread = None
    client_id = INVALID_ID

    def __init__(self, client_thread, client_id):
        self.client_thread = client_thread
        self.client_id = client_id

    def add_known_client(self, client_id, client_nick):
        if self.clients.__contains__(client_id):
            return

        print(f"Adding client: {client_id}, {client_nick}")
        item = QStandardItem(client_nick)
        item.setData(client_id)
        self.clients_model.appendRow(item)

        self.clients[client_id] = client_nick

    def add_known_room(self, room_id, room_title):
        if self.rooms.__contains__(room_id):
            return

        print(f"Adding room: {room_id}, {room_title}")
        item = QStandardItem(room_title)
        item.setData(room_id)
        self.rooms_model.appendRow(item)

        self.rooms[room_id] = room_title

    def get_known_client_name(self, client_id):
        return self.clients[client_id]

    def get_known_room_name(self, room_id):
        return self.rooms[room_id]