# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
db_name = 'kolesa.db'


class InitDatabase:
    @staticmethod
    def get_connection():
        return sqlite3.connect(db_name)

    def create_tables(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                create table if not exists clients(
                    id_client integer primary key autoincrement,
                    fio varchar(255),
                    phone varchar(20),
                    password varchar(255),
                    email varchar(255),
                    role varchar(255),
                    registration_date date
                );
                """)

            cursor.execute("""
                create table if not exists vehicles(
                    id_vehicle integer primary key autoincrement,
                    id_client integer,
                    brand varchar(255),
                    model varchar(255),
                    year year,
                    vin varchar(17),
                    license_plate varchar(20),
                    current_mileage integer,
                    foreign key(id_client) references clients(id_client)
                );
            """)

            cursor.execute("""
                create table if not exists mechanics(
                    id_mechanic integer primary key autoincrement,
                    fio varchar(255),
                    specialization varchar(255),
                    hourly_rate decimal(10, 2),
                    phone varchar(20),
                    hire_date date
                );
            """)

            cursor.execute("""
                create table if not exists work_orders(
                    id_work_order integer primary key autoincrement,
                    id_client integer,
                    id_vehicle integer,
                    id_mechanic integer,
                    creation_date date,
                    planned_completion_date date,
                    actual_completion_date date,
                    status varchar(20),
                    total_cost decimal(10, 2),
                    paid_amount decimal(10, 2),
                    current_mileage integer,
                    client_complaints varchar(255),
                    foreign key (id_client) references clients(id_client),
                    foreign key (id_vehicle) references vehicles(id_vehicle),
                    foreign key (id_mechanic) references mechanics(id_mechanic)
                );
            """)

            cursor.execute("""
                create table if not exists used_parts(
                    id_used_part integer primary key autoincrement,
                    id_work_order integer,
                    part_name varchar(255),
                    part_number varchar(255),
                    quantity integer,
                    unit_price decimal(10, 2), 
                    supplier varchar(255),
                    foreign key (id_work_order) references work_orders(id_work_order)
                );
            """)

            cursor.execute("""
                        create table if not exists service_price_list(
                            id_service integer primary key autoincrement,
                            service_name varchar(255), 
                            service_category varchar(255),
                            standard_price decimal(10, 2),
                            estimated_time_hours decimal(4, 2),
                            description varchar(255)
                        );
                    """)

            cursor.execute("""
                create table if not exists work_order_services(
                    id_wo_service integer primary key autoincrement,
                    id_work_order integer,
                    id_service integer,
                    quantity integer,
                    actual_price decimal(10, 2),
                    work_start_time datetime,
                    work_end_time datetime,
                    is_completed bool,
                    foreign key (id_work_order) references work_orders(id_work_order),
                    foreign key (id_service) references service_price_list(id_service)
                );
            """)
            print('Все таблицы успешно созданы!')
            connection.commit()
            connection.close()

        except sqlite3.Error as e:
            print('Произошла ошибка: {}'.format(e))

    def fill_data(self):
        try:
            clients_file = pd.read_excel('автосервис импорт.xlsx', sheet_name='клиенты')
            clients_file.to_sql('clients', con=self.get_connection(), if_exists='append', index=False)

            vehicles_file = pd.read_excel('автосервис импорт.xlsx', sheet_name='автомобили')
            vehicles_file.to_sql('vehicles', con=self.get_connection(), if_exists='append', index=False)

            mechanics_file = pd.read_excel('автосервис импорт.xlsx', sheet_name='механики')
            mechanics_file.to_sql('mechanics', con=self.get_connection(), if_exists='append', index=False)

            service_price_list_file = pd.read_excel('автосервис импорт.xlsx', sheet_name='прайс-лист')
            service_price_list_file.to_sql('service_price_list', con=self.get_connection(), if_exists='append', index=False)

            work_orders_file = pd.read_excel('автосервис импорт.xlsx', sheet_name='заказ-наряды')
            work_orders_file.to_sql('work_orders', con=self.get_connection(), if_exists='append', index=False)

            work_orders_services_file = pd.read_excel('автосервис импорт.xlsx', sheet_name='работы по заказ-наряду')
            work_orders_services_file.to_sql('work_order_services', con=self.get_connection(), if_exists='append', index=False)

            used_parts_file = pd.read_excel('автосервис импорт.xlsx', sheet_name='использованные запчасти')
            used_parts_file.to_sql('used_parts', con=self.get_connection(), if_exists='append', index=False)
            print('Все данные успешно добавлены')
        except Exception as exc:
            print('Произошла ошибка при добавлении данных: {}'.format(exc))
