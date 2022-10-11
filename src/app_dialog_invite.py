# Qt GUI (Invite Dialog)
# Name: Matthew Jakeman
# UPI: mjak923

from PyQt5.QtWidgets import QDialog, QListWidget, QListWidgetItem, QDialogButtonBox, QVBoxLayout, QListView


class InviteToRoomDialog(QDialog):
    list = None
    app_state = None

    def __init__(self, app_state):
        super(InviteToRoomDialog, self).__init__()

        self.app_state = app_state
        self.construct_ui()

    def construct_ui(self):
        self.setWindowTitle("Invite User")

        vbox = QVBoxLayout()

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.list = QListView()
        self.list.setModel(self.app_state.clients_model)
        vbox.addWidget(self.list)
        vbox.addWidget(button_box)

        self.setLayout(vbox)

    def client_id(self):
        index = self.list.currentIndex()
        item = self.app_state.clients_model.itemFromIndex(index)

        return item.data()
