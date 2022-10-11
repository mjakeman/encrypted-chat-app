# Qt GUI (Main Window)
# Name: Matthew Jakeman
# UPI: mjak923
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QHBoxLayout, QPushButton, QApplication

from app_state import AppState
from app_thread import ClientThread
from app_view_chat import RoomView
from app_view_main import MainView
from client import Client
from message import ListClientsMessage, ListRoomsMessage


class ChatWindow(QWidget):

    main_view = None
    stack = None

    back_btn = None
    quit_btn = None

    app_state = None
    connect_window = None

    def __init__(self, connect_window, address, port, nickname):
        super().__init__()

        # Store a reference to the connection window
        self.connect_window = connect_window

        # Setup Client
        client = Client(address, port, nickname)
        client_id = client.client_id
        client_thread = ClientThread(client)
        client_thread.start()

        # Setup State
        self.app_state = AppState(client_thread, client_id)
        self.app_state.client_thread.discovered_client.connect(self.on_discover_client)
        self.app_state.client_thread.discovered_room.connect(self.on_discover_room)

        # Construct UI
        self.construct_ui()
        self.setWindowTitle(f"{nickname}'s Conversations")

        # Send startup messages
        list_clients_message = ListClientsMessage()
        list_rooms_message = ListRoomsMessage()
        client_thread.queue_message(list_clients_message)
        client_thread.queue_message(list_rooms_message)

    def on_discover_client(self, user_id, nickname):
        self.app_state.add_known_client(user_id, nickname)
        pass

    def on_discover_room(self, room_id, room_title, host_id, host_name):
        self.app_state.add_known_room(room_id, room_title, host_id, host_name)
        pass

    def construct_ui(self):
        vbox = QVBoxLayout()

        self.main_view = self.construct_main_ui()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.main_view)
        self.stack.setCurrentWidget(self.main_view)
        vbox.addWidget(self.stack)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        # Add Back Button
        self.back_btn = QPushButton("Back")
        self.back_btn.setEnabled(False)
        self.back_btn.clicked.connect(self.return_home)
        hbox.addWidget(self.back_btn)

        # Add Quit Button
        self.quit_btn = QPushButton("Logout")
        self.quit_btn.clicked.connect(self.logout)
        hbox.addWidget(self.quit_btn)

        self.setLayout(vbox)

    def logout(self):
        self.connect_window.setVisible(True)
        self.close()

    def construct_main_ui(self):
        return MainView(self, self.app_state)

    def construct_room_ui(self, room_id, title):
        return RoomView(self, self.app_state, room_id, title, True)

    def construct_direct_chat_ui(self, room_id, title):
        return RoomView(self, self.app_state, room_id, title, False)

    def show_direct_chat(self, user_id, room_id, user_name):
        room_view = self.construct_direct_chat_ui(room_id, f"Chatting with {user_name}")
        self.stack.addWidget(room_view)
        self.stack.setCurrentWidget(room_view)

        self.back_btn.setEnabled(True)

    def show_room(self, room_id):
        room_view = self.construct_room_ui(room_id, self.app_state.get_known_room_name(room_id))
        self.stack.addWidget(room_view)
        self.stack.setCurrentWidget(room_view)

        self.back_btn.setEnabled(True)

    def return_home(self):
        current = self.stack.currentWidget()
        while current is not self.main_view:
            self.stack.removeWidget(current)
            current = self.stack.currentWidget()

        self.back_btn.setEnabled(False)
