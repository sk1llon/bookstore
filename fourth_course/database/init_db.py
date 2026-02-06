# -*- coding: utf-8 -*-
import sqlite3

db_name = 'orgtehnika.db'


def init_db():
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute("""
    create table if not exists users(
        u_phone varchar(255) primary key,
        u_fio varchar(255),
        u_login varchar(255),
        u_password varchar(255),
        u_role varchar(255)
    );
    """)

    cursor.execute("""
    create table if not exists masters(
        master_id integer primary key autoincrement,
        user_id varchar(255),
        specialization varchar(255),
        foreign key (user_id) references users(u_phone)
    );
    """)

    cursor.execute("""
    create table if not exists requests(
        r_id integer primary key autoincrement,
        client_phone varchar(255),
        equipment_type varchar(255),
        equipment_model varchar(255),
        problem_description varchar(255),
        r_status varchar(255),
        priority varchar(255),
        master_id int,
        registration_date datetime default current_timestamp,
        completion_date datetime,
        foreign key (client_phone) references users(u_phone),
        foreign key (master_id) references masters(master_id)
    );
    """)

    connection.commit()
    connection.close()


init_db()
