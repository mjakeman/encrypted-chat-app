# Message Protocol
# Name: Matthew Jakeman
# UPI: mjak923
import datetime
from enum import IntEnum

SEPERATOR_TOKEN = chr(0xFFFF)
MESSAGE_HEADER_SIZE = 4


# Message Protocol:
#
# This message system uses a custom 'on the wire' protocol:
#  - Message Header (64 bits)
#  - Content (variable)
#
# The message header is 64-bits long and holds two fields:
#  - length 56 bits
#  - type 8 bits
#
# The content encoding depends on the message and will have
# a length of exactly 'length' bits.


class MessageType(IntEnum):
    NICKNAME = 1,
    ACKNOWLEDGE_CLIENT = 2,
    LIST_CLIENTS = 3,
    CLIENT_DISCOVERY = 4,
    LIST_ROOMS = 5,
    ROOM_DISCOVERY = 6,
    ROOM_CREATE = 7,
    ACKNOWLEDGE_ROOM_CREATE = 8,
    ROOM_INVITE = 9,
    INITIATE_USER_CHAT = 10,
    ACKNOWLEDGE_USER_CHAT = 11,
    ROOM_MESSAGE_SEND = 12,
    ROOM_MESSAGE_BROADCAST = 13,


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
    elif message_type == MessageType.ACKNOWLEDGE_CLIENT:
        client_id = int(byte_data.decode())
        return AcknowledgeClientMessage(client_id)
    elif message_type == MessageType.LIST_CLIENTS:
        return ListClientsMessage()
    elif message_type == MessageType.CLIENT_DISCOVERY:
        tokens = byte_data.decode().split(SEPERATOR_TOKEN)
        client_id = int(tokens[0])
        nickname = tokens[1]
        return ClientDiscoveryMessage(client_id, nickname)
    elif message_type == MessageType.LIST_ROOMS:
        return ListRoomsMessage()
    elif message_type == MessageType.ROOM_DISCOVERY:
        tokens = byte_data.decode().split(SEPERATOR_TOKEN)
        room_id = int(tokens[0])
        title = tokens[1]
        return RoomDiscoveryMessage(room_id, title)
    elif message_type == MessageType.ROOM_CREATE:
        tokens = byte_data.decode().split(SEPERATOR_TOKEN)
        host_id = int(tokens[0])
        title = tokens[1]
        return RoomCreateMessage(host_id, title)
    elif message_type == MessageType.ACKNOWLEDGE_ROOM_CREATE:
        room_id = int(byte_data.decode())
        return AcknowledgeRoomCreateMessage(room_id)
    elif message_type == MessageType.ROOM_INVITE:
        tokens = byte_data.decode().split(SEPERATOR_TOKEN)
        room_id = int(tokens[0])
        client_id = int(tokens[1])
        return RoomInviteMessage(room_id, client_id)
    elif message_type == MessageType.INITIATE_USER_CHAT:
        user_id = int(byte_data.decode())
        return InitiateUserChat(user_id)
    elif message_type == MessageType.ACKNOWLEDGE_USER_CHAT:
        tokens = byte_data.decode().split(SEPERATOR_TOKEN)
        room_id = int(tokens[0])
        user_id = int(tokens[1])
        user_nick = tokens[2]
        return AcknowledgeUserChat(room_id, user_id, user_nick)
    elif message_type == MessageType.ROOM_MESSAGE_SEND:
        tokens = byte_data.decode().split(SEPERATOR_TOKEN)
        room_id = int(tokens[0])
        text = tokens[1]
        timestamp = datetime.datetime.fromisoformat(tokens[2])
        return RoomMessageSend(room_id, text, timestamp)
    elif message_type == MessageType.ROOM_MESSAGE_BROADCAST:
        tokens = byte_data.decode().split(SEPERATOR_TOKEN)
        room_id = int(tokens[0])
        text = tokens[1]
        timestamp = datetime.datetime.fromisoformat(tokens[2])
        user_id = int (tokens[3])
        return RoomMessageBroadcast(room_id, text, timestamp, user_id)


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


