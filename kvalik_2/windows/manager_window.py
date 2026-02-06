# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QMessageBox, QMainWindow, QTableWidgetItem
from PyQt6.QtCore import QDate
from PyQt6.uic import loadUi
from kvalik_2.database.db_utils import DbUtils

db = DbUtils()


class ManagerWindow(QMainWindow):
    def __init__(self, user_id, full_name):
        super().__init__()
        self.user_id = user_id
        self.full_name = full_name
        loadUi('interfaces/manager_ui.ui', self)
        self.setWindowTitle('Панель директора - {}'.format(self.full_name))
        
        # Хранение данных для фильтрации и сортировки
        self.orders_data = []
        self.services_data = []
        
        # Подключение кнопки расчёта среднего чека
        self.calculate_button.clicked.connect(self.calculate_average_check)
        
        # Установка дат по умолчанию (за последний месяц)
        self.end_date.setDate(QDate.currentDate())
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        
        # Подключение кнопок обновления
        self.refresh_orders_button.clicked.connect(self.load_orders)
        self.refresh_services_button.clicked.connect(self.load_services)
        
        # Подключение фильтров и поиска для заказов
        self.search_orders_input.textChanged.connect(self.filter_and_sort_orders)
        self.filter_orders_combo.currentIndexChanged.connect(self.filter_and_sort_orders)
        self.sort_orders_combo.currentIndexChanged.connect(self.filter_and_sort_orders)
        
        # Подключение фильтров и поиска для услуг
        self.search_services_input.textChanged.connect(self.filter_and_sort_services)
        self.filter_services_combo.currentIndexChanged.connect(self.filter_and_sort_services)
        self.sort_services_combo.currentIndexChanged.connect(self.filter_and_sort_services)
        
        # Загрузка данных
        self.load_orders()
        self.load_services()
        self.load_service_categories()

    def calculate_average_check(self):
        """Вычислить средний чек за выбранный период"""
        start = self.start_date.date().toString('yyyy-MM-dd')
        end = self.end_date.date().toString('yyyy-MM-dd')
        
        result = db.get_average_check(start, end)
        
        self.total_revenue_value.setText('{:.2f} руб.'.format(result['total_revenue']))
        self.completed_orders_value.setText(str(result['orders_count']))
        self.average_check_value.setText('{:.2f} руб.'.format(result['average_check']))
        
        if result['orders_count'] == 0:
            QMessageBox.information(
                self, 'Информация', 
                'За выбранный период нет завершённых заказов'
            )

    def load_orders(self):
        """Загрузить все заказы"""
        self.orders_data = db.get_all_orders()
        self.filter_and_sort_orders()

    def load_services(self):
        """Загрузить все услуги"""
        self.services_data = db.get_all_services()
        self.filter_and_sort_services()

    def load_service_categories(self):
        """Загрузить категории услуг в фильтр"""
        categories = db.get_service_categories()
        self.filter_services_combo.clear()
        self.filter_services_combo.addItem('Все')
        for category in categories:
            if category:
                self.filter_services_combo.addItem(category)

    def filter_and_sort_orders(self):
        """Фильтрация и сортировка заказов"""
        search_text = self.search_orders_input.text().lower()
        filter_status = self.filter_orders_combo.currentText()
        sort_option = self.sort_orders_combo.currentIndex()
        
        # Фильтрация
        filtered_data = []
        for order in self.orders_data:
            # Фильтр по статусу
            if filter_status != 'Все' and order[8] != filter_status:
                continue
            
            # Поиск по тексту
            if search_text:
                found = False
                for value in order:
                    if value and search_text in str(value).lower():
                        found = True
                        break
                if not found:
                    continue
            
            filtered_data.append(order)
        
        # Сортировка
        if sort_option == 0:  # По дате (новые)
            filtered_data.sort(key=lambda x: x[5] if x[5] else '', reverse=True)
        elif sort_option == 1:  # По дате (старые)
            filtered_data.sort(key=lambda x: x[5] if x[5] else '')
        elif sort_option == 2:  # По стоимости (возр.)
            filtered_data.sort(key=lambda x: float(x[9]) if x[9] else 0)
        elif sort_option == 3:  # По стоимости (убыв.)
            filtered_data.sort(key=lambda x: float(x[9]) if x[9] else 0, reverse=True)
        
        self.display_orders(filtered_data)

    def filter_and_sort_services(self):
        """Фильтрация и сортировка услуг"""
        search_text = self.search_services_input.text().lower()
        filter_category = self.filter_services_combo.currentText()
        sort_option = self.sort_services_combo.currentIndex()
        
        # Фильтрация
        filtered_data = []
        for service in self.services_data:
            # Фильтр по категории
            if filter_category != 'Все' and service[2] != filter_category:
                continue
            
            # Поиск по тексту
            if search_text:
                found = False
                for value in service:
                    if value and search_text in str(value).lower():
                        found = True
                        break
                if not found:
                    continue
            
            filtered_data.append(service)
        
        # Сортировка
        if sort_option == 0:  # По названию (А-Я)
            filtered_data.sort(key=lambda x: x[1] if x[1] else '')
        elif sort_option == 1:  # По названию (Я-А)
            filtered_data.sort(key=lambda x: x[1] if x[1] else '', reverse=True)
        elif sort_option == 2:  # По цене (возр.)
            filtered_data.sort(key=lambda x: float(x[3]) if x[3] else 0)
        elif sort_option == 3:  # По цене (убыв.)
            filtered_data.sort(key=lambda x: float(x[3]) if x[3] else 0, reverse=True)
        
        self.display_services(filtered_data)

    def display_orders(self, orders):
        """Отобразить заказы в таблице"""
        headers = ['ID', 'Клиент', 'Автомобиль', 'Гос. номер', 'Механик', 
                   'Дата создания', 'Плановая дата', 'Факт. дата', 'Статус', 
                   'Стоимость', 'Оплачено', 'Жалобы']
        
        self.orders_table.clear()
        self.orders_table.setColumnCount(len(headers))
        self.orders_table.setHorizontalHeaderLabels(headers)
        self.orders_table.setRowCount(len(orders))
        
        for row_idx, order in enumerate(orders):
            for col_idx, value in enumerate(order):
                item = QTableWidgetItem(str(value) if value is not None else '')
                self.orders_table.setItem(row_idx, col_idx, item)
        
        self.orders_table.resizeColumnsToContents()

    def display_services(self, services):
        """Отобразить услуги в таблице"""
        headers = ['ID', 'Название', 'Категория', 'Цена (руб.)', 'Время (ч.)', 'Описание']
        
        self.services_table.clear()
        self.services_table.setColumnCount(len(headers))
        self.services_table.setHorizontalHeaderLabels(headers)
        self.services_table.setRowCount(len(services))
        
        for row_idx, service in enumerate(services):
            for col_idx, value in enumerate(service):
                item = QTableWidgetItem(str(value) if value is not None else '')
                self.services_table.setItem(row_idx, col_idx, item)
        
        self.services_table.resizeColumnsToContents()
