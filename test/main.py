# -*- coding: utf-8 -*-
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt

class GoodsTable(QTableWidget):
    def __init__(self):
        super().__init__(0, 10)
        self.setHorizontalHeaderLabels([
            "",
            "Категория", "Наименование", "Описание", "Производитель",
            "Поставщик", "Цена", "Ед. изм.", "Кол-во", "Скидка"
        ])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setDefaultSectionSize(80)

    def add_goods(self, photo_path, category, name, description, manufacturer, supplier, price, unit, quantity, discount):
        row_position = self.rowCount()
        self.insertRow(row_position)

        photo_label = QLabel()
        if photo_path:
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                photo_label.setPixmap(pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
            else:
                photo_label.setText("Нет фото")
                photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            photo_label.setText("Нет фото")
            photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setCellWidget(row_position, 0, photo_label)

        items = [
            category, name, description, manufacturer,
            supplier, str(price), unit, str(quantity), f"{discount}%"
        ]
        for col, item in enumerate(items, start=1):
            self.setItem(row_position, col, QTableWidgetItem(item))

        if quantity == 0:
            for col in range(1, self.columnCount()):
                self.item(row_position, col).setBackground(QColor(255, 100, 100))
        elif discount > 15:
            for col in range(1, self.columnCount()):
                self.item(row_position, col).setBackground(QColor(150, 255, 150))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Список товаров")
        self.setGeometry(100, 100, 1000, 600)

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        self.goods_table = GoodsTable()
        main_layout.addWidget(self.goods_table)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.add_example_goods()

    def add_example_goods(self):
        goods_list = [
            ("notebook.jpg", "Электроника", "Ноутбук", "Ноутбук для работы", "Dell", "ТехноМастер", 50000, "шт", 10, 0),
            ("smartphone.jpg", "Электроника", "Смартфон", "Смартфон с хорошей камерой", "Apple", "Связной", 70000, "шт", 5, 10),
            (None, "Бытовая техника", "Холодильник", "Двухкамерный холодильник", "Samsung", "МВидео", 45000, "шт", 0, 0),
            ("microwave.jpg", "Бытовая техника", "Микроволновка", "Микроволновка с грилем", "LG", "Эльдорадо", 12000, "шт", 15, 20),
            ("jacket.jpg", "Одежда", "Куртка", "Зимняя куртка", "The North Face", "Глория Джинс", 20000, "шт", 3, 5),
            (None, "Обувь", "Кроссовки", "Спортивная обувь", "Nike", "СпортМастер", 8000, "шт", 20, 0),
        ]

        for goods in goods_list:
            self.goods_table.add_goods(*goods)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