class AcknowledgeClientMessage(Message):
    client_id = None

    def __init__(self, client_id):
        super(AcknowledgeClientMessage, self).__init__(MessageType.ACKNOWLEDGE_CLIENT)

        self.client_id = client_id

    def __str__(self):
        return str(self.client_id)


class ListClientsMessage(Message):
    def __init__(self):
        super(ListClientsMessage, self).__init__(MessageType.LIST_CLIENTS)

    def __str__(self):
        return None


class ClientDiscoveryMessage(Message):
    nickname = None
    client_id = None

    def __init__(self, client_id, nickname):
        super(ClientDiscoveryMessage, self).__init__(MessageType.CLIENT_DISCOVERY)
        self.client_id = client_id
        self.nickname = nickname

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.client_id), str(self.nickname)])


class ListRoomsMessage(Message):
    def __init__(self):
        super(ListRoomsMessage, self).__init__(MessageType.LIST_ROOMS)

    def __str__(self):
        return None


class RoomDiscoveryMessage(Message):
    room_id = None
    title = None

    def __init__(self, room_id, room_title):
        super(RoomDiscoveryMessage, self).__init__(MessageType.ROOM_DISCOVERY)
        self.room_id = room_id
        self.title = room_title

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.room_id), str(self.title)])


class RoomCreateMessage(Message):
    host_id = None
    title = None

    def __init__(self, host_id, title):
        super(RoomCreateMessage, self).__init__(MessageType.ROOM_CREATE)
        self.host_id = host_id
        self.title = title

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.host_id), str(self.title)])


class AcknowledgeRoomCreateMessage(Message):
    room_id = None

    def __init__(self, room_id):
        super(AcknowledgeRoomCreateMessage, self).__init__(MessageType.ACKNOWLEDGE_ROOM_CREATE)
        self.room_id = room_id

    def __str__(self):
        return str(self.room_id)


class RoomInviteMessage(Message):
    room_id = None
    client_id = None

    def __init__(self, room_id, client_id):
        super(RoomInviteMessage, self).__init__(MessageType.ROOM_INVITE)
        self.room_id = room_id
        self.client_id = client_id

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.room_id), str(self.client_id)])


class InitiateUserChat(Message):
    user_id = None

    def __init__(self, user_id):
        super(InitiateUserChat, self).__init__(MessageType.INITIATE_USER_CHAT)
        self.user_id = user_id

    def __str__(self):
        return str(self.user_id)


class AcknowledgeUserChat(Message):
    room_id = None
    user_id = None
    user_nick = None

    def __init__(self, room_id, user_id, user_nick):
        super(AcknowledgeUserChat, self).__init__(MessageType.ACKNOWLEDGE_USER_CHAT)
        self.room_id = room_id
        self.user_id = user_id
        self.user_nick = user_nick

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.room_id), str(self.user_id), str(self.user_nick)])


class RoomMessageSend(Message):
    text = None
    timestamp = None
    room_id = None

    def __init__(self, room_id, text, timestamp):
        super(RoomMessageSend, self).__init__(MessageType.ROOM_MESSAGE_SEND)
        self.room_id = room_id
        self.text = text
        self.timestamp = timestamp

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.room_id), str(self.text), datetime.datetime.isoformat(self.timestamp)])


class RoomMessageBroadcast(Message):
    text = None
    timestamp = None
    user_id = None
    room_id = None

    def __init__(self, room_id, text, timestamp, user_id):
        super(RoomMessageBroadcast, self).__init__(MessageType.ROOM_MESSAGE_BROADCAST)
        self.text = text
        self.timestamp = timestamp
        self.user_id = user_id
        self.room_id = room_id

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.room_id), str(self.text),
                                     datetime.datetime.isoformat(self.timestamp),
                                     str(self.user_id)])
