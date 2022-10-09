# Qt GUI
# Name: Matthew Jakeman
# UPI: mjak923
import queue
import sys
import traceback

from PyQt5.QtCore import QTimer, QThread, QObject, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGroupBox,
                             QMessageBox, QListView, QDialog, QDialogButtonBox, QStackedWidget, QGridLayout,
                             QScrollArea)

from client import Client
from message import MessageType, RoomCreateMessage, ListRoomsMessage, ListClientsMessage, InitiateUserChat


class ClientThread(QThread):
    client = None
    queue = None

    discovered_client = pyqtSignal(int, str)
    discovered_room = pyqtSignal(int, str)
    created_room = pyqtSignal(int)
    started_chat = pyqtSignal(int, int, str)

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.queue = queue.Queue()

    def dispatch(self, server_socket, message):
        if message.message_type is MessageType.CLIENT_DISCOVERY:
            print(f"Discovered client: {message.nickname}")
            self.discovered_client.emit(message.client_id, message.nickname)
            return

        if message.message_type is MessageType.ROOM_DISCOVERY:
            print(f"Discovered room: {message.title}")
            self.discovered_room.emit(message.room_id, message.title)
            return

        if message.message_type is MessageType.ACKNOWLEDGE_ROOM_CREATE:
            print(f"Ack'd room creation: {message.room_id}")
            self.created_room.emit(message.room_id)
            return

        if message.message_type is MessageType.ACKNOWLEDGE_USER_CHAT:
            print(f"Ack'd user chat: {message.room_id}")
            self.started_chat.emit(message.user_id, message.room_id, message.user_nick)
            return

        print(f"Unsupported message: {message.message_type}")

    def run(self):
        while True:
            # Poll for incoming messages
            self.client.poll(self.dispatch)

            # Send all queued messages
            while not self.queue.empty():
                message = self.queue.get()
                self.client.send_message(message)

    def queue_message(self, message):
        self.queue.put(message)


class CreateRoomDialog(QDialog):
    title = None

    def __init__(self, parent):
        super(CreateRoomDialog, self).__init__(parent)
        self.construct_ui()

    def construct_ui(self):
        self.setWindowTitle("Create Room")

        vbox = QVBoxLayout()

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.title = QLineEdit()
        vbox.addWidget(self.title)
        vbox.addWidget(button_box)

        self.setLayout(vbox)

    def title_text(self):
        return self.title.text()


class RoomView(QWidget):
    room_id = None
    title = None

    client_id = None
    client_thread = None

    chat_window = None

    participants = None
    chat_vbox = None
    message_entry = None

    should_show_participants = None

    def __init__(self, parent, client_id, client_thread, room_id, title, should_show_participants=False):
        super(RoomView, self).__init__()

        self.room_id = room_id
        self.title = title

        self.client_id = client_id
        self.client_thread = client_thread

        self.chat_window = parent
        self.should_show_participants = should_show_participants

        self.construct_ui()

    def construct_ui(self):
        # (0,0) Label
        grid = QGridLayout()
        grid.addWidget(QLabel(self.title), 0, 0)

        # (1,0) Chat Messages
        self.chat_vbox = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setLayout(self.chat_vbox)
        grid.addWidget(scroll_area, 1, 0)

        # (2,0) Entry and Send Buttons
        hbox = QHBoxLayout()
        self.message_entry = QLineEdit()
        hbox.addWidget(self.message_entry)

        send_message_btn = QPushButton("Send")
        hbox.addWidget(send_message_btn)

        send_image_btn = QPushButton("Attach")
        hbox.addWidget(send_image_btn)

        grid.addLayout(hbox, 2, 0)

        if self.should_show_participants:
            # (0,1) Label
            grid.addWidget(QLabel("Members"), 0, 1)

            # (1,1) Room Members
            self.participants = QListView()
            grid.addWidget(self.participants, 1, 1)

            # (2,1) Invite Button
            invite_btn = QPushButton("Invite")
            grid.addWidget(invite_btn, 2, 1)

        self.setLayout(grid)


