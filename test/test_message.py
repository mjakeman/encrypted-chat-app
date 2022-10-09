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

    def test_list_clients_round_trip(self):
        message = ListClientsMessage()
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)

    def test_client_data_round_trip(self):
        message = ClientDataMessage("Some data")
        byte_data = message_to_wire(message)

        cmp_message = parse_message(byte_data)
        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.nickname, cmp_message.nickname)
