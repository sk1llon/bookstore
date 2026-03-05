import os

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

from database.db_utils import get_connection

UI_PATH = os.path.join(os.path.dirname(__file__), '..', 'interfaces', 'login_window.ui')
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_PATH, self)

        icon_path = os.path.join(PROJECT_DIR, 'resources', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        logo_path = os.path.join(PROJECT_DIR, 'resources', 'logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(
                100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.logo_label.setPixmap(pixmap)

        self.login_button.clicked.connect(self.login)
        self.guest_button.clicked.connect(self.enter_as_guest)

        self.catalog_window = None

    def login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not login or not password:
            QMessageBox.warning(
                self, "Ошибка ввода",
                "Пожалуйста, введите логин и пароль."
            )
            return

        try:
            conn = get_connection()
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM Users WHERE Login=%s AND Password=%s",
                        (login, password)
                    )
                    user = cursor.fetchone()

            if user:
                self.open_catalog(user)
            else:
                QMessageBox.warning(
                    self, "Ошибка авторизации",
                    "Неверный логин или пароль.\nПроверьте данные и попробуйте снова."
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка подключения",
                f"Не удалось подключиться к базе данных:\n{e}"
            )

    def enter_as_guest(self):
        self.open_catalog(None)

    def open_catalog(self, user):
        from windows.catalog_window import CatalogWindow
        self.catalog_window = CatalogWindow(user, self)
        self.catalog_window.show()
        self.hide()

    def on_return(self):
        self.login_input.clear()
        self.password_input.clear()
        self.catalog_window = None
        self.show()