class MainView(QWidget):
    client_thread = None
    client_id = -1

    users_model = None
    users_list = None

    rooms_model = None
    rooms_list = None

    chat_window = None

    def __init__(self, parent, client_id, client_thread):
        super(MainView, self).__init__()

        # Create Models
        self.users_model = QStandardItemModel()
        self.rooms_model = QStandardItemModel()

        self.chat_window = parent

        self.client_id = client_id
        self.client_thread = client_thread

        # Connect signals
        self.client_thread.discovered_client.connect(self.on_discover_client)
        self.client_thread.discovered_room.connect(self.on_discover_room)
        self.client_thread.created_room.connect(self.on_create_room)
        self.client_thread.started_chat.connect(self.on_start_chat)

        self.construct_ui()

    def on_discover_client(self, user_id, nickname):
        row = QStandardItem(nickname)
        row.setData(user_id)
        self.users_model.appendRow(row)
        pass

    def on_discover_room(self, room_id, room_title):
        row = QStandardItem(room_title)
        row.setData(room_id)
        self.rooms_model.appendRow(row)
        pass

    def on_start_chat(self, user_id, room_id, nickname):
        self.chat_window.show_direct_chat(user_id, room_id, nickname)

    def on_create_room(self, room_id):
        # TODO: Open created room immediately
        self.rooms_model.clear()
        new_msg = ListRoomsMessage()
        self.client_thread.queue_message(new_msg)

    def construct_ui(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        # Create Users Section
        users_group = QGroupBox("Users")
        users_vbox = QVBoxLayout()

        # List of currently logged-in users
        self.users_list = QListView()
        self.users_list.setModel(self.users_model)
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
        self.rooms_list.setModel(self.rooms_model)
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
            new_msg = RoomCreateMessage(self.client_id, dlg.title_text())
            self.client_thread.queue_message(new_msg)

    def initiate_direct_chat(self):
        try:
            index = self.users_list.currentIndex()
            item = self.users_model.itemFromIndex(index)

            user_id = item.data()

            if user_id is not None:
                new_msg = InitiateUserChat(user_id)
                self.client_thread.queue_message(new_msg)
        except:
            pass

    def show_room(self):
        try:
            index = self.rooms_list.currentIndex()
            item = self.rooms_model.itemFromIndex(index)

            room_id = item.data()
            self.chat_window.show_room(room_id)
        except:
            pass


class ChatWindow(QWidget):
    client_thread = None
    client_id = -1

    main_view = None
    stack = None

    back_btn = None
    quit_btn = None

    def __init__(self, address, port, nickname):
        super().__init__()

        # Setup Client
        client = Client(address, port, nickname)
        self.client_id = client.client_id
        self.client_thread = ClientThread(client)
        self.client_thread.start()

        self.construct_ui()

        list_clients_message = ListClientsMessage()
        list_rooms_message = ListRoomsMessage()
        self.client_thread.queue_message(list_clients_message)
        self.client_thread.queue_message(list_rooms_message)

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
        self.quit_btn = QPushButton("Quit")
        hbox.addWidget(self.quit_btn)

        self.setLayout(vbox)

    def construct_main_ui(self):
        return MainView(self, self.client_id, self.client_thread)

    def construct_room_ui(self, room_id, title):
        return RoomView(self, self.client_id, self.client_thread, room_id, title, True)

    def construct_direct_chat_ui(self, room_id, title):
        return RoomView(self, self.client_id, self.client_thread, room_id, title, False)

    def show_direct_chat(self, user_id, room_id, user_name):
        room_view = self.construct_direct_chat_ui(room_id, f"Chatting with {user_name}")
        self.stack.addWidget(room_view)
        self.stack.setCurrentWidget(room_view)

        self.back_btn.setEnabled(True)

    def show_room(self, room_id):
        room_view = self.construct_room_ui(room_id, "todo")
        self.stack.addWidget(room_view)
        self.stack.setCurrentWidget(room_view)

        self.back_btn.setEnabled(True)

    def return_home(self):
        current = self.stack.currentWidget()
        while current is not self.main_view:
            self.stack.removeWidget(current)
            current = self.stack.currentWidget()

        self.back_btn.setEnabled(False)


class ConnectionWindow(QWidget):
    addr_edit = None
    port_edit = None
    nick_edit = None

    # Must store reference to chat window otherwise it will
    # go out of scope and be destroyed
    chat_window = None

    def __init__(self):
        super().__init__()
        self.construct_ui()

    def construct_ui(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        # IP Address
        self.addr_edit = QLineEdit()
        self.addr_edit.setPlaceholderText("e.g. 127.0.0.1")
        addr_label = QLabel("Server Address:")
        addr_label.setBuddy(self.addr_edit)

        # Port
        self.port_edit = QLineEdit()
        self.port_edit.setPlaceholderText("e.g. 12000")
        port_label = QLabel("Server Port:")
        port_label.setBuddy(self.port_edit)

        # Nickname
        self.nick_edit = QLineEdit()
        self.nick_edit.setPlaceholderText("e.g. Matthew")
        nick_label = QLabel("Nickname:")
        nick_label.setBuddy(self.nick_edit)

        # Connect Button
        connect_button = QPushButton('Connect', self)
        connect_button.resize(connect_button.sizeHint())
        connect_button.clicked.connect(self.do_connection)

        # Populate vbox
        group = QGroupBox("Server Details")

        group_vbox = QVBoxLayout()
        group_vbox.addWidget(addr_label)
        group_vbox.addWidget(self.addr_edit)
        group_vbox.addWidget(port_label)
        group_vbox.addWidget(self.port_edit)
        group.setLayout(group_vbox)

        vbox.addWidget(group)

        hbox = QHBoxLayout()
        hbox.addWidget(self.nick_edit)
        hbox.addWidget(connect_button)

        vbox.addWidget(nick_label)
        vbox.addLayout(hbox)

        self.setWindowTitle('Enter Server Information')
        self.show()

    def do_connection(self):
        try:
            addr = self.addr_edit.text()
            port = int(self.port_edit.text())
            nick = self.nick_edit.text()

            self.chat_window = ChatWindow(addr, port, nick)
            self.chat_window.show()
            self.setVisible(False)
        except Exception as e:
            traceback.print_exception(e)
            QMessageBox.information(self, "Could not connect to server",
                                    "Ensure address, port, and nickname are valid",
                                    QMessageBox.Ok, QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = None

    if len(sys.argv) == 4:
        try:
            address = sys.argv[1]
            port = int(sys.argv[2])
            nickname = sys.argv[3]

            window = ChatWindow(address, port, nickname)
            window.show()
        except Exception as e:
            traceback.print_exception(e)
            print("Could not connect to server specified by command line arguments.")

            window = ConnectionWindow()
            window.show()
    else:
        window = ConnectionWindow()
        window.show()

    sys.exit(app.exec_())
