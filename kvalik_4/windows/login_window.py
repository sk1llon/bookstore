# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi
from kvalik_4.database.db_utils import DbUtils
from kvalik_4.windows.guest_window import GuestWindow
from kvalik_4.windows.client_window import ClientWindow
from kvalik_4.windows.admin_window import AdminWindow
db = DbUtils()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('interfaces/login_window.ui', self)
        self.setWindowTitle('Окно авторизации')

        self.enter_button.clicked.connect(self.if_user_exists)
        self.guest_button.clicked.connect(self.guest_window)

    def guest_window(self):
        self.close()
        self.open_guest_window = GuestWindow(self)
        self.open_guest_window.show()

    def if_user_exists(self):
        login = self.email_input.text()
        password = self.password_input.text()

        if not login or not password:
            QMessageBox.warning(self, 'Ошибка', 'Не все данные введены')
            return

        user = db.if_user_exists(login, password)

        if user:
            user_id, fio, role = user['user_id'], user['fio'], user['role']
            QMessageBox.information(self, 'Успех', '{}, Добро пожаловать!'.format(fio))
            self.open_role_window(user_id, fio, role)

        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

    def open_role_window(self, user_id, fio, role):
        self.close()
        if role == 'Клиент':
            self.client_window = ClientWindow(self, user_id, fio)
            self.client_window.show()
        elif role == 'Администратор':
            self.admin_window = AdminWindow(self, user_id, fio)
            self.admin_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Обратитесь к администратору')
