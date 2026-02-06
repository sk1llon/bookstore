# -*- coding: utf-8 -*-
import sqlite3

from kvalik.database.init_db import InitDatabase
from PyQt6.QtWidgets import QMessageBox


class DbUtils(InitDatabase):
    def __init__(self):
        super().__init__()

    def user_exists(self, login, password):
        try:
            self.cursor.execute("""
            select 
                user_id, first_name, last_name, role
            from 
                users
            where 
                login = ? and password = ?
            """, (login, password))

            user = self.cursor.fetchone()

            return user
        except sqlite3.Error as e:
            print('Произошла ошибка: {}'.format(e))


