# Testing: Message
# Name: Matthew Jakeman
# UPI: mjak923

from unittest import TestCase
from message import *


class MessageTest(TestCase):
    def test_nickname_round_trip(self):
        message = NicknameMessage("Matthew")
        message_str = message.__str__()

        cmp_message = parse_message(message_str)
        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.nickname, cmp_message.nickname)

    def test_list_clients_round_trip(self):
        message = ListClientsMessage()
        message_str = message.__str__()

        cmp_message = parse_message(message_str)
        self.assertEqual(message.message_type, cmp_message.message_type)

    def test_client_data_round_trip(self):
        message = ClientDataMessage("Some data")
        message_str = message.__str__()

        cmp_message = parse_message(message_str)
        self.assertEqual(message.message_type, cmp_message.message_type)
        self.assertEqual(message.nickname, cmp_message.nickname)
