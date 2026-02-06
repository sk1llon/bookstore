# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QMessageBox, QMainWindow, QTableWidgetItem, 
                             QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QDoubleSpinBox,
                             QDateEdit, QTextEdit, QSpinBox, QTableWidget)
from PyQt6.QtCore import QDate
from PyQt6.uic import loadUi
from kvalik_2.database.db_utils import DbUtils

db = DbUtils()



class AdminWindow(QMainWindow):
    def __init__(self, user_id, full_name):
        super().__init__()
        self.user_id = user_id
        self.full_name = full_name
        loadUi('interfaces/admin_ui.ui', self)
        self.setWindowTitle('Панель администратора - {}'.format(self.full_name))
        
        # Хранение данных
        self.clients_data = []
        self.vehicles_data = []
        self.orders_data = []
        self.services_data = []
        
        # Подключение кнопок для клиентов
        self.add_client_button.clicked.connect(self.add_client)
        self.edit_client_button.clicked.connect(self.edit_client)
        self.refresh_clients_button.clicked.connect(self.load_clients)
        
        # Подключение кнопок для автомобилей
        self.add_vehicle_button.clicked.connect(self.add_vehicle)
        self.edit_vehicle_button.clicked.connect(self.edit_vehicle)
        self.refresh_vehicles_button.clicked.connect(self.load_vehicles)
        
        # Подключение кнопок для заказов
        self.add_order_button.clicked.connect(self.add_order)
        self.edit_order_button.clicked.connect(self.edit_order)
        self.refresh_orders_button.clicked.connect(self.load_orders)
        
        # Подключение кнопки обновления для услуг
        self.refresh_services_button.clicked.connect(self.load_services)
        
        # Подключение поиска для клиентов
        self.search_clients_input.textChanged.connect(self.filter_clients)
        
        # Подключение поиска для автомобилей
        self.search_vehicles_input.textChanged.connect(self.filter_vehicles)
        
        # Подключение фильтров и поиска для заказов
        self.search_orders_input.textChanged.connect(self.filter_and_sort_orders)
        self.filter_orders_combo.currentIndexChanged.connect(self.filter_and_sort_orders)
        self.sort_orders_combo.currentIndexChanged.connect(self.filter_and_sort_orders)
        
        # Подключение фильтров и поиска для услуг
        self.search_services_input.textChanged.connect(self.filter_and_sort_services)
        self.filter_services_combo.currentIndexChanged.connect(self.filter_and_sort_services)
        self.sort_services_combo.currentIndexChanged.connect(self.filter_and_sort_services)
        
        # Загрузка данных
        self.load_clients()
        self.load_vehicles()
        self.load_orders()
        self.load_services()
        self.load_service_categories()

    # ==================== Клиенты ====================

    def load_clients(self):
        """Загрузить всех клиентов"""
        self.clients_data = db.get_all_clients()
        self.filter_clients()

    def filter_clients(self):
        """Фильтрация клиентов по поиску"""
        search_text = self.search_clients_input.text().lower()
        
        filtered_data = []
        for client in self.clients_data:
            if search_text:
                found = False
                for value in client:
                    if value and search_text in str(value).lower():
                        found = True
                        break
                if not found:
                    continue
            filtered_data.append(client)
        
        self.display_clients(filtered_data)

    def display_clients(self, clients):
        """Отобразить клиентов в таблице"""
        headers = ['ID', 'ФИО', 'Телефон', 'Email', 'Дата регистрации']
        
        self.clients_table.clear()
        self.clients_table.setColumnCount(len(headers))
        self.clients_table.setHorizontalHeaderLabels(headers)
        self.clients_table.setRowCount(len(clients))
        
        for row_idx, client in enumerate(clients):
            for col_idx, value in enumerate(client):
                item = QTableWidgetItem(str(value) if value is not None else '')
                self.clients_table.setItem(row_idx, col_idx, item)
        
        self.clients_table.resizeColumnsToContents()

    def add_client(self):
        """Добавить нового клиента"""
        dialog = ClientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if db.add_client(data['fio'], data['phone'], data['email'], data['password']):
                QMessageBox.information(self, 'Успех', 'Клиент успешно добавлен')
                self.load_clients()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось добавить клиента')

    def edit_client(self):
        """Редактировать выбранного клиента"""
        selected = self.clients_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите клиента для редактирования')
            return
        
        client_id = int(self.clients_table.item(selected, 0).text())
        client_data = db.get_client_by_id(client_id)
        
        if not client_data:
            QMessageBox.warning(self, 'Ошибка', 'Клиент не найден')
            return
        
        dialog = ClientDialog(self, client_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if db.update_client(client_id, data['fio'], data['phone'], data['email'], data.get('password')):
                QMessageBox.information(self, 'Успех', 'Данные клиента обновлены')
                self.load_clients()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось обновить данные')

    # ==================== Автомобили ====================

    def load_vehicles(self):
        """Загрузить все автомобили"""
        self.vehicles_data = db.get_all_vehicles()
        self.filter_vehicles()

    def filter_vehicles(self):
        """Фильтрация автомобилей по поиску"""
        search_text = self.search_vehicles_input.text().lower()
        
        filtered_data = []
        for vehicle in self.vehicles_data:
            if search_text:
                found = False
                for value in vehicle:
                    if value and search_text in str(value).lower():
                        found = True
                        break
                if not found:
                    continue
            filtered_data.append(vehicle)
        
        self.display_vehicles(filtered_data)

    def display_vehicles(self, vehicles):
        """Отобразить автомобили в таблице"""
        headers = ['ID', 'Владелец', 'Марка', 'Модель', 'Год', 'VIN', 'Гос. номер', 'Пробег']
        
        self.vehicles_table.clear()
        self.vehicles_table.setColumnCount(len(headers))
        self.vehicles_table.setHorizontalHeaderLabels(headers)
        self.vehicles_table.setRowCount(len(vehicles))
        
        for row_idx, vehicle in enumerate(vehicles):
            for col_idx, value in enumerate(vehicle):
                item = QTableWidgetItem(str(value) if value is not None else '')
                self.vehicles_table.setItem(row_idx, col_idx, item)
        
        self.vehicles_table.resizeColumnsToContents()

    def add_vehicle(self):
        """Добавить новый автомобиль"""
        dialog = VehicleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if db.add_vehicle(data['client_id'], data['brand'], data['model'], 
                            data['year'], data['vin'], data['license_plate'], data['mileage']):
                QMessageBox.information(self, 'Успех', 'Автомобиль успешно добавлен')
                self.load_vehicles()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось добавить автомобиль')

    def edit_vehicle(self):
        """Редактировать выбранный автомобиль"""
        selected = self.vehicles_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите автомобиль для редактирования')
            return
        
        vehicle_id = int(self.vehicles_table.item(selected, 0).text())
        vehicle_data = db.get_vehicle_by_id(vehicle_id)
        
        if not vehicle_data:
            QMessageBox.warning(self, 'Ошибка', 'Автомобиль не найден')
            return
        
        dialog = VehicleDialog(self, vehicle_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if db.update_vehicle(vehicle_id, data['client_id'], data['brand'], data['model'], 
                               data['year'], data['vin'], data['license_plate'], data['mileage']):
                QMessageBox.information(self, 'Успех', 'Данные автомобиля обновлены')
                self.load_vehicles()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось обновить данные')

    # ==================== Заказы ====================

    def load_orders(self):
        """Загрузить все заказы"""
        self.orders_data = db.get_all_orders()
        self.filter_and_sort_orders()

    def filter_and_sort_orders(self):
        """Фильтрация и сортировка заказов"""
        search_text = self.search_orders_input.text().lower()
        filter_status = self.filter_orders_combo.currentText()
        sort_option = self.sort_orders_combo.currentIndex()
        
        filtered_data = []
        for order in self.orders_data:
            if filter_status != 'Все' and order[8] != filter_status:
                continue
            
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
        if sort_option == 0:
            filtered_data.sort(key=lambda x: x[5] if x[5] else '', reverse=True)
        elif sort_option == 1:
            filtered_data.sort(key=lambda x: x[5] if x[5] else '')
        elif sort_option == 2:
            filtered_data.sort(key=lambda x: float(x[9]) if x[9] else 0)
        elif sort_option == 3:
            filtered_data.sort(key=lambda x: float(x[9]) if x[9] else 0, reverse=True)
        
        self.display_orders(filtered_data)

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

    def add_order(self):
        """Добавить новый заказ"""
        dialog = OrderDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if db.add_order(
                data['client_id'], data['vehicle_id'], data['mechanic_id'],
                data['creation_date'], data['planned_date'], data['status'],
                data['total_cost'], data['complaints']
            ):
                QMessageBox.information(self, 'Успех', 'Заказ успешно добавлен')
                self.load_orders()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось добавить заказ')

    def edit_order(self):
        """Редактировать выбранный заказ"""
        selected = self.orders_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите заказ для редактирования')
            return
        
        order_id = int(self.orders_table.item(selected, 0).text())
        order_data = db.get_order_by_id(order_id)
        
        if not order_data:
            QMessageBox.warning(self, 'Ошибка', 'Заказ не найден')
            return
        
        dialog = OrderDialog(self, order_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if db.update_order(
                order_id, data['mechanic_id'], data['planned_date'],
                data['actual_date'], data['status'], data['total_cost'],
                data['paid_amount'], data['complaints']
            ):
                QMessageBox.information(self, 'Успех', 'Заказ успешно обновлён')
                self.load_orders()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось обновить заказ')

    # ==================== Услуги ====================

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

    def filter_and_sort_services(self):
        """Фильтрация и сортировка услуг"""
        search_text = self.search_services_input.text().lower()
        filter_category = self.filter_services_combo.currentText()
        sort_option = self.sort_services_combo.currentIndex()
        
        filtered_data = []
        for service in self.services_data:
            if filter_category != 'Все' and service[2] != filter_category:
                continue
            
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
        if sort_option == 0:
            filtered_data.sort(key=lambda x: x[1] if x[1] else '')
        elif sort_option == 1:
            filtered_data.sort(key=lambda x: x[1] if x[1] else '', reverse=True)
        elif sort_option == 2:
            filtered_data.sort(key=lambda x: float(x[3]) if x[3] else 0)
        elif sort_option == 3:
            filtered_data.sort(key=lambda x: float(x[3]) if x[3] else 0, reverse=True)
        
        self.display_services(filtered_data)

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


# ==================== Диалоговые окна ====================

class ClientDialog(QDialog):
    """Диалог для добавления/редактирования клиента"""
    def __init__(self, parent=None, client_data=None):
        super().__init__(parent)
        self.client_data = client_data
        self.is_edit = client_data is not None
        
        loadUi('interfaces/client_dialog.ui', self)
        self.setWindowTitle('Редактировать клиента' if self.is_edit else 'Добавить клиента')
        
        # Подключение кнопок
        self.save_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)
        
        if self.is_edit:
            self.fill_data()
            self.password_input.setPlaceholderText('Оставьте пустым, чтобы не менять')

    def fill_data(self):
        """Заполнить данными при редактировании"""
        # client_data: (id, fio, phone, email)
        self.fio_input.setText(str(self.client_data[1]) if self.client_data[1] else '')
        self.phone_input.setText(str(self.client_data[2]) if self.client_data[2] else '')
        self.email_input.setText(str(self.client_data[3]) if self.client_data[3] else '')

    def validate_and_accept(self):
        """Проверка данных перед сохранением"""
        if not self.fio_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите ФИО клиента')
            return
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите телефон')
            return
        if not self.email_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите email')
            return
        if not self.is_edit and not self.password_input.text():
            QMessageBox.warning(self, 'Ошибка', 'Введите пароль')
            return
        self.accept()

    def get_data(self):
        """Получить введённые данные"""
        data = {
            'fio': self.fio_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'email': self.email_input.text().strip()
        }
        password = self.password_input.text().strip()
        if password or not self.is_edit:
            data['password'] = password
        return data


class VehicleDialog(QDialog):
    """Диалог для добавления/редактирования автомобиля"""
    def __init__(self, parent=None, vehicle_data=None):
        super().__init__(parent)
        self.vehicle_data = vehicle_data
        self.is_edit = vehicle_data is not None
        
        loadUi('interfaces/vehicle_dialog.ui', self)
        self.setWindowTitle('Редактировать автомобиль' if self.is_edit else 'Добавить автомобиль')
        
        # Подключение кнопок
        self.save_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Загрузка клиентов
        clients = db.get_clients_list()
        for client_id, name in clients:
            self.client_combo.addItem(name, client_id)
        
        if self.is_edit:
            self.fill_data()

    def fill_data(self):
        """Заполнить данными при редактировании"""
        # vehicle_data: (id, client_id, brand, model, year, vin, license_plate, mileage)
        
        # Найти клиента
        clients = db.get_clients_list()
        for i, (client_id, _) in enumerate(clients):
            if client_id == self.vehicle_data[1]:
                self.client_combo.setCurrentIndex(i)
                break
        
        self.brand_input.setText(str(self.vehicle_data[2]) if self.vehicle_data[2] else '')
        self.model_input.setText(str(self.vehicle_data[3]) if self.vehicle_data[3] else '')
        if self.vehicle_data[4]:
            self.year_input.setValue(int(self.vehicle_data[4]))
        self.vin_input.setText(str(self.vehicle_data[5]) if self.vehicle_data[5] else '')
        self.license_plate_input.setText(str(self.vehicle_data[6]) if self.vehicle_data[6] else '')
        if self.vehicle_data[7]:
            self.mileage_input.setValue(int(self.vehicle_data[7]))

    def validate_and_accept(self):
        """Проверка данных перед сохранением"""
        if not self.client_combo.currentData():
            QMessageBox.warning(self, 'Ошибка', 'Выберите клиента')
            return
        if not self.brand_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите марку автомобиля')
            return
        if not self.model_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите модель автомобиля')
            return
        self.accept()

    def get_data(self):
        """Получить введённые данные"""
        return {
            'client_id': self.client_combo.currentData(),
            'brand': self.brand_input.text().strip(),
            'model': self.model_input.text().strip(),
            'year': self.year_input.value(),
            'vin': self.vin_input.text().strip(),
            'license_plate': self.license_plate_input.text().strip(),
            'mileage': self.mileage_input.value()
        }


class OrderDialog(QDialog):
    """Диалог для добавления/редактирования заказа"""
    def __init__(self, parent=None, order_data=None):
        super().__init__(parent)
        self.order_data = order_data
        self.is_edit = order_data is not None
        
        loadUi('interfaces/order_dialog.ui', self)
        self.setWindowTitle('Редактировать заказ' if self.is_edit else 'Добавить заказ')
        
        # Скрываем поля для нового/редактирования
        if not self.is_edit:
            self.actual_date_label.setVisible(False)
            self.actual_date.setVisible(False)
            self.paid_amount_label.setVisible(False)
            self.paid_amount.setVisible(False)
        else:
            self.client_label.setVisible(False)
            self.client_combo.setVisible(False)
            self.vehicle_label.setVisible(False)
            self.vehicle_combo.setVisible(False)
        
        # Подключение кнопок
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Инициализация данных
        self.setup_data()
        
        if self.is_edit:
            self.fill_data()

    def setup_data(self):
        """Загрузка данных в комбобоксы"""
        self.planned_date.setDate(QDate.currentDate().addDays(7))
        
        if not self.is_edit:
            clients = db.get_clients_list()
            for client_id, name in clients:
                self.client_combo.addItem(name, client_id)
            self.client_combo.currentIndexChanged.connect(self.on_client_changed)
            self.on_client_changed()
        
        mechanics = db.get_mechanics_list()
        for mech_id, name in mechanics:
            self.mechanic_combo.addItem(name, mech_id)

    def on_client_changed(self):
        """Обновить список автомобилей при смене клиента"""
        if not self.is_edit:
            self.vehicle_combo.clear()
            client_id = self.client_combo.currentData()
            if client_id:
                vehicles = db.get_vehicles_by_client(client_id)
                for veh_id, name in vehicles:
                    self.vehicle_combo.addItem(name, veh_id)

    def fill_data(self):
        """Заполнить данными при редактировании"""
        # order_data: (id, client_id, vehicle_id, mechanic_id, creation_date, 
        #              planned_date, actual_date, status, total_cost, paid_amount, complaints)
        
        mechanics = db.get_mechanics_list()
        for i, (mech_id, _) in enumerate(mechanics):
            if mech_id == self.order_data[3]:
                self.mechanic_combo.setCurrentIndex(i)
                break
        
        if self.order_data[5]:
            date = QDate.fromString(str(self.order_data[5]), 'yyyy-MM-dd')
            self.planned_date.setDate(date)
        
        if self.order_data[6]:
            date = QDate.fromString(str(self.order_data[6]), 'yyyy-MM-dd')
            self.actual_date.setDate(date)
        
        status = self.order_data[7]
        statuses = ['Ожидает', 'В работе', 'Завершён']
        if status in statuses:
            self.status_combo.setCurrentIndex(statuses.index(status))
        
        if self.order_data[8]:
            self.total_cost.setValue(float(self.order_data[8]))
        if self.order_data[9]:
            self.paid_amount.setValue(float(self.order_data[9]))
        
        if self.order_data[10]:
            self.complaints.setPlainText(str(self.order_data[10]))

    def get_data(self):
        """Получить введённые данные"""
        data = {
            'mechanic_id': self.mechanic_combo.currentData(),
            'planned_date': self.planned_date.date().toString('yyyy-MM-dd'),
            'status': self.status_combo.currentText(),
            'total_cost': self.total_cost.value(),
            'complaints': self.complaints.toPlainText()
        }
        
        if not self.is_edit:
            data['client_id'] = self.client_combo.currentData()
            data['vehicle_id'] = self.vehicle_combo.currentData()
            data['creation_date'] = QDate.currentDate().toString('yyyy-MM-dd')
        else:
            data['actual_date'] = self.actual_date.date().toString('yyyy-MM-dd') if self.actual_date.date().isValid() else None
            data['paid_amount'] = self.paid_amount.value()
        
        return data
