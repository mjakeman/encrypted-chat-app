# Qt GUI (Upload Dialog)
# Name: Matthew Jakeman
# UPI: mjak923

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLineEdit, QProgressBar


class UploadResourceDialog(QDialog):
    title = None
    app_state = None

    def __init__(self, parent, app_state):
        super(UploadResourceDialog, self).__init__(parent)
        self.app_state = app_state

        self.construct_ui()

    def construct_ui(self):
        self.setWindowTitle("Upload Resource")

        vbox = QVBoxLayout()

        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(0)

        self.setLayout(vbox)

    def title_text(self):
        return self.title.text()