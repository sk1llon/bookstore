# -*- coding: utf-8 -*-
import sys
from PyQt6.QtWidgets import QApplication
from kvalik.windows.login_window import LoginWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())



