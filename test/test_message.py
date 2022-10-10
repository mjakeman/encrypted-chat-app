# Testing: Message
# Name: Matthew Jakeman
# UPI: mjak923

from unittest import TestCase
from message import *


class MessageTest(TestCase):
    def test_header_round_trip(self):
        header = build_message_header(4080, 3)
        (l, t) = parse_message_header(header)

        self.assertEqual(l, 4080)
        self.assertEqual(t, 3)

    def test_nickname_round_trip(self):
        message = NicknameMessage("Matthew")
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)

        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.nickname, cmp_message.nickname)

    def test_ack_client_round_trip(self):
        message = AcknowledgeClientMessage(147)
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.client_id, cmp_message.client_id)

    def test_list_clients_round_trip(self):
        message = ListClientsMessage()
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)

    def test_client_discovery_round_trip(self):
        message = ClientDiscoveryMessage(12, "Some data")
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.client_id, cmp_message.client_id)
        self.assertEqual(message.nickname, cmp_message.nickname)

    def test_list_rooms_round_trip(self):
        message = ListRoomsMessage()
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)

    def test_room_discovery_round_trip(self):
        message = RoomDiscoveryMessage(12, "Hello")
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.room_id, cmp_message.room_id)
        self.assertEqual(message.title, cmp_message.title)

    def test_room_create_round_trip(self):
        message = RoomCreateMessage(125, "My Room")
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.host_id, cmp_message.host_id)
        self.assertEqual(message.title, cmp_message.title)

    def test_ack_room_create_round_trip(self):
        message = AcknowledgeRoomCreateMessage(14)
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.room_id, cmp_message.room_id)

    def test_initiate_user_chat_round_trip(self):
        message = InitiateUserChat(14)
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.user_id, cmp_message.user_id)

    def test_ack_user_chat_round_trip(self):
        message = AcknowledgeUserChat(14, 26, "Name")
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.room_id, cmp_message.room_id)
        self.assertEqual(message.user_id, cmp_message.user_id)
        self.assertEqual(message.user_nick, cmp_message.user_nick)

    def test_room_message_send_round_trip(self):
        message = RoomMessageSend(14, "Name", datetime.datetime.now())
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.room_id, cmp_message.room_id)
        self.assertEqual(message.text, cmp_message.text)
        self.assertEqual(message.timestamp, cmp_message.timestamp)

    def test_room_message_broadcast_round_trip(self):
        message = RoomMessageBroadcast(14, "Name", datetime.datetime.now(), 8)
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.room_id, cmp_message.room_id)
        self.assertEqual(message.text, cmp_message.text)
        self.assertEqual(message.timestamp, cmp_message.timestamp)
        self.assertEqual(message.user_id, cmp_message.user_id)
