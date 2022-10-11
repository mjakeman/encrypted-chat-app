# Qt GUI (Invite Dialog)
# Name: Matthew Jakeman
# UPI: mjak923

from PyQt5.QtWidgets import QDialog, QListWidget, QListWidgetItem


class InviteToRoomDialog(QDialog):
    list = None
    client_map = None

    def __init__(self, client_map):
        super(InviteToRoomDialog, self).__init__()

        self.client_map = client_map
        self.construct_ui()

    def construct_ui(self):
        self.list = QListWidget()

        for client in self.client_map:
            item = QListWidgetItem()
            item.setText(client)
            item.setData(0, self.client_map[client])
            self.list.addItem()