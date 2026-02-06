# -*- coding: utf-8 -*-
import sys
from PyQt6.QtWidgets import QApplication
from kvalik_3.windows.login_window import LoginWindow
from kvalik_3.database.init_db import InitDatabase
init_db = InitDatabase()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # init_db.create_tables()
    # init_db.fill_data()
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
