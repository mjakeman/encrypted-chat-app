# Qt GUI (Connection Window)
# Name: Matthew Jakeman
# UPI: mjak923

import traceback

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QGroupBox, QHBoxLayout, QMessageBox

from app_window import ChatWindow


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
