# -*- coding: utf-8 -*-
import pymysql
import sys
from pymysql.err import Error
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from PyQt6.uic import loadUi


class DbUtils:
    @staticmethod
    def get_connection():
        try:
            connection = pymysql.connect(
                host='127.0.0.1',
                port=3306,
                user='root',
                password='root',
                database='cars',
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except Error as e:
            print('Ошибка при подключении к БД: {}'.format(e))
            return None

    def get_all_cars(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    select
                        c.car_id, 
                        m.name,
                        c.model,
                        c.car_year,
                        c.license_plate,
                        c.engine_volume
                    from
                        cars c 
                    left join manufactures m on c.brand_id = m.id_manufacture;
                """)
                return cursor.fetchall()
        except Error as e:
            print('Не удалось получить информацию об автомобилях: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_all_models(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                        select name
                        from manufactures;
                    """)
                return cursor.fetchall()
        except Error as e:
            print('Не удалось получить информацию о моделях: {}'.format(e))
            return None
        finally:
            connection.close()


db = DbUtils()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('main_ui.ui', self)
        self.setWindowTitle('Информация об автомобилях')

        self.cars_data = list()

        self.search_input.textChanged.connect(self.filter_and_sort)
        self.filter_input_combo.currentIndexChanged.connect(self.filter_and_sort)
        self.sort_input_combo.currentIndexChanged.connect(self.filter_and_sort)

        self.load_filter_combo()
        self.load_cars()

    def load_filter_combo(self):
        all_models = db.get_all_models()
        for values in all_models:
            self.filter_input_combo.addItem(values.get('name'))

    def load_cars(self):
        self.cars_data = db.get_all_cars()
        self.filter_and_sort()

    def filter_and_sort(self):
        search_text = self.search_input.text().lower()
        filter_status = self.filter_input_combo.currentText()
        sort_status = self.sort_input_combo.currentIndex()

        filtered_data = list()
        for car in self.cars_data:
            if filter_status != 'Все' and car['name'] != filter_status:
                continue

            if search_text:
                found = False
                for value in car:
                    if value and search_text in str(value).lower():
                        found = True
                        break
                if not found:
                    continue
            filtered_data.append(car)

        if sort_status == 0:
            filtered_data.sort(key=lambda x: x['car_year'] if x['car_year'] else '')
        elif sort_status == 1:
            filtered_data.sort(key=lambda x: x['car_year'] if x['car_year'] else '', reverse=True)

        self.display_cars(filtered_data)

    def display_cars(self, cars):
        headers = ['ID', 'Бренд', 'Модель', 'Год', 'Номер', 'Объём двигателя']

        self.car_table.clear()
        self.car_table.setRowCount(len(cars))
        self.car_table.setColumnCount(len(headers))
        self.car_table.setHorizontalHeaderLabels(headers)

        for row_in, car in enumerate(cars):
            for col_in, value in enumerate(car.values()):
                item = QTableWidgetItem(str(value) if value is not None else '')
                self.car_table.setItem(row_in, col_in, item)

        self.car_table.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
