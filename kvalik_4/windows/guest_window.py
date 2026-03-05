# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox
from PyQt6.uic import loadUi
from kvalik_4.database.db_utils import DbUtils
db = DbUtils()


class GuestWindow(QMainWindow):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window

        loadUi('interfaces/guest_window.ui', self)
        self.setWindowTitle('Окно гостя')

        self.exit_button.clicked.connect(self.exit)

        self.all_goods = list()

        self.load_goods()

    def load_goods(self):
        self.all_goods = db.get_all_goods()
        self.display_goods()

    def display_goods(self):
        headers = ['Артикул', 'Название', 'Категория', 'Производитель', 'Цена', 'Скидка', 'Количество на складе']

        self.guest_table.clear()
        self.guest_table.setRowCount(len(self.all_goods))
        self.guest_table.setColumnCount(len(headers))
        self.guest_table.setHorizontalHeaderLabels(headers)

        for row_in, good in enumerate(self.all_goods):
            for col_in, value in enumerate(good.values()):
                item = QTableWidgetItem(str(value) if value is not None else '')
                self.guest_table.setItem(row_in, col_in, item)

        self.guest_table.resizeColumnsToContents()

    def exit(self):
        self.close()
        self.login_window.show()
