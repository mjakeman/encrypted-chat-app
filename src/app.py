# Qt GUI
# Name: Matthew Jakeman
# UPI: mjak923

import sys
import traceback

from PyQt5.QtWidgets import (QApplication)

from app_connection import ConnectionWindow
from app_window import ChatWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = None

    if len(sys.argv) == 4:
        try:
            address = sys.argv[1]
            port = int(sys.argv[2])
            nickname = sys.argv[3]

            window = ChatWindow(address, port, nickname)
            window.show()
        except Exception as e:
            traceback.print_exception(e)
            print("Could not connect to server specified by command line arguments.")

            window = ConnectionWindow()
            window.show()
    else:
        window = ConnectionWindow()
        window.show()

    sys.exit(app.exec_())
