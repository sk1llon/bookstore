# -*- coding: utf-8 -*-
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)

orders_data = [
    {
        "Артикул заказа": "ORD001",
        "Статус заказа": "В обработке",
        "Адрес пункта выдачи": "ул. Ленина, 10",
        "Дата заказа": "2023-10-01",
        "Дата доставки": "2023-10-05"
    },
    {
        "Артикул заказа": "ORD002",
        "Статус заказа": "Доставлен",
        "Адрес пункта выдачи": "ул. Гагарина, 25",
        "Дата заказа": "2023-10-02",
        "Дата доставки": "2023-10-06"
    },
    {
        "Артикул заказа": "ORD003",
        "Статус заказа": "Отменен",
        "Адрес пункта выдачи": "пр-т Мира, 5",
        "Дата заказа": "2023-10-03",
        "Дата доставки": ""
    },
    {
        "Артикул заказа": "ORD004",
        "Статус заказа": "В пути",
        "Адрес пункта выдачи": "ул. Пушкина, 15",
        "Дата заказа": "2023-10-04",
        "Дата доставки": "2023-10-08"
    }
]

class OrderWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Список заказов")
        self.setGeometry(100, 100, 800, 400)

        self.table = QTableWidget()
        self.table.setColumnCount(len(data[0]))
        self.table.setHorizontalHeaderLabels(data[0].keys())

        self.table.setRowCount(len(data))
        for i, order in enumerate(data):
            for j, key in enumerate(order.keys()):
                self.table.setItem(i, j, QTableWidgetItem(str(order[key])))

        layout = QVBoxLayout()
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = OrderWindow(orders_data)
    window.show()

    sys.exit(app.exec())



