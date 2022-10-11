# Qt GUI (Chat View)
# Name: Matthew Jakeman
# UPI: mjak923

from datetime import datetime

from PyQt5.QtCore import QByteArray, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QScrollArea, QHBoxLayout, QLineEdit, QPushButton, \
    QListView, QFileDialog, QProgressDialog, QFrame

from app_dialog_invite import InviteToRoomDialog
from config import INVALID_ID
from message import RoomEntrySendMessage, RoomInviteMessage, ResourceCreateMessage, ResourceFetchMessage

IMAGE_PREVIEW_HEIGHT = 200
IMAGE_PREVIEW_WIDTH = 300


class RoomView(QWidget):
    room_id = None
    title = None

    app_state = None
    chat_window = None

    participants = None
    chat_vbox = None
    message_entry = None

    should_show_participants = None
    upload_progress = None
    transfer_progress = None
    image = None

    def __init__(self, parent, app_state, room_id, title, should_show_participants=False):
        super(RoomView, self).__init__()

        self.room_id = room_id
        self.title = title

        self.app_state = app_state
        self.chat_window = parent

        self.should_show_participants = should_show_participants

        self.app_state.client_thread.received_message.connect(self.on_message)
        self.app_state.client_thread.resource_ack.connect(self.on_resource_created)
        self.app_state.client_thread.resource_transfer.connect(self.on_resource_transferred)

        self.construct_ui()

    def construct_ui(self):
        # (0,0) Label
        grid = QGridLayout()
        grid.addWidget(QLabel(self.title), 0, 0)

        # (1,0) Chat Messages
        # Special invocation to make vbox scrollable
        # See: https://stackoverflow.com/a/40139336
        self.chat_vbox = QVBoxLayout()
        self.chat_vbox.setAlignment(Qt.AlignTop)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        inner = QFrame(scroll_area)
        inner.setLayout(self.chat_vbox)
        scroll_area.setWidget(inner)

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

    def on_message(self, room_id, user_id, timestamp, text, resource_id):
        if room_id is not self.room_id:
            return

        if resource_id is not INVALID_ID:
            # Create image and setup scaling
            self.image = QLabel()
            self.image.setFixedWidth(IMAGE_PREVIEW_WIDTH)
            self.image.setFixedHeight(IMAGE_PREVIEW_HEIGHT)
            self.image.setAlignment(Qt.AlignCenter)
            self.chat_vbox.addWidget(self.image)

            # Styling
            self.image.setStyleSheet("background-color: black; border-radius: 8px; border 1px solid black;")

            new_msg = ResourceFetchMessage(resource_id)
            self.app_state.client_thread.queue_message(new_msg)
            self.transfer_progress = self.show_progress_dialog("Processing")

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
        new_msg = RoomEntrySendMessage(self.room_id, text, datetime.now(), INVALID_ID)
        self.app_state.client_thread.queue_message(new_msg)

    def send_image_message(self):

        if self.upload_progress is not None:
            return

        filename = QFileDialog.getOpenFileName(self, "Open image", "/", "Image files (*.png *.jpg)")

        if filename is None:
            return

        try:
            with open(filename[0], "rb") as image:
                f = image.read()
                b = bytearray(f)
                new_msg = ResourceCreateMessage(b)
                self.app_state.client_thread.queue_message(new_msg)
        except FileNotFoundError:
            return

        self.upload_progress = self.show_progress_dialog("Uploading")

    def show_progress_dialog(self, title):
        progress = QProgressDialog()

        progress.setMinimum(0)
        progress.setMaximum(0)
        progress.setModal(True)
        progress.setWindowTitle(title)
        progress.show()

        return progress

    def on_resource_created(self, resource_id):
        if self.upload_progress is not None:
            self.upload_progress.close()

            new_msg = RoomEntrySendMessage(self.room_id, f"Sending image: {resource_id}", datetime.now(), resource_id)
            self.app_state.client_thread.queue_message(new_msg)

            self.upload_progress = None

    def on_resource_transferred(self, resource_data):
        if self.transfer_progress is not None:
            self.transfer_progress.close()

            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(resource_data))
            self.image.setPixmap(pixmap.scaled(IMAGE_PREVIEW_WIDTH, IMAGE_PREVIEW_WIDTH, Qt.KeepAspectRatio))

            self.image = None
            self.transfer_progress = None
