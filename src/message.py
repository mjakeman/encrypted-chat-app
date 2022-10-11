# Message Protocol
# Name: Matthew Jakeman
# UPI: mjak923
import datetime
from enum import IntEnum

from config import INVALID_ID

SEPERATOR_TOKEN = chr(0xFFFF)
MESSAGE_HEADER_SIZE = 8


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
    RESOURCE_CREATE = 14,
    ACKNOWLEDGE_RESOURCE = 15,
    RESOURCE_FETCH = 16,
    RESOURCE_TRANSFER = 17


def build_message_header(length, msg_type):
    header = (length << 8) | int(msg_type)
    return header.to_bytes(MESSAGE_HEADER_SIZE, byteorder='big')


def parse_message_header(header):
    integer_val = int.from_bytes(header, byteorder='big')

    length = (integer_val >> 8)
    msg_type = integer_val & 0b11111111
    return length, MessageType(msg_type)


def message_to_wire(message):
    message_data = message.to_bytes()
    msg_type = message.message_type

    if message_data:
        message_bytes = bytearray(message_data)

        length = len(message_bytes)
        header = build_message_header(length, msg_type)
        message_bytes[:0] = header  # prepend to byte array

        return message_bytes
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
        host_id = int(tokens[2])
        host_name = tokens[3]
        return RoomDiscoveryMessage(room_id, title, host_id, host_name)
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
        return InitiateUserChatMessage(user_id)
    elif message_type == MessageType.ACKNOWLEDGE_USER_CHAT:
        tokens = byte_data.decode().split(SEPERATOR_TOKEN)
        room_id = int(tokens[0])
        user_id = int(tokens[1])
        user_nick = tokens[2]
        return AcknowledgeUserChatMessage(room_id, user_id, user_nick)
    elif message_type == MessageType.ROOM_MESSAGE_SEND:
        tokens = byte_data.decode().split(SEPERATOR_TOKEN)
        room_id = int(tokens[0])
        text = tokens[1]
        timestamp = datetime.datetime.fromisoformat(tokens[2])
        resource_id = int(tokens[3])
        return RoomEntrySendMessage(room_id, text, timestamp, resource_id)
    elif message_type == MessageType.ROOM_MESSAGE_BROADCAST:
        tokens = byte_data.decode().split(SEPERATOR_TOKEN)
        room_id = int(tokens[0])
        text = tokens[1]
        timestamp = datetime.datetime.fromisoformat(tokens[2])
        user_id = int(tokens[3])
        resource_id = int(tokens[4])
        return RoomEntryBroadcastMessage(room_id, text, timestamp, user_id, resource_id)
    elif message_type == MessageType.RESOURCE_CREATE:
        return ResourceCreateMessage(byte_data)
    elif message_type == MessageType.ACKNOWLEDGE_RESOURCE:
        resource_id = int(byte_data.decode())
        return AcknowledgeResourceMessage(resource_id)
    elif message_type == MessageType.RESOURCE_FETCH:
        resource_id = int(byte_data.decode())
        return ResourceFetchMessage(resource_id)
    elif message_type == MessageType.RESOURCE_TRANSFER:
        return ResourceTransferMessage(byte_data)


def parse_message(byte_data):
    (_, msg_type) = parse_message_header(byte_data[0:MESSAGE_HEADER_SIZE])
    return parse_message_contents(msg_type, byte_data[MESSAGE_HEADER_SIZE:])


class Message:
    message_type = None

    def __init__(self, message_type):
        self.message_type = message_type

    def __str__(self):
        raise Exception("Cannot serialise the base Message type")

    def to_bytes(self):
        raise Exception("Cannot serialise the base Message type")


class NicknameMessage(Message):
    nickname = None

    def __init__(self, content):
        super(NicknameMessage, self).__init__(MessageType.NICKNAME)

        self.nickname = content

    def __str__(self):
        return self.nickname

    def to_bytes(self):
        return self.__str__().encode()


class AcknowledgeClientMessage(Message):
    client_id = None

    def __init__(self, client_id):
        super(AcknowledgeClientMessage, self).__init__(MessageType.ACKNOWLEDGE_CLIENT)

        self.client_id = client_id

    def __str__(self):
        return str(self.client_id)

    def to_bytes(self):
        return self.__str__().encode()


class ListClientsMessage(Message):
    def __init__(self):
        super(ListClientsMessage, self).__init__(MessageType.LIST_CLIENTS)

    def __str__(self):
        return None

    def to_bytes(self):
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

    def to_bytes(self):
        return self.__str__().encode()


class ListRoomsMessage(Message):
    def __init__(self):
        super(ListRoomsMessage, self).__init__(MessageType.LIST_ROOMS)

    def __str__(self):
        return None

    def to_bytes(self):
        return None


