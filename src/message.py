# SE364 A2 Message
# Name: Matthew Jakeman
# UPI: mjak923

from enum import Enum

SEPERATOR_TOKEN = ';'
NO_CONTENT = " "


class MessageType(Enum):
    NICKNAME = 1
    LIST_CLIENTS = 2,
    CLIENT_DATA = 3


def parse_message(message):
    tokens = message.split(SEPERATOR_TOKEN)
    message_type = MessageType[tokens[0]]

    if message_type == MessageType.NICKNAME:
        return NicknameMessage(tokens[1])
    elif message_type == MessageType.LIST_CLIENTS:
        return ListClientsMessage()
    elif message_type == MessageType.CLIENT_DATA:
        return ClientDataMessage(tokens[1])


class Message:
    message_type = None

    def __init__(self, message_type):
        self.message_type = message_type

    def __str__(self):
        raise Exception("Cannot serialise the base Message type")


class NicknameMessage(Message):
    nickname = None

    def __init__(self, content):
        super(NicknameMessage, self).__init__(MessageType.NICKNAME)

        self.nickname = content

    def __str__(self):
        return MessageType.NICKNAME.name + ";" + self.nickname


class ListClientsMessage(Message):
    def __init__(self):
        super(ListClientsMessage, self).__init__(MessageType.LIST_CLIENTS)

    def __str__(self):
        return MessageType.LIST_CLIENTS.name + ";" + NO_CONTENT


class ClientDataMessage(Message):
    nickname = None

    def __init__(self, content):
        super(ClientDataMessage, self).__init__(MessageType.CLIENT_DATA)
        self.nickname = content

    def __str__(self):
        return MessageType.CLIENT_DATA.name + ";" + self.nickname
