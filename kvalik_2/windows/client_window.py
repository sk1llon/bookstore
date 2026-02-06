# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QMessageBox, QMainWindow, QTableWidgetItem
from PyQt6.uic import loadUi
from kvalik_2.database.db_utils import DbUtils

db = DbUtils()


class ClientWindow(QMainWindow):
    def __init__(self, user_id, full_name):
        super().__init__()
        self.user_id = user_id
        self.full_name = full_name
        loadUi('interfaces/client_ui.ui', self)
        self.setWindowTitle('Личный кабинет - {}'.format(self.full_name))
        
        # Подключение кнопок
        self.my_orders_button.clicked.connect(self.show_my_orders)
        self.all_services_button.clicked.connect(self.show_all_services)

    def show_my_orders(self):
        """Показать заказы текущего клиента"""
        orders = db.get_client_orders(self.user_id)
        
        headers = ['ID', 'Автомобиль', 'Гос. номер', 'Механик', 'Дата создания', 
                   'Плановая дата', 'Статус', 'Стоимость', 'Жалобы клиента']
        
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setRowCount(len(orders))
        
        for row_idx, order in enumerate(orders):
            for col_idx, value in enumerate(order):
                item = QTableWidgetItem(str(value) if value is not None else '')
                self.tableWidget.setItem(row_idx, col_idx, item)
        
        self.tableWidget.resizeColumnsToContents()

        if not orders:
            QMessageBox.information(self, 'Информация', 'У вас пока нет заказов')

    def show_all_services(self):
        """Показать прайс-лист всех услуг"""
        services = db.get_all_services()

        headers = ['ID', 'Название услуги', 'Категория услуги', 'Цена', 'Время', 'Описание']

        self.tableWidget.clear()
        self.tableWidget.setRowCount(len(services))
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)

        for row_in, service in enumerate(services):
            for col_in, value in enumerate(service):
                item = QTableWidgetItem(str(value) if value is not None else '')
                self.tableWidget.setItem(row_in, col_in, item)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.verticalHeader().setDefaultSectionSize(60)

        if not services:
            QMessageBox.warning(None, 'Информация', 'Список услуг пуст')





