# Qt GUI
# Name: Matthew Jakeman
# UPI: mjak923

import sys
import traceback

from PyQt5.QtCore import QTimer, QThread, QObject, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGroupBox,
                             QMessageBox, QListView)

from client import Client
from message import MessageType


class ClientThread(QThread):
    client = None

    discovered_client = pyqtSignal(str)

    def __init__(self, client):
        super().__init__()
        self.client = client

    def dispatch(self, server_socket, message):
        if message.message_type is MessageType.CLIENT_DISCOVERY:
            print(f"Discovered client: {message.nickname}")
            self.discovered_client.emit(message.nickname)
            return

        print(f"Unsupported message: {message.message_type}")

    def run(self):
        while True:
            self.client.poll(self.dispatch)


class ChatWindow(QWidget):
    client_thread = None
    client_id = -1

    users_model = None
    rooms_model = None

    def __init__(self, address, port, nickname):
        super().__init__()

        # Create Models
        self.users_model = QStandardItemModel()
        self.rooms_model = QStandardItemModel()

        # Setup Client
        client = Client(address, port, nickname)
        self.client_id = client.client_id
        self.client_thread = ClientThread(client)

        # Connect signals
        self.client_thread.discovered_client.connect(self.on_discover_client)

        self.client_thread.start()

        self.construct_ui()

    def on_discover_client(self, nickname):

        row = QStandardItem(nickname)
        self.users_model.appendRow(row)
        pass

    def construct_ui(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        # Create Users Section
        users_group = QGroupBox("Users")
        users_vbox = QVBoxLayout()

        # List of currently logged-in users
        users_list = QListView()
        users_list.setModel(self.users_model)
        users_vbox.addWidget(users_list)

        # Chat button for users
        users_chat_btn = QPushButton("Chat")
        users_vbox.addWidget(users_chat_btn)

        users_group.setLayout(users_vbox)
        hbox.addWidget(users_group)

        # Create Rooms Section
        rooms_group = QGroupBox("Rooms")
        rooms_vbox = QVBoxLayout()

        # List of rooms
        rooms_list = QListView()
        rooms_list.setModel(self.rooms_model)
        rooms_vbox.addWidget(rooms_list)

        # Chat button for rooms
        rooms_chat_btn = QPushButton("Join")
        rooms_vbox.addWidget(rooms_chat_btn)

        rooms_group.setLayout(rooms_vbox)
        hbox.addWidget(rooms_group)

        # Add Quit Button
        btn = QPushButton("Quit")
        vbox.addWidget(btn)

        self.setLayout(vbox)


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
