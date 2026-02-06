# -*- coding: utf-8 -*-
from fourth_course.database import db_utils
from PyQt6.QtWidgets import QMainWindow, QWidget, QMessageBox, QLabel, QPushButton, QLineEdit, QVBoxLayout


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно авторизации")
        self.setGeometry(100, 100, 500, 350)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.login_label = QLabel('Логин')
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        self.password_label = QLabel('Пароль')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.enter_button = QPushButton('Войти')
        self.enter_button.clicked.connect(self.get_user_info)

        self.layout.addWidget(self.login_label)
        self.layout.addWidget(self.login_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.enter_button)

    def get_user_info(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        user = db_utils.if_user_exists(self, login, password)
        if user:
            phone_number, fio, role = user

        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

