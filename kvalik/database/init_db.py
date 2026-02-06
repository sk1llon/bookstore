# -*- coding: utf-8 -*-
import sys
import sqlite3


class InitDatabase:
    def __init__(self, db_name='Hotel.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        try:
            self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS Users (
                                user_id integer PRIMARY KEY autoincrement,
                                login TEXT NOT NULL UNIQUE,
                                password TEXT,
                                role TEXT NOT NULL CHECK(role IN ('Гость', 'Сотрудник', 'Администратор', 'Руководитель')),
                                first_name TEXT NOT NULL,
                                last_name TEXT NOT NULL,
                                passport_data TEXT NOT NULL UNIQUE,
                                phone TEXT,
                                email TEXT,
                                loyalty_level INTEGER DEFAULT 0
                            )
                        """)

            self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS RoomTypes (
                                room_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                type_name TEXT NOT NULL,
                                description TEXT,
                                capacity INTEGER NOT NULL
                            )
                        """)

            self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS Rooms (
                                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                room_number TEXT NOT NULL UNIQUE,
                                room_type_id INTEGER NOT NULL,
                                status TEXT NOT NULL CHECK(status IN ('Свободен', 'Занят', 'Грязный', 'Назначен к уборке', 'Чистый')),
                                price_per_night REAL NOT NULL,
                                FOREIGN KEY (room_type_id) REFERENCES RoomTypes(room_type_id)
                            )
                        """)

            self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS Bookings (
                                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                room_id INTEGER NOT NULL,
                                check_in_date TEXT NOT NULL,
                                check_out_date TEXT NOT NULL,
                                status TEXT NOT NULL CHECK(status IN ('Подтверждено', 'Отменено', 'Завершено')),
                                total_price REAL NOT NULL,
                                FOREIGN KEY (user_id) REFERENCES Users(user_id),
                                FOREIGN KEY (room_id) REFERENCES Rooms(room_id)
                            )
                        """)

            self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS Services (
                                service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                service_name TEXT NOT NULL,
                                price REAL NOT NULL
                            )
                        """)

            self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS GuestServices (
                                guest_service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                booking_id INTEGER NOT NULL,
                                service_id INTEGER NOT NULL,
                                date_provided TEXT NOT NULL,
                                price REAL NOT NULL,
                                FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id),
                                FOREIGN KEY (service_id) REFERENCES Services(service_id)
                            )
                        """)

            self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS CleaningSchedule (
                                cleaning_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                room_id INTEGER NOT NULL,
                                user_id INTEGER NOT NULL,
                                cleaning_date TEXT NOT NULL,
                                status TEXT NOT NULL CHECK(status IN ('Назначено', 'Выполнено')),
                                FOREIGN KEY (room_id) REFERENCES Rooms(room_id),
                                FOREIGN KEY (user_id) REFERENCES Users(user_id)
                            )
                        """)

            print('Таблицы успешно созданы!')

            self.connection.commit()

        except Exception as exc:
            print('Не удалось создать таблицы в базе данных: {}'.format(exc))

    def fill_test_data(self):
        try:
            users = [
                (
                "admin", "admin", "Администратор", "Иван", "Иванов", "1234 567890", "+79001234567", "admin@example.com",
                0),
                ("manager", "manager", "Руководитель", "Петр", "Петров", "2345 678901", "+79002345678",
                 "manager@example.com", 0),
                ("client", "client", "Гость", "Сидор", "Сидоров", "3456 789012", "+79003456789", "client@example.com",
                 1),
                ("employee", "employee", "Сотрудник", "Алексей", "Алексеев", "4567 890123", "+79004567890",
                 "employee@example.com", 0),
            ]
            for login, password, role, first_name, last_name, passport, phone, email, loyalty in users:
                self.cursor.execute("""
                            INSERT OR IGNORE INTO Users (login, password, role, first_name, last_name, passport_data, phone, email, loyalty_level)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (login, password, role, first_name, last_name, passport, phone, email, loyalty))

            # Типы номеров
            room_types = [
                ("Стандарт", "Стандартный номер с одной кроватью", 2),
                ("Люкс", "Номер люкс с видом на море", 4),
                ("Семейный", "Семейный номер с двумя кроватями", 4),
            ]
            for type_name, description, capacity in room_types:
                self.cursor.execute("""
                            INSERT OR IGNORE INTO RoomTypes (type_name, description, capacity)
                            VALUES (?, ?, ?)
                        """, (type_name, description, capacity))

            # Номера
            rooms = [
                ("101", 1, 3500, "Свободен"),
                ("102", 1, 3500, "Свободен"),
                ("201", 2, 7000, "Свободен"),
                ("202", 2, 7000, "Занят"),
                ("301", 3, 5000, "Свободен"),
            ]
            for room_number, room_type_id, price, status in rooms:
                self.cursor.execute("""
                            INSERT OR IGNORE INTO Rooms (room_number, room_type_id, price_per_night, status)
                            VALUES (?, ?, ?, ?)
                        """, (room_number, room_type_id, price, status))

            # Услуги
            services = [
                ("Завтрак", 500),
                ("Трансфер", 1000),
                ("SPA", 2000),
            ]
            for service_name, price in services:
                self.cursor.execute("""
                            INSERT OR IGNORE INTO Services (service_name, price)
                            VALUES (?, ?)
                        """, (service_name, price))

            self.connection.commit()
            self.connection.close()
            print("База данных успешно заполнена тестовыми данными!")
        except sqlite3.Error as e:
            print(f"Ошибка при заполнении тестовыми данными: {e}")


# try:
#     db = InitDatabase()
#     db.create_tables()
#     db.fill_test_data()
# except Exception as exc:
#     print('Произошла ошибка: {}'.format(exc))
# finally:
#     sys.exit(0)
