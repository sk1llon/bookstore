# -*- coding: utf-8 -*-
import sqlite3
from kvalik_3.database.init_db import InitDatabase


class DbUtils(InitDatabase):
    def if_user_exists(self, mail, password):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                select 
                    id_client, fio, role
                from 
                    clients
                where 
                    email = ? and password = ?;
            """, (mail, password))
            result = cursor.fetchone()
            return result
        except sqlite3.Error as e:
            print('Ошибка при поиске пользователя: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_client_orders(self, client_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
            select
                wo.id_work_order,
                v.brand || ' ' || v.model as vehicle,
                v.license_plate,
                m.fio,
                wo.creation_date,
                wo.planned_completion_date,
                wo.status,
                wo.total_cost,
                wo.client_complaints
            from 
                work_orders wo
            left join vehicles v on wo.id_vehicle = v.id_vehicle
            left join mechanics m on wo.id_mechanic = m.id_mechanic
            where
                wo.id_client = ?
            order by wo.creation_date asc;
            """, (client_id,))
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print('Ошибка при поиске заказов пользователя: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_client_by_id(self, client_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
            select id_client, fio, phone, email, password
            from clients
            where id_client = ?;
            """, (client_id,))
            result = cursor.fetchone()
            return result
        except sqlite3.Error as e:
            print('Ошибка при поиске клиента: {}'.format(e))
            return None

    def get_all_clients(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                select 
                    id_client, fio, phone, email, registration_date
                from 
                    clients
                where 
                    role = 'Клиент'
                order by fio;
            """)
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print('Ошибка при получении данных о клиентах: {}'.format(e))
            return None
        finally:
            connection.close()

    def add_client(self, fio, phone, email, password):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                insert into clients(fio, phone, password, email, role, registration_date) values 
                (?, ?, ?, ?, 'Клиент', date('now'));
            """, (fio, phone, password, email))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Не удалось добавить нового клиента: {}'.format(e))
            return False
        finally:
            connection.close()

    def update_client(self, id_client, fio, phone, email, password=None):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            if password:
                cursor.execute("""
                    update clients
                    set fio = ?, phone = ?, password = ?, email = ?
                    where id_client = ?;
                """, (fio, phone, password, email, id_client))
            else:
                cursor.execute("""
                    update clients
                    set fio = ?, phone = ?, email = ?
                    where id_client = ?;
                """, (fio, phone, email, id_client))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при редактировании клиента: {}'.format(e))
            return False
        finally:
            connection.close()

    def get_client_list(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                select id_client, fio
                from clients
                where role = 'Клиент'
                order by fio;
            """)
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print('Не удалось найти пользователей: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_all_vehicles(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                select
                    v.id_vehicle,
                    c.fio,
                    v.brand,
                    v.model,
                    v.year,
                    v.vin,
                    v.license_plate,
                    v.current_mileage
                from
                    vehicles v
                left join clients c on v.id_client = c.id_client
                order by c.fio;
             """)
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print('Ошибка при получении данных о машинах: {}'.format(e))
            return None
        finally:
            connection.close()

    def add_vehicle(self, id_client, brand, model, year, vin, license_plate, current_mileage):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                insert into vehicles(id_client, brand, model, year, vin, license_plate, current_mileage)
                values (?, ?, ?, ?, ?, ?, ?)
            """, (id_client, brand, model, year, vin, license_plate, current_mileage))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при добавлении авто: {}'.format(e))
            return False
        finally:
            connection.close()

    def edit_vehicle(self, id_vehicle, id_client, brand, model, year, vin, license_plate, current_mileage):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                update vehicles
                set id_client = ?, brand = ?, model = ?, year = ?, vin = ?, license_plate = ?, current_mileage = ?
                where id_vehicle = ?;
            """, (id_client, brand, model, year, vin, license_plate, current_mileage, id_vehicle))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при редактировании авто: {}'.format(e))
            return False
        finally:
            connection.close()

    def get_vehicle_by_id(self, vehicle_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                select 
                    id_vehicle, id_client, brand, model, year, vin, license_plate, current_mileage
                from
                    vehicles
                where 
                    id_vehicle = ?;
            """, (vehicle_id,))
            result = cursor.fetchone()
            return result
        except sqlite3.Error as e:
            print('Ошибка при поиске авто: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_all_services(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
            select
                id_service,
                service_name,
                service_category,
                standard_price,
                estimated_time_hours,
                description
            from
                service_price_list
            order by
                service_name
            """)
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print('Ошибка при поиске услуг: {}'.format(e))
            return None
        finally:
            connection.close()