class RoomDiscoveryMessage(Message):
    room_id = None
    title = None
    host_id = None
    host_name = None

    def __init__(self, room_id, room_title, host_id, host_name):
        super(RoomDiscoveryMessage, self).__init__(MessageType.ROOM_DISCOVERY)
        self.room_id = room_id
        self.title = room_title
        self.host_id = host_id
        self.host_name = host_name

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.room_id), str(self.title),
                                     str(self.host_id), str(self.host_name)])

    def to_bytes(self):
        return self.__str__().encode()


class RoomCreateMessage(Message):
    host_id = None
    title = None

    def __init__(self, host_id, title):
        super(RoomCreateMessage, self).__init__(MessageType.ROOM_CREATE)
        self.host_id = host_id
        self.title = title

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.host_id), str(self.title)])

    def to_bytes(self):
        return self.__str__().encode()


class AcknowledgeRoomCreateMessage(Message):
    room_id = None

    def __init__(self, room_id):
        super(AcknowledgeRoomCreateMessage, self).__init__(MessageType.ACKNOWLEDGE_ROOM_CREATE)
        self.room_id = room_id

    def __str__(self):
        return str(self.room_id)

    def to_bytes(self):
        return self.__str__().encode()


class RoomInviteMessage(Message):
    room_id = None
    client_id = None

    def __init__(self, room_id, client_id):
        super(RoomInviteMessage, self).__init__(MessageType.ROOM_INVITE)
        self.room_id = room_id
        self.client_id = client_id

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.room_id), str(self.client_id)])

    def to_bytes(self):
        return self.__str__().encode()


class InitiateUserChatMessage(Message):
    user_id = None

    def __init__(self, user_id):
        super(InitiateUserChatMessage, self).__init__(MessageType.INITIATE_USER_CHAT)
        self.user_id = user_id

    def __str__(self):
        return str(self.user_id)

    def to_bytes(self):
        return self.__str__().encode()


class AcknowledgeUserChatMessage(Message):
    room_id = None
    user_id = None
    user_nick = None

    def __init__(self, room_id, user_id, user_nick):
        super(AcknowledgeUserChatMessage, self).__init__(MessageType.ACKNOWLEDGE_USER_CHAT)
        self.room_id = room_id
        self.user_id = user_id
        self.user_nick = user_nick

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.room_id), str(self.user_id), str(self.user_nick)])

    def to_bytes(self):
        return self.__str__().encode()


class RoomEntrySendMessage(Message):
    text = None
    timestamp = None
    room_id = None
    resource_id = None

    def __init__(self, room_id, text, timestamp, resource_id):
        super(RoomEntrySendMessage, self).__init__(MessageType.ROOM_MESSAGE_SEND)
        self.room_id = room_id
        self.text = text
        self.timestamp = timestamp
        self.resource_id = resource_id

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.room_id), str(self.text),
                                     datetime.datetime.isoformat(self.timestamp),
                                     str(self.resource_id)])

    def to_bytes(self):
        return self.__str__().encode()


class RoomEntryBroadcastMessage(Message):
    text = None
    timestamp = None
    user_id = None
    room_id = None
    resource_id = None

    def __init__(self, room_id, text, timestamp, user_id, resource_id):
        super(RoomEntryBroadcastMessage, self).__init__(MessageType.ROOM_MESSAGE_BROADCAST)
        self.text = text
        self.timestamp = timestamp
        self.user_id = user_id
        self.room_id = room_id
        self.resource_id = resource_id

    def __str__(self):
        return SEPERATOR_TOKEN.join([str(self.room_id), str(self.text),
                                     datetime.datetime.isoformat(self.timestamp),
                                     str(self.user_id),
                                     str(self.resource_id)])

    def to_bytes(self):
        return self.__str__().encode()


class ResourceCreateMessage(Message):
    data = None

    def __init__(self, data):
        super(ResourceCreateMessage, self).__init__(MessageType.RESOURCE_CREATE)
        self.data = data

    def to_bytes(self):
        return self.data


class AcknowledgeResourceMessage(Message):
    resource_id = None

    def __init__(self, resource_id):
        super(AcknowledgeResourceMessage, self).__init__(MessageType.ACKNOWLEDGE_RESOURCE)
        self.resource_id = resource_id

    def __str__(self):
        return str(self.resource_id)

    def to_bytes(self):
        return self.__str__().encode()


class ResourceFetchMessage(Message):
    resource_id = None

    def __init__(self, resource_id):
        super(ResourceFetchMessage, self).__init__(MessageType.RESOURCE_FETCH)
        self.resource_id = resource_id

    def __str__(self):
        return str(self.resource_id)

    def to_bytes(self):
        return self.__str__().encode()


class ResourceTransferMessage(Message):
    data = None

    def __init__(self, data):
        super(ResourceTransferMessage, self).__init__(MessageType.RESOURCE_TRANSFER)
        self.data = data

    def to_bytes(self):
        return self.data
