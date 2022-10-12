# Qt GUI (Invite Dialog)
# Name: Matthew Jakeman
# UPI: mjak923
from PyQt5.QtCore import Qt, QByteArray
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QLabel, QToolBar, QPushButton, QVBoxLayout, QFileDialog, QScrollArea


class ImagePreviewDialog(QDialog):
    list = None
    app_state = None
    data = None

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.construct_ui()

    def construct_ui(self):

        vbox = QVBoxLayout()
        self.setWindowTitle("Image Preview")
        self.setFixedWidth(640)
        self.setFixedHeight(480)

        scroll = QScrollArea()
        vbox.addWidget(scroll)

        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(self.data))

        image = QLabel()
        image.setPixmap(pixmap)
        image.setAlignment(Qt.AlignCenter)
        scroll.setWidget(image)
        scroll.setWidgetResizable(True)

        button = QPushButton("Download")
        button.clicked.connect(self.download_image)
        vbox.addWidget(button)

        self.setLayout(vbox)

    def download_image(self):
        filename = QFileDialog.getSaveFileName(self, "Save image", "/", "Image files (*.png *.jpg)")

        try:
            with open(filename[0], "wb") as image:
                image.write(self.data)
        except:
            pass
