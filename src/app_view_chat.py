# Qt GUI (Chat View)
# Name: Matthew Jakeman
# UPI: mjak923

from datetime import datetime

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QScrollArea, QHBoxLayout, QLineEdit, QPushButton, \
    QListView, QFileDialog

from app_dialog_invite import InviteToRoomDialog
from message import RoomEntrySendMessage, RoomInviteMessage, ResourceTransferMessage


class RoomView(QWidget):
    room_id = None
    title = None

    app_state = None
    chat_window = None

    participants = None
    chat_vbox = None
    message_entry = None

    should_show_participants = None

    def __init__(self, parent, app_state, room_id, title, should_show_participants=False):
        super(RoomView, self).__init__()

        self.room_id = room_id
        self.title = title

        self.app_state = app_state
        self.chat_window = parent

        self.should_show_participants = should_show_participants

        self.app_state.client_thread.received_message.connect(self.on_message)

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
        send_message_btn.clicked.connect(self.send_text_message)
        hbox.addWidget(send_message_btn)

        send_image_btn = QPushButton("Attach")
        send_image_btn.clicked.connect(self.send_image_message)
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
            invite_btn.clicked.connect(self.show_invite_dialog)
            grid.addWidget(invite_btn, 2, 1)

        self.setLayout(grid)

    def on_message(self, room_id, user_id, timestamp, text):
        if room_id is not self.room_id:
            return

        label = QLabel(f"{user_id}: {text}\n{timestamp}")
        self.chat_vbox.addWidget(label)

    def show_invite_dialog(self):
        dlg = InviteToRoomDialog(self.app_state)
        dlg.setModal(True)

        # On success
        if dlg.exec():
            new_msg = RoomInviteMessage(self.room_id, dlg.client_id())
            self.app_state.client_thread.queue_message(new_msg)

    def send_text_message(self):
        text = self.message_entry.text()
        new_msg = RoomEntrySendMessage(self.room_id, text, datetime.now())
        self.app_state.client_thread.queue_message(new_msg)

    def send_image_message(self):
        filename = QFileDialog.getOpenFileName(self, "Open image", "/", "Image files (*.png *.jpg)")

        if filename:
            with open(filename[0], "rb") as image:
                f = image.read()
                b = bytearray(f)
                new_msg = ResourceTransferMessage(b)
                self.app_state.client_thread.queue_message(new_msg)
