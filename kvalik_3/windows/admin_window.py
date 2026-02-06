# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QDialog
from PyQt6.uic import loadUi
from kvalik_3.database.db_utils import DbUtils
db = DbUtils()


class AdminWindow(QMainWindow):
    def __init__(self, user_id, fio):
        super().__init__()
        self.user_id = user_id
        self.fio = fio
        loadUi('interfaces/admin_window.ui', self)
        self.setWindowTitle('{fio} - панель администратора'.format(fio=self.fio))

        self.client_data = list()
        self.vehicle_data = list()
        self.order_data = list()
        self.service_data = list()

        self.add_client_button.clicked.connect(self.add_client)
        self.edit_client_button.clicked.connect(self.edit_client)
        self.refresh_client_button.clicked.connect(self.load_clients)

        self.add_vehicle_button.clicked.connect(self.add_vehicle)
        self.edit_vehicle_button.clicked.connect(self.edit_vehicle)
        self.refresh_client_button.clicked.connect(self.load_vehicles)

        self.load_clients()
        self.load_vehicles()
        self.load_orders()
        self.load_services()

    # Кнопки клиентов
    def load_clients(self):
        self.client_data = db.get_all_clients()
        self.display_clients()

    def display_clients(self):
        headers = ['ID', 'ФИО', 'Номер телефона', 'Почта', 'Дата регистрации']

        self.client_table.clear()
        self.client_table.setRowCount(len(self.client_data))
        self.client_table.setColumnCount(len(headers))
        self.client_table.setHorizontalHeaderLabels(headers)

        for row_in, client in enumerate(self.client_data):
            for col_in, value in enumerate(client):
                item = QTableWidgetItem(str(value) if not None else '')
                self.client_table.setItem(row_in, col_in, item)

        self.client_table.resizeColumnsToContents()

    def add_client(self):
        dialog = ClientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if db.add_client(data['fio'], data['phone'], data['email'], data['password']):
                QMessageBox.information(self, 'Успех', 'Данные успешно добавлены')
                self.load_clients()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось добавить клиента')

    def edit_client(self):
        selected = self.client_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите клиента для редактирования')
            return

        client_id = int(self.client_table.item(selected, 0).text())
        client_data = db.get_client_by_id(client_id)

        if not client_data:
            QMessageBox.warning(self, 'Ошибка', 'Не удалось найти пользователя')
            return

        dialog = ClientDialog(self, client_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if db.update_client(client_id, data['fio'], data['phone'], data['email'], data.get('password')):
                QMessageBox.information(self, 'Успех', 'Данные успешно обновлены')
                self.load_clients()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось обновить данные')

    # Кнопки машин
    def load_vehicles(self):
        self.vehicle_data = db.get_all_vehicles()
        self.display_vehicles()

    def display_vehicles(self):
        headers = ['ID', 'ФИО клиента', 'Марка автомобиля', 'Модель автомобиля', 'Год выпуска',
                   'VIN-номер', 'Номер автомобиля', 'Пробег']

        self.vehicle_table.clear()
        self.vehicle_table.setRowCount(len(self.vehicle_data))
        self.vehicle_table.setColumnCount(len(headers))
        self.vehicle_table.setHorizontalHeaderLabels(headers)

        for row_in, vehicle in enumerate(self.vehicle_data):
            for col_in, value in enumerate(vehicle):
                item = QTableWidgetItem(str(value) if not None else '')
                self.vehicle_table.setItem(row_in, col_in, item)

        self.vehicle_table.resizeColumnsToContents()

    def add_vehicle(self):
        dialog = VehicleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if db.add_vehicle(data['id_client'], data['brand'], data['model'], data['year'],
                              data['vin'], data['license_plate'], data['mileage']):
                QMessageBox.information(self, 'Успех', 'Автомобиль успешно добавлен')
                self.load_vehicles()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось добавить автомобиль')

    def edit_vehicle(self):
        selected = self.vehicle_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите автомобиль для редактирования')
            return

        vehicle_id = int(self.vehicle_table.item(selected, 0).text())
        vehicle_data = db.get_vehicle_by_id(vehicle_id)

        if not vehicle_data:
            QMessageBox.warning(self, 'Ошибка', 'Не удалось найти авто')
            return

        dialog = VehicleDialog(self, vehicle_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if db.edit_vehicle(vehicle_id, data['id_client'], data['brand'], data['model'], data['year'],
                               data['vin'], data['license_plate'], data['mileage']):
                QMessageBox.information(self, 'Успех', 'Данные успешно обновлены')
                self.load_vehicles()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось обновить данные')

    # Кнопки заказов
    def load_orders(self):
        pass

    # Кнопки услуг
    def load_services(self):
        pass


class ClientDialog(QDialog):
    def __init__(self, parent=None, client_data=None):
        super().__init__(parent)
        self.client_data = client_data
        self.is_edit = client_data is not None

        loadUi('interfaces/client_dialog.ui', self)
        self.setWindowTitle('Редактировать клиента' if self.is_edit else 'Добавить клиента')

        self.save_button.clicked.connect(self.validate_and_accept)
        self.reject_button.clicked.connect(self.reject)

        if self.is_edit:
            self.fill_data()
            self.password_input.setPlaceholderText('Оставьте пустым, чтобы не менять')

    def fill_data(self):
        self.fio_input.setText(str(self.client_data[1]) if self.client_data[1] else '')
        self.phone_input.setText(str(self.client_data[2]) if self.client_data[2] else '')
        self.email_input.setText(str(self.client_data[3]) if self.client_data[3] else '')

    def validate_and_accept(self):
        if not self.fio_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите ФИО клиента')
            return
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите номер телефона')
            return
        if not self.email_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите почту')
            return
        if not self.is_edit and not self.password_input.text():
            QMessageBox.warning(self, 'Ошибка', 'Введите пароль')
            return
        self.accept()

    def get_data(self):
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
    def __init__(self, parent=None, vehicle_data=None):
        super().__init__(parent)
        self.vehicle_data = vehicle_data
        self.is_edit = vehicle_data is not None

        loadUi('interfaces/vehicle_dialog.ui', self)
        self.setWindowTitle('Редактирование авто' if self.is_edit else 'Добавление авто')

        self.save_button.clicked.connect(self.validate_and_accept)
        self.reject_button.clicked.connect(self.reject)

        client_list = db.get_client_list()
        for client_id, fio in client_list:
            self.client_input_combo.addItem(fio, client_id)

        if self.is_edit:
            self.fill_data()

    def fill_data(self):
        client_list = db.get_client_list()
        for i, (client_id, _) in enumerate(client_list):
            if client_id == self.vehicle_data[1]:
                self.client_input_combo.setCurrentIndex(i)
                break

        self.brand_input.setText(str(self.vehicle_data[2] if self.vehicle_data[2] else ''))
        self.model_input.setText(str(self.vehicle_data[3] if self.vehicle_data[3] else ''))
        if self.vehicle_data[4]:
            self.year_input_spin.setValue(int(self.vehicle_data[4]))
        self.vin_input.setText(str(self.vehicle_data[5] if self.vehicle_data[5] else ''))
        self.license_plate_input.setText(str(self.vehicle_data[6] if self.vehicle_data[6] else ''))
        if self.vehicle_data[7]:
            self.mileage_input_spin.setValue(int(self.vehicle_data[7]))

    def validate_and_accept(self):
        if not self.client_input_combo.currentData():
            QMessageBox.warning(self, 'Ошибка', 'Выберите клиента')
            return
        if not self.brand_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите марку')
            return
        if not self.model_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите модель')
            return
        if not self.vin_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите VIN-номер')
            return
        if not self.license_plate_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите номер авто')
            return
        self.accept()

    def get_data(self):
        data = {
            'id_client': self.client_input_combo.currentData(),
            'brand': self.brand_input.text().strip(),
            'model': self.model_input.text().strip(),
            'year': self.year_input_spin.value(),
            'vin': self.vin_input.text().strip(),
            'license_plate': self.license_plate_input.text().strip(),
            'mileage': self.mileage_input_spin.value()
        }
        return data
