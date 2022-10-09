# Message Protocol
# Name: Matthew Jakeman
# UPI: mjak923

from enum import IntEnum

SEPERATOR_TOKEN = ':'
MESSAGE_HEADER_SIZE = 4

# Message Protocol:
#
# This message system uses a custom 'on the wire' protocol:
#  - Message Header (32 bits)
#  - Content (variable)
#
# The message header is 32-bits long and holds two fields:
#  - length 24 bits
#  - type 8 bits
#
# The content encoding depends on the message and will have
# a length of exactly 'length' bits.


class MessageType(IntEnum):
    NICKNAME = 1
    LIST_CLIENTS = 2,
    CLIENT_DATA = 3


def build_message_header(length, msg_type):
    header = (length << 8) | int(msg_type)
    return header.to_bytes(4, byteorder='big')


def parse_message_header(header):
    integer_val = int.from_bytes(header, byteorder='big')

    length = (integer_val >> 8)
    msg_type = integer_val & 0b1111
    return length, MessageType(msg_type)


def message_to_wire(message):
    message_str = message.__str__()
    msg_type = message.message_type

    if message_str:
        message_data = bytearray(message_str.encode())

        length = len(message_data)
        header = build_message_header(length, msg_type)
        message_data[:0] = header  # prepend to byte array

        return message_data
    else:
        header = build_message_header(0, msg_type)
        return header


def parse_message_contents(message_type, byte_data):
    if message_type == MessageType.NICKNAME:
        return NicknameMessage(byte_data.decode())
    elif message_type == MessageType.LIST_CLIENTS:
        return ListClientsMessage()
    elif message_type == MessageType.CLIENT_DATA:
        return ClientDataMessage(byte_data.decode())


def parse_message(byte_data):
    (_, msg_type) = parse_message_header(byte_data[0:4])
    return parse_message_contents(msg_type, byte_data[4:])


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
        return self.nickname


class ListClientsMessage(Message):
    def __init__(self):
        super(ListClientsMessage, self).__init__(MessageType.LIST_CLIENTS)

    def __str__(self):
        return None


class ClientDataMessage(Message):
    nickname = None

    def __init__(self, content):
        super(ClientDataMessage, self).__init__(MessageType.CLIENT_DATA)
        self.nickname = content

    def __str__(self):
        return self.nickname
