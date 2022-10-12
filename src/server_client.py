# Server Client Data
# Name: Matthew Jakeman
# UPI: mjak923

class ClientData:
    client_nick = None
    client_id = None
    user_room_map = {}

    def __init__(self, client_id):
        self.client_id = client_id
