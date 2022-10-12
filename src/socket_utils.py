# Socket Utils
# Name: Matthew Jakeman
# UPI: mjak923
import traceback

from message import *

MAX_SOCKET_TRANSFER = 1024


def send_message(sender_socket, msg):
    if msg is None:
        print("WARN: Attempted to send null message")
        traceback.print_stack()
        return

    if sender_socket is None:
        print("WARN: Attempted to send message to invalid socket")
        traceback.print_stack()
        return

    byte_data = message_to_wire(msg)
    sender_socket.sendall(byte_data)

    extra_length = len(byte_data) - MESSAGE_HEADER_SIZE
    if extra_length > 0:
        print(f"DEBUG: Sent message of type {msg.message_type.name} (length: {extra_length})")
    else:
        print(f"DEBUG: Sent message of type {msg.message_type.name}")


def recv_message(listener_socket):
    header = listener_socket.recv(MESSAGE_HEADER_SIZE)

    if not header:
        print("WARN: Peer disconnected - things will probably crash")
        return None

    (length, msg_type) = parse_message_header(header)
    print(f"DEBUG: Received message of type {msg_type.name}")

    if length > 0:
        # Create empty contents
        contents = bytearray()

        # Do not exceed max socket transfer size
        bytes_remaining = length
        while bytes_remaining > MAX_SOCKET_TRANSFER:
            # Receive bytes and add to array
            add = listener_socket.recv(MAX_SOCKET_TRANSFER)
            contents += bytearray(add)

            # Decrease length by amount transferred
            bytes_remaining -= len(add)

        # Append the remaining amount
        add = listener_socket.recv(bytes_remaining)
        contents += bytearray(add)

        # Ensure message transferred in full
        if len(contents) != length:
            print("ERROR: Message was corrupted")
            print(f"Expected length: {length}")
            print(f"Actual length: {len(contents)}")
            return None

        # Parse contents
        return parse_message_contents(msg_type, contents)
    else:
        return parse_message_contents(msg_type, None)
