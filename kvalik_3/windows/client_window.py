# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QTableWidget
from PyQt6.uic import loadUi
from kvalik_3.database.db_utils import DbUtils
db_utils = DbUtils()


class ClientWindow(QMainWindow):
    def __init__(self, user_id, fio):
        super().__init__()
        self.user_id = user_id
        self.table = QTableWidget()
        self.fio = fio
        loadUi('interfaces/client_window.ui', self)
        self.setWindowTitle('{fio}'.format(fio=self.fio))

        self.my_orders_button.clicked.connect(self.show_user_orders)
        self.all_services_button.clicked.connect(self.show_all_services)

    def show_user_orders(self):
        orders = db_utils.get_client_orders(self.user_id)

        headers = ['ID', 'Автомобиль', 'Гос. номер', 'Механик', 'Дата создания',
                   'Плановая дата сдачи', 'Статус', 'Стоимость', 'Жалобы клиента']

        self.tableWidget.clear()
        self.tableWidget.setRowCount(len(orders))
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)

        for row_in, order in enumerate(orders):
            for col_in, value in enumerate(order):
                item = QTableWidgetItem(str(value) if not None else '')
                self.tableWidget.setItem(row_in, col_in, item)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.verticalHeader().setDefaultSectionSize(60)

        if not orders:
            QMessageBox.information(None, 'Информация', 'У вас нет текущих заказов')

    def show_all_services(self):
        services = db_utils.get_all_services()

        headers = ['ID', 'Название услуги', 'Категория услуги', 'Цена (руб)', 'Время (час)', 'Описание']

        self.tableWidget.clear()
        self.tableWidget.setRowCount(len(services))
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)

        for row_in, service in enumerate(services):
            for col_in, value in enumerate(service):
                item = QTableWidgetItem(str(value) if not None else '')
                self.tableWidget.setItem(row_in, col_in, item)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.verticalHeader().setDefaultSectionSize(60)

        if not services:
            QMessageBox.information(None, 'Информация', 'Список услуг пуст')
