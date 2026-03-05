import os

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QHeaderView
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from database.db_utils import get_connection

UI_PATH = os.path.join(os.path.dirname(__file__), '..', 'interfaces', 'orders_window.ui')
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')

ORDER_COLUMNS = [
    'ID заказа', 'Клиент', 'Статус', 'Адрес доставки',
    'Дата заказа', 'Дата выдачи', 'Состав заказа'
]


class OrdersWindow(QWidget):
    def __init__(self, role, parent_window):
        super().__init__()
        uic.loadUi(UI_PATH, self)

        self.role = role
        self.parent_window = parent_window
        self.order_form = None
        self.all_orders = []

        icon_path = os.path.join(PROJECT_DIR, 'resources', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._setup_ui()
        self._connect_signals()
        self.load_orders()

    def _setup_ui(self):
        is_admin = self.role == 'admin'
        self.add_order_button.setVisible(is_admin)
        self.delete_order_button.setVisible(is_admin)

        self.orders_table.setColumnCount(len(ORDER_COLUMNS))
        self.orders_table.setHorizontalHeaderLabels(ORDER_COLUMNS)
        header = self.orders_table.horizontalHeader()
        for i in range(len(ORDER_COLUMNS)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

    def _connect_signals(self):
        self.back_button.clicked.connect(self._go_back)

        if self.role == 'admin':
            self.add_order_button.clicked.connect(self._open_add_form)
            self.delete_order_button.clicked.connect(self._delete_order)
            self.orders_table.doubleClicked.connect(self._open_edit_form)

    def load_orders(self):
        try:
            conn = get_connection()
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT o.OrderID, o.UserID, u.FIO AS ClientName,
                               o.Status, o.DeliveryAddress, o.OrderDate, o.IssueDate
                        FROM Orders o
                        JOIN Users u ON o.UserID = u.UserID
                        ORDER BY o.OrderDate DESC
                    """)
                    self.all_orders = cursor.fetchall()

                    for order in self.all_orders:
                        cursor.execute("""
                            SELECT b.Title, oi.Quantity
                            FROM OrderItems oi
                            JOIN Books b ON oi.BookID = b.BookID
                            WHERE oi.OrderID = %s
                        """, (order['OrderID'],))
                        items = cursor.fetchall()
                        order['Items'] = items

            self._update_table()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заказы:\n{e}")

    def _update_table(self):
        self.orders_table.setRowCount(0)
        self.orders_table.setRowCount(len(self.all_orders))

        for row, order in enumerate(self.all_orders):
            id_item = QTableWidgetItem(str(order['OrderID']))
            id_item.setData(Qt.ItemDataRole.UserRole, order['OrderID'])
            self.orders_table.setItem(row, 0, id_item)
            self.orders_table.setItem(row, 1, QTableWidgetItem(str(order['ClientName'])))
            self.orders_table.setItem(row, 2, QTableWidgetItem(str(order['Status'])))
            self.orders_table.setItem(row, 3, QTableWidgetItem(str(order['DeliveryAddress'] or '')))
            self.orders_table.setItem(row, 4, QTableWidgetItem(str(order['OrderDate'])))
            self.orders_table.setItem(row, 5, QTableWidgetItem(str(order['IssueDate'] or '—')))

            items_text = '; '.join(
                f"{item['Title']} x{item['Quantity']}" for item in order.get('Items', [])
            )
            self.orders_table.setItem(row, 6, QTableWidgetItem(items_text))

        self.count_label.setText(f"Заказов: {len(self.all_orders)}")

    def _open_add_form(self):
        if self.order_form and self.order_form.isVisible():
            QMessageBox.information(
                self, "Внимание",
                "Окно редактирования заказа уже открыто."
            )
            self.order_form.activateWindow()
            return

        from windows.order_form import OrderForm
        self.order_form = OrderForm(parent_window=self)
        self.order_form.show()

    def _open_edit_form(self):
        if self.role != 'admin':
            return

        row = self.orders_table.currentRow()
        if row < 0:
            return

        if self.order_form and self.order_form.isVisible():
            QMessageBox.information(
                self, "Внимание",
                "Окно редактирования заказа уже открыто."
            )
            self.order_form.activateWindow()
            return

        order_id = self.orders_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        order = next((o for o in self.all_orders if o['OrderID'] == order_id), None)
        if order:
            from windows.order_form import OrderForm
            self.order_form = OrderForm(order=order, parent_window=self)
            self.order_form.show()

    def _delete_order(self):
        row = self.orders_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Информация", "Выберите заказ для удаления.")
            return

        order_id = self.orders_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить заказ №{order_id}?\n"
            "Это действие необратимо.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = get_connection()
                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute("DELETE FROM OrderItems WHERE OrderID=%s", (order_id,))
                        cursor.execute("DELETE FROM Orders WHERE OrderID=%s", (order_id,))
                    conn.commit()

                QMessageBox.information(self, "Успешно", "Заказ успешно удалён.")
                self.load_orders()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить заказ:\n{e}")

    def _go_back(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()

    def closeEvent(self, event):
        if self.order_form and self.order_form.isVisible():
            self.order_form.close()
        if self.parent_window:
            self.parent_window.show()
        super().closeEvent(event)
