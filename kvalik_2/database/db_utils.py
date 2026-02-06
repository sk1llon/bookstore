# -*- coding: utf-8 -*-
import sqlite3
from kvalik_2.database.init_db import InitDatabase


class DbUtils(InitDatabase):

    def user_exists(self, mail, password):
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

    # ==================== Методы для клиента ====================

    def get_client_orders(self, client_id):
        """Получить все заказы клиента"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT 
                    wo.id_work_order,
                    v.brand || ' ' || v.model as vehicle,
                    v.license_plate,
                    m.fio as mechanic,
                    wo.creation_date,
                    wo.planned_completion_date,
                    wo.status,
                    wo.total_cost,
                    wo.client_complaints
                FROM work_orders wo
                LEFT JOIN vehicles v ON wo.id_vehicle = v.id_vehicle
                LEFT JOIN mechanics m ON wo.id_mechanic = m.id_mechanic
                WHERE wo.id_client = ?
                ORDER BY wo.creation_date DESC
            """, (client_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print('Ошибка при получении заказов клиента: {}'.format(e))
            return []
        finally:
            connection.close()

    def get_all_services(self):
        """Получить прайс-лист всех услуг"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT 
                    id_service,
                    service_name,
                    service_category,
                    standard_price,
                    estimated_time_hours,
                    description
                FROM service_price_list
                ORDER BY service_category, service_name
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print('Ошибка при получении прайс-листа: {}'.format(e))
            return []
        finally:
            connection.close()

    # ==================== Методы для администратора и менеджера ====================

    def get_all_orders(self):
        """Получить все заказы"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT 
                    wo.id_work_order,
                    c.fio as client_name,
                    v.brand || ' ' || v.model as vehicle,
                    v.license_plate,
                    m.fio as mechanic,
                    wo.creation_date,
                    wo.planned_completion_date,
                    wo.actual_completion_date,
                    wo.status,
                    wo.total_cost,
                    wo.paid_amount,
                    wo.client_complaints
                FROM work_orders wo
                LEFT JOIN clients c ON wo.id_client = c.id_client
                LEFT JOIN vehicles v ON wo.id_vehicle = v.id_vehicle
                LEFT JOIN mechanics m ON wo.id_mechanic = m.id_mechanic
                ORDER BY wo.creation_date DESC
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print('Ошибка при получении заказов: {}'.format(e))
            return []
        finally:
            connection.close()

    def get_service_categories(self):
        """Получить все категории услуг"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT DISTINCT service_category 
                FROM service_price_list 
                WHERE service_category IS NOT NULL
                ORDER BY service_category
            """)
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print('Ошибка при получении категорий: {}'.format(e))
            return []
        finally:
            connection.close()

    # ==================== CRUD для клиентов ====================

    def get_all_clients(self):
        """Получить всех клиентов"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT id_client, fio, phone, email, registration_date
                FROM clients
                WHERE role = 'Клиент'
                ORDER BY fio
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print('Ошибка при получении клиентов: {}'.format(e))
            return []
        finally:
            connection.close()

    def add_client(self, fio, phone, email, password):
        """Добавить нового клиента"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO clients (fio, phone, email, password, role, registration_date)
                VALUES (?, ?, ?, ?, 'Клиент', date('now'))
            """, (fio, phone, email, password))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при добавлении клиента: {}'.format(e))
            return False
        finally:
            connection.close()

    def update_client(self, client_id, fio, phone, email, password=None):
        """Обновить данные клиента"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            if password:
                cursor.execute("""
                    UPDATE clients 
                    SET fio = ?, phone = ?, email = ?, password = ?
                    WHERE id_client = ?
                """, (fio, phone, email, password, client_id))
            else:
                cursor.execute("""
                    UPDATE clients 
                    SET fio = ?, phone = ?, email = ?
                    WHERE id_client = ?
                """, (fio, phone, email, client_id))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при обновлении клиента: {}'.format(e))
            return False
        finally:
            connection.close()

    def get_client_by_id(self, client_id):
        """Получить клиента по ID"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT id_client, fio, phone, email
                FROM clients
                WHERE id_client = ?
            """, (client_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print('Ошибка при получении клиента: {}'.format(e))
            return None
        finally:
            connection.close()

    # ==================== CRUD для автомобилей ====================

    def get_all_vehicles(self):
        """Получить все автомобили"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT 
                    v.id_vehicle,
                    c.fio as client_name,
                    v.brand,
                    v.model,
                    v.year,
                    v.vin,
                    v.license_plate,
                    v.current_mileage
                FROM vehicles v
                LEFT JOIN clients c ON v.id_client = c.id_client
                ORDER BY c.fio, v.brand, v.model
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print('Ошибка при получении автомобилей: {}'.format(e))
            return []
        finally:
            connection.close()

    def add_vehicle(self, client_id, brand, model, year, vin, license_plate, mileage):
        """Добавить новый автомобиль"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO vehicles 
                (id_client, brand, model, year, vin, license_plate, current_mileage)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (client_id, brand, model, year, vin, license_plate, mileage))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при добавлении автомобиля: {}'.format(e))
            return False
        finally:
            connection.close()

    def update_vehicle(self, vehicle_id, client_id, brand, model, year, vin, license_plate, mileage):
        """Обновить данные автомобиля"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE vehicles 
                SET id_client = ?, brand = ?, model = ?, year = ?, 
                    vin = ?, license_plate = ?, current_mileage = ?
                WHERE id_vehicle = ?
            """, (client_id, brand, model, year, vin, license_plate, mileage, vehicle_id))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при обновлении автомобиля: {}'.format(e))
            return False
        finally:
            connection.close()

    def get_vehicle_by_id(self, vehicle_id):
        """Получить автомобиль по ID"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT id_vehicle, id_client, brand, model, year, 
                       vin, license_plate, current_mileage
                FROM vehicles
                WHERE id_vehicle = ?
            """, (vehicle_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print('Ошибка при получении автомобиля: {}'.format(e))
            return None
        finally:
            connection.close()

    # ==================== Аналитика ====================

    def get_average_check(self, start_date, end_date):
        """Вычислить средний чек за период"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT 
                    SUM(total_cost) as total_revenue,
                    COUNT(*) as orders_count
                FROM work_orders
                WHERE status = 'Завершён' 
                  AND actual_completion_date BETWEEN ? AND ?
            """, (start_date, end_date))
            result = cursor.fetchone()
            
            if result and result[0] and result[1]:
                total_revenue = float(result[0])
                orders_count = int(result[1])
                average_check = total_revenue / orders_count if orders_count > 0 else 0
                return {
                    'total_revenue': total_revenue,
                    'orders_count': orders_count,
                    'average_check': average_check
                }
            return {'total_revenue': 0, 'orders_count': 0, 'average_check': 0}
        except sqlite3.Error as e:
            print('Ошибка при вычислении среднего чека: {}'.format(e))
            return {'total_revenue': 0, 'orders_count': 0, 'average_check': 0}
        finally:
            connection.close()

    # ==================== CRUD для услуг ====================

    def add_service(self, service_name, service_category, standard_price, estimated_time_hours, description):
        """Добавить новую услугу"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO service_price_list 
                (service_name, service_category, standard_price, estimated_time_hours, description)
                VALUES (?, ?, ?, ?, ?)
            """, (service_name, service_category, standard_price, estimated_time_hours, description))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при добавлении услуги: {}'.format(e))
            return False
        finally:
            connection.close()

    def update_service(self, service_id, service_name, service_category, standard_price, estimated_time_hours, description):
        """Обновить услугу"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE service_price_list 
                SET service_name = ?, service_category = ?, standard_price = ?, 
                    estimated_time_hours = ?, description = ?
                WHERE id_service = ?
            """, (service_name, service_category, standard_price, estimated_time_hours, description, service_id))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при обновлении услуги: {}'.format(e))
            return False
        finally:
            connection.close()

    def delete_service(self, service_id):
        """Удалить услугу"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM service_price_list WHERE id_service = ?", (service_id,))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при удалении услуги: {}'.format(e))
            return False
        finally:
            connection.close()

    # ==================== CRUD для заказов ====================

    def get_clients_list(self):
        """Получить список клиентов"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id_client, fio FROM clients WHERE role = 'Клиент' ORDER BY fio")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print('Ошибка при получении списка клиентов: {}'.format(e))
            return []
        finally:
            connection.close()

    def get_vehicles_by_client(self, client_id):
        """Получить автомобили клиента"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT id_vehicle, brand || ' ' || model || ' (' || license_plate || ')' 
                FROM vehicles WHERE id_client = ?
            """, (client_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print('Ошибка при получении автомобилей: {}'.format(e))
            return []
        finally:
            connection.close()

    def get_mechanics_list(self):
        """Получить список механиков"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id_mechanic, fio FROM mechanics ORDER BY fio")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print('Ошибка при получении списка механиков: {}'.format(e))
            return []
        finally:
            connection.close()

    def add_order(self, client_id, vehicle_id, mechanic_id, creation_date, planned_completion_date, 
                  status, total_cost, client_complaints):
        """Добавить новый заказ"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO work_orders 
                (id_client, id_vehicle, id_mechanic, creation_date, planned_completion_date, 
                 status, total_cost, paid_amount, client_complaints)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (client_id, vehicle_id, mechanic_id, creation_date, planned_completion_date, 
                  status, total_cost, client_complaints))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при добавлении заказа: {}'.format(e))
            return False
        finally:
            connection.close()

    def update_order(self, order_id, mechanic_id, planned_completion_date, actual_completion_date,
                     status, total_cost, paid_amount, client_complaints):
        """Обновить заказ"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE work_orders 
                SET id_mechanic = ?, planned_completion_date = ?, actual_completion_date = ?,
                    status = ?, total_cost = ?, paid_amount = ?, client_complaints = ?
                WHERE id_work_order = ?
            """, (mechanic_id, planned_completion_date, actual_completion_date,
                  status, total_cost, paid_amount, client_complaints, order_id))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при обновлении заказа: {}'.format(e))
            return False
        finally:
            connection.close()

    def delete_order(self, order_id):
        """Удалить заказ"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            # Сначала удаляем связанные записи
            cursor.execute("DELETE FROM work_order_services WHERE id_work_order = ?", (order_id,))
            cursor.execute("DELETE FROM used_parts WHERE id_work_order = ?", (order_id,))
            cursor.execute("DELETE FROM work_orders WHERE id_work_order = ?", (order_id,))
            connection.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка при удалении заказа: {}'.format(e))
            return False
        finally:
            connection.close()

    def get_order_by_id(self, order_id):
        """Получить заказ по ID"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT 
                    wo.id_work_order, wo.id_client, wo.id_vehicle, wo.id_mechanic,
                    wo.creation_date, wo.planned_completion_date, wo.actual_completion_date,
                    wo.status, wo.total_cost, wo.paid_amount, wo.client_complaints
                FROM work_orders wo
                WHERE wo.id_work_order = ?
            """, (order_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print('Ошибка при получении заказа: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_service_by_id(self, service_id):
        """Получить услугу по ID"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT id_service, service_name, service_category, 
                       standard_price, estimated_time_hours, description
                FROM service_price_list
                WHERE id_service = ?
            """, (service_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print('Ошибка при получении услуги: {}'.format(e))
            return None
        finally:
            connection.close()

