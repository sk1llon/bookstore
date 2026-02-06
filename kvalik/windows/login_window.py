# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QMainWindow, QDialog, QWidget, QMessageBox, QLineEdit, QLabel, QVBoxLayout, QPushButton
from PyQt6 import uic
from kvalik.database.db_utils import DbUtils
from kvalik.windows import employee_window, guest_window, manager_window
db = DbUtils()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('user interface/authorization_window.ui', self)
        self.enter_button.clicked.connect(self.get_user_info)

    def get_user_info(self):
        login = self.login_input.text()
        password = self.password_input.text()
        if not login or not password:
            QMessageBox.warning(None, 'Ошибка', 'Не все данные заполнены')
            return

        user = db.user_exists(login=login, password=password)

        if user:
            user_id, first_name, last_name, role = user
            full_name = '{ln} {fn}'.format(ln=last_name, fn=first_name)
            QMessageBox.information(None, 'Успех', '{full_name}, добро пожаловать!'.format(full_name=full_name))
            self.open_role_window(user_id, role, full_name)
        else:
            QMessageBox.warning(None, 'Ошибка', 'Неверный логин или пароль')

    @staticmethod
    def open_role_window(user_id, role, full_name):
        if role == 'Гость':
            g_win = guest_window.GuestWindow(user_id, full_name)
            g_win.show()
        elif role == 'Сотрудник':
            em_win = employee_window.EmployeeWindow(user_id, full_name)
            em_win.show()
        elif role == 'Руководитель':
            m_win = manager_window.ManagerWindow(user_id, full_name)
            m_win.show()
        else:
            QMessageBox.critical(None, 'Ошибка', 'Возникла ошибка при авторизации, обратитесь к администратору')