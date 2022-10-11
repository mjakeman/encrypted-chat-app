# Qt GUI (Chat View)
# Name: Matthew Jakeman
# UPI: mjak923

from datetime import datetime

from PyQt5.QtCore import QByteArray, Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath
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
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 1)

        # (1,0) Chat Messages
        # Special invocation to make vbox scrollable
        # See: https://stackoverflow.com/a/40139336
        self.chat_vbox = QVBoxLayout()
        self.chat_vbox.setAlignment(Qt.AlignTop)
        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
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

    def append_message(self, widget, is_current_user):
        parent_hbox = QHBoxLayout()

        if is_current_user:
            parent_hbox.addStretch()
            parent_hbox.addWidget(widget)
        else:
            parent_hbox.addWidget(widget)
            parent_hbox.addStretch()

        self.chat_vbox.addLayout(parent_hbox)

    def on_message(self, room_id, user_id, timestamp, text, resource_id):
        if room_id is not self.room_id:
            return

        is_current_user = (user_id is self.app_state.client_id)

        if resource_id is not INVALID_ID:
            # Create image and setup scaling
            self.image = QLabel()
            self.image.setFixedWidth(IMAGE_PREVIEW_WIDTH)
            self.image.setFixedHeight(IMAGE_PREVIEW_HEIGHT)
            self.image.setAlignment(Qt.AlignCenter)
            self.append_message(self.image, is_current_user)

            # Styling
            self.image.setStyleSheet("background-color: black; border-radius: 8px; border 1px solid black;")

            new_msg = ResourceFetchMessage(resource_id)
            self.app_state.client_thread.queue_message(new_msg)
            self.transfer_progress = self.show_progress_dialog("Processing")

        frame = QFrame()
        hbox = QHBoxLayout()
        frame.setLayout(hbox)

        label = QLabel()
        label.setWordWrap(True)

        if is_current_user:
            label.setText(f"{text}")
            frame.setStyleSheet("background-color: #1c71d8; color: white; border-radius: 20px;")
        else:
            nickname = self.app_state.get_known_client_name(user_id)
            label.setText(f"{nickname}: {text}")
            frame.setStyleSheet("background-color: #813d9c; color: white; border-radius: 20px;")

        time = QLabel(timestamp.strftime("%H.%M"))
        time.setStyleSheet("color: #deddda; font-size: 60%;")

        hbox.addWidget(label)
        hbox.addSpacing(10)
        hbox.addWidget(time)

        self.append_message(frame, is_current_user)

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

            new_msg = RoomEntrySendMessage(self.room_id, "Sent an image.", datetime.now(), resource_id)
            self.app_state.client_thread.queue_message(new_msg)

            self.upload_progress = None

    def on_resource_transferred(self, resource_data):
        if self.transfer_progress is not None:
            self.transfer_progress.close()

            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(resource_data))
            pixmap = pixmap.scaled(IMAGE_PREVIEW_WIDTH, IMAGE_PREVIEW_WIDTH, Qt.KeepAspectRatio)

            self.image.setPixmap(pixmap)

            self.image = None
            self.transfer_progress = None
