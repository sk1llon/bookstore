# -*- coding: utf-8 -*-
import pymysql
from pymysql.err import Error
from pymysql.cursors import DictCursor


class DbUtils:
    @staticmethod
    def get_connection():
        try:
            connection = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='root',
                database='obuvnoy',
                cursorclass=DictCursor
            )
            return connection
        except Error as e:
            print('Ошибка при подключении к БД: {}'.format(e))
            return None

    def if_user_exists(self, login, password):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    select
                        user_id, fio, role
                    from 
                        users
                    where
                        login = %s and password = %s;
                """, (login, password))
                return cursor.fetchone()
        except Error as e:
            print('Не удалось найти пользователя: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_all_user_names(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    select user_id, fio
                    from users
                    where role = 'Клиент'
                    order by fio;
                """)
                return cursor.fetchall()
        except Error as e:
            print('Не удалось получить информацию о пользователях: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_all_goods(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    select
                        articul, name, category, producer, price, discount, amount_in_storage, description
                    from
                        goods
                    order by articul;
                """)
                return cursor.fetchall()
        except Error as e:
            print('Не удалось получить информацию о товарах: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_all_orders(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    select
                        o.order_id,
                        GROUP_CONCAT(oi.articul, ' - ', oi.quantity, ' шт.' SEPARATOR ', ') as content,
                        o.order_date,
                        o.delivery_date,
                        p.address,
                        u.fio,
                        o.order_code,
                        o.status,
                        ROUND(SUM(g.price * oi.quantity * (1 - g.discount / 100)), 2) as total
                    from orders o
                    join order_items oi on o.order_id = oi.order_id
                    join pvz p on o.pvz_id = p.pvz_id
                    join users u on o.user_id = u.user_id
                    join goods g on oi.articul = g.articul
                    group by o.order_id;
                """)
                return cursor.fetchall()
        except Error as e:
            print('Не удалось получить информацию о заказах: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_all_brands(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    select producer
                    from goods;
                """)
                return cursor.fetchall()
        except Error as e:
            print('Не удалось получить информацию о брендах: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_all_statuses(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    select status
                    from orders;
                """)
                return cursor.fetchall()
        except Error as e:
            print('Не удалось получить информацию о статусах: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_all_pvz(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    select pvz_id, address
                    from pvz;
                """)
                return cursor.fetchall()
        except Error as e:
            print('Не удалось получить информацию о пунктах выдачи: {}'.format(e))
            return None
        finally:
            connection.close()

    def get_good_by_article(self, article):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    select 
                        articul, name, price, supplier, producer, category, discount, amount_in_storage, description
                    from
                        goods
                    where articul = %s;
                """, (article,))
                return cursor.fetchone()
        except Error as e:
            print('Не удалось найти товар: {}'.format(e))
            return None
        finally:
            connection.close()

    def add_goods(self, art, name, price, supplier, producer, category, discount, amount, description):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    insert into goods(articul, name, price, supplier, producer, 
                    category, discount, amount_in_storage, description)
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (art, name, price, supplier, producer, category, discount, amount, description))
                connection.commit()
                return True
        except Error as e:
            print('Не удалось добавить товар: {}'.format(e))
            return False
        finally:
            connection.close()

    def update_goods(self, article, name, price, supplier, producer, category, discount, amount, description):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    update goods
                    set name = %s, price = %s, supplier = %s, producer = %s, 
                    category = %s, discount = %s, amount_in_storage = %s, description = %s
                    where articul = %s;
                """, (name, price, supplier, producer, category, discount, amount, description, article))
                connection.commit()
                return True
        except Error as e:
            print('Не удалось обновить данные: {}'.format(e))
            return False
        finally:
            connection.close()

    def delete_good(self, article):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    delete from order_items
                    where articul = %s;
                """, (article,))

                cursor.execute("""
                    delete from goods
                    where articul = %s;
                """, (article,))
                connection.commit()
                return True
        except Error as e:
            print('Не удалось удалить товар: {}'.format(e))
            return False
        finally:
            connection.close()

    def delete_order(self, order_id):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    delete from order_items
                    where order_id = %s;
                """, (order_id,))

                cursor.execute("""
                    delete from orders
                    where order_id = %s;
                """, (order_id,))
                connection.commit()
                return True
        except Error as e:
            print('Не удалось удалить заказ: {}'.format(e))
            return False
        finally:
            connection.close()

    def get_good_for_cart(self, article):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    select articul, name, producer, price
                    from goods
                    where articul = %s;
                """, (article,))
                return cursor.fetchone()
        except Error as e:
            print('Не удалось получить информацию о товаре: {}'.format(e))
            return None
        finally:
            connection.close()

    def add_order(self, delivery_date, pvz_id, user_id, order_code, status, cart_items):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    insert into orders(order_date, delivery_date, pvz_id, user_id, order_code, status)
                    values (CURDATE(), %s, %s, %s, %s, %s);
                """, (delivery_date, pvz_id, user_id, order_code, status))

                order_id = cursor.lastrowid

                for item in cart_items:
                    cursor.execute("""
                        insert into order_items(order_id, articul, quantity)
                        values (%s, %s, %s)
                    """, (order_id, item['articul'], item['quantity']))
                connection.commit()
                return True
        except Error as e:
            print('Не удалось добавить данные о заказе: {}'.format(e))
            return False
        finally:
            connection.close()
