# -*- coding: utf-8 -*-
import sys
from PyQt6.QtWidgets import QApplication
from kvalik_2.windows.login_window import LoginWindow
from kvalik_2.database.init_db import InitDatabase
init_db = InitDatabase()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
