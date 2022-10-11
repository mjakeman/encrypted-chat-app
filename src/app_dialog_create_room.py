# Qt GUI (Invite Dialog)
# Name: Matthew Jakeman
# UPI: mjak923

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLineEdit


class CreateRoomDialog(QDialog):
    title = None

    def __init__(self, parent):
        super(CreateRoomDialog, self).__init__(parent)
        self.construct_ui()

    def construct_ui(self):
        self.setWindowTitle("Create Room")

        vbox = QVBoxLayout()

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.title = QLineEdit()
        vbox.addWidget(self.title)
        vbox.addWidget(button_box)

        self.setLayout(vbox)

    def title_text(self):
        return self.title.text()