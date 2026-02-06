# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QLineEdit
from PyQt6.uic import loadUi
from kvalik_3.windows.client_window import ClientWindow
from kvalik_3.windows.admin_window import AdminWindow
from kvalik_3.database.db_utils import DbUtils
db_utils = DbUtils()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('interfaces/login_window.ui', self)
        self.setWindowTitle('Окно авторизации')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.enter_button.clicked.connect(self.user_exists)

    def user_exists(self):
        mail = self.email_input.text()
        password = self.password_input.text()
        if not mail or not password:
            QMessageBox.warning(None, 'Предупреждение', 'Не все данные заполнены')
            return

        user = db_utils.if_user_exists(mail, password)

        if user:
            user_id, fio, role = user
            QMessageBox.information(None, 'Успех', '{fio}, Добро пожаловать!'.format(fio=fio))
            self.open_role_window(user_id, fio, role)
        else:
            QMessageBox.critical(None, 'Ошибка', 'Неверно введён логин или пароль')

    def open_role_window(self, user_id, fio, role):
        self.close()
        if role == 'Клиент':
            self.client_window = ClientWindow(user_id, fio)
            self.client_window.show()
        elif role == 'Администратор':
            self.admin_window = AdminWindow(user_id, fio)
            self.admin_window.show()
        else:
            QMessageBox.critical(None, 'Ошибка', 'Обратитесь к администратору')