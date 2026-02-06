# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QMessageBox
from PyQt6.uic import loadUi
from kvalik_2.windows.client_window import ClientWindow
from kvalik_2.windows.admin_window import AdminWindow
from kvalik_2.windows.manager_window import ManagerWindow
from kvalik_2.database.db_utils import DbUtils
db = DbUtils()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('interfaces/auth_ui.ui', self)
        self.setWindowTitle('Окно авторизации')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.enter_button.clicked.connect(self.if_user_exists)

    def if_user_exists(self):
        login = self.login_input.text()
        password = self.password_input.text()
        if not login or not password:
            QMessageBox.warning(None, 'Ошибка', 'Не все данные введены!')
            return

        user = db.user_exists(login, password)

        if user:
            user_id, fio, role = user
            QMessageBox.information(None, 'Успех!', '{full_name}, добро пожаловать!'.format(
                full_name=fio
            ))
            self.open_role_window(user_id, role, fio)
        else:
            QMessageBox.critical(None, 'Ошибка', 'Неверный логин или пароль')

    def open_role_window(self, user_id, role, full_name):
        self.close()
        if role == 'Клиент':
            self.client_window = ClientWindow(user_id, full_name)
            self.client_window.show()
        elif role == 'Администратор':
            self.admin_window = AdminWindow(user_id, full_name)
            self.admin_window.show()
        elif role == 'Руководитель':
            self.manager_window = ManagerWindow(user_id, full_name)
            self.manager_window.show()
        else:
            QMessageBox.critical(None, 'Ошибка', 'Не удалось выполнить операцию')


