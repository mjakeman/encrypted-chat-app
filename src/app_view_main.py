# Qt GUI (Main View)
# Name: Matthew Jakeman
# UPI: mjak923

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QListView, QPushButton

from app_dialog_create_room import CreateRoomDialog
from message import RoomCreateMessage, InitiateUserChat, ListRoomsMessage


class MainView(QWidget):
    app_state = None
    chat_window = None

    users_list = None
    rooms_list = None

    def __init__(self, parent, app_state):
        super(MainView, self).__init__()

        self.chat_window = parent
        self.app_state = app_state

        # Connect signals
        self.app_state.client_thread.created_room.connect(self.on_create_room)
        self.app_state.client_thread.started_chat.connect(self.on_start_chat)

        self.construct_ui()

    def on_start_chat(self, user_id, room_id, nickname):
        self.chat_window.show_direct_chat(user_id, room_id, nickname)

    def on_create_room(self, room_id):
        new_msg = ListRoomsMessage()
        self.app_state.client_thread.queue_message(new_msg)

        self.chat_window.show_room(room_id)

    def construct_ui(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        # Create Users Section
        users_group = QGroupBox("Users")
        users_vbox = QVBoxLayout()

        # List of currently logged-in users
        self.users_list = QListView()
        self.users_list.setModel(self.app_state.clients_model)
        users_vbox.addWidget(self.users_list)

        # Chat button for users
        users_chat_btn = QPushButton("Chat")
        users_chat_btn.clicked.connect(self.initiate_direct_chat)
        users_vbox.addWidget(users_chat_btn)

        users_group.setLayout(users_vbox)
        hbox.addWidget(users_group)

        # Create Rooms Section
        rooms_group = QGroupBox("Rooms")
        rooms_vbox = QVBoxLayout()

        # List of rooms
        self.rooms_list = QListView()
        self.rooms_list.setModel(self.app_state.rooms_model)
        rooms_vbox.addWidget(self.rooms_list)

        # Chat button for rooms
        rooms_chat_btn = QPushButton("Join")
        rooms_chat_btn.clicked.connect(self.show_room)
        rooms_vbox.addWidget(rooms_chat_btn)

        # Create button for rooms
        rooms_create_btn = QPushButton("Create")
        rooms_create_btn.clicked.connect(self.show_create_room_dialog)
        rooms_vbox.addWidget(rooms_create_btn)

        rooms_group.setLayout(rooms_vbox)
        hbox.addWidget(rooms_group)

        self.setLayout(vbox)

    def show_create_room_dialog(self):
        dlg = CreateRoomDialog(self)
        dlg.setModal(True)

        # On success
        if dlg.exec():
            new_msg = RoomCreateMessage(self.app_state.client_id, dlg.title_text())
            self.app_state.client_thread.queue_message(new_msg)

    def initiate_direct_chat(self):
        try:
            index = self.users_list.currentIndex()
            item = self.app_state.clients_model.itemFromIndex(index)

            user_id = item.data()

            if user_id is not None:
                new_msg = InitiateUserChat(user_id)
                self.app_state.client_thread.queue_message(new_msg)
        except:
            pass

    def show_room(self):
        try:
            index = self.rooms_list.currentIndex()
            item = self.app_state.rooms_model.itemFromIndex(index)

            room_id = item.data()
            self.chat_window.show_room(room_id)
        except:
            pass