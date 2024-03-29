# Qt GUI (App Thread)
# Name: Matthew Jakeman
# UPI: mjak923

import queue
import sys
import traceback
from datetime import datetime

from PyQt5.QtCore import QThread, pyqtSignal

from message import MessageType


class ClientThread(QThread):
    client = None
    queue = None

    running = None

    discovered_client = pyqtSignal(int, str)
    discovered_room = pyqtSignal(int, str, int, str)
    created_room = pyqtSignal(int)
    started_chat = pyqtSignal(int, int, str)
    received_message = pyqtSignal(int, int, datetime, str, int)
    resource_ack = pyqtSignal(int)
    resource_transfer = pyqtSignal(bytearray)
    room_membership = pyqtSignal(int, object)

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.queue = queue.Queue()
        self.running = True

    def dispatch(self, server_socket, message):
        if message.message_type is MessageType.CLIENT_DISCOVERY:
            print(f"Discovered client: {message.nickname}")
            self.discovered_client.emit(message.client_id, message.nickname)
            return

        if message.message_type is MessageType.ROOM_DISCOVERY:
            print(f"Discovered room: {message.title}")
            self.discovered_room.emit(message.room_id, message.title, message.host_id, message.host_name)
            return

        if message.message_type is MessageType.ACKNOWLEDGE_ROOM_CREATE:
            print(f"Ack'd room creation: {message.room_id}")
            self.created_room.emit(message.room_id)
            return

        if message.message_type is MessageType.ACKNOWLEDGE_USER_CHAT:
            print(f"Ack'd user chat: {message.room_id}")
            self.started_chat.emit(message.user_id, message.room_id, message.user_nick)
            return

        if message.message_type is MessageType.ROOM_MESSAGE_BROADCAST:
            print(f"Room {message.room_id}, User {message.user_id}, Time {str(message.timestamp)}: {message.text}, "
                  f"Resource: {str(message.resource_id)}")

            self.received_message.emit(message.room_id, message.user_id, message.timestamp,
                                       message.text, message.resource_id)
            return

        if message.message_type is MessageType.ACKNOWLEDGE_RESOURCE:
            print(f"Resource created: {message.resource_id}")
            self.resource_ack.emit(message.resource_id)
            return

        if message.message_type is MessageType.RESOURCE_TRANSFER:
            self.resource_transfer.emit(message.data)
            return

        if message.message_type is MessageType.ROOM_MEMBERSHIP_DISCOVERY:
            self.room_membership.emit(message.host_id, message.members)
            return

        print(f"Unsupported message: {message.message_type}")

    def run(self):
        while self.running:
            # Poll for incoming messages
            self.client.poll(self.dispatch)

            # Send all queued messages
            while not self.queue.empty():
                message = self.queue.get()
                self.client.send_message(message)

        # Loop terminated, so quit
        self.client.__del__()

    def queue_message(self, message):
        self.queue.put(message)

    def stop(self):
        self.running = False
