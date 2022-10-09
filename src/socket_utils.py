# Socket Utils
# Name: Matthew Jakeman
# UPI: mjak923

from message import *


def send_message(sender_socket, msg):
    byte_data = message_to_wire(msg)
    sender_socket.send(byte_data)
    print(f"DEBUG: Sent message of type {msg.message_type.name}")


def recv_message(listener_socket):
    header = listener_socket.recv(MESSAGE_HEADER_SIZE)

    if not header:
        print("DEBUG: Peer disconnected")
        return None

    (length, msg_type) = parse_message_header(header)
    print(f"DEBUG: Received message of type {msg_type.name}")

    if length > 0:
        contents = listener_socket.recv(length)
        return parse_message_contents(msg_type, contents)
    else:
        return parse_message_contents(msg_type, None)
