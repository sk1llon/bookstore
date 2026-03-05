import os
from datetime import date

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QDate

from database.db_utils import get_connection

UI_PATH = os.path.join(os.path.dirname(__file__), '..', 'interfaces', 'order_form.ui')
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')

ORDER_STATUSES = ['Новый', 'В обработке', 'Выдан', 'Отменён']


class OrderForm(QWidget):
    def __init__(self, order=None, parent_window=None):
        super().__init__()
        uic.loadUi(UI_PATH, self)

        self.order = order
        self.parent_window = parent_window

        icon_path = os.path.join(PROJECT_DIR, 'resources', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._load_combos()
        self._connect_signals()

        if order:
            self.setWindowTitle("Редактирование заказа")
            self.form_title_label.setText("Редактирование заказа")
            self._fill_form()
        else:
            self.setWindowTitle("Добавление заказа")
            self.form_title_label.setText("Добавление заказа")
            self.id_input.setVisible(False)
            self.order_date_input.setDate(QDate.currentDate())
            self.issue_date_input.setEnabled(False)

    def _load_combos(self):
        self.status_combo.addItems(ORDER_STATUSES)

        try:
            conn = get_connection()
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT UserID, FIO FROM Users ORDER BY FIO")
                    users = cursor.fetchall()
            for u in users:
                self.user_combo.addItem(u['FIO'], u['UserID'])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить клиентов:\n{e}")

    def _connect_signals(self):
        self.save_button.clicked.connect(self._save)
        self.cancel_button.clicked.connect(self.close)
        self.issue_date_checkbox.toggled.connect(self._toggle_issue_date)

    def _toggle_issue_date(self, checked):
        self.issue_date_input.setEnabled(not checked)

    def _fill_form(self):
        self.id_input.setText(str(self.order['OrderID']))

        idx = self.user_combo.findData(self.order['UserID'])
        if idx >= 0:
            self.user_combo.setCurrentIndex(idx)

        status_idx = self.status_combo.findText(self.order['Status'])
        if status_idx >= 0:
            self.status_combo.setCurrentIndex(status_idx)

        self.address_input.setText(self.order.get('DeliveryAddress', '') or '')

        if self.order['OrderDate']:
            od = self.order['OrderDate']
            if isinstance(od, str):
                parts = od.split('-')
                qdate = QDate(int(parts[0]), int(parts[1]), int(parts[2]))
            else:
                qdate = QDate(od.year, od.month, od.day)
            self.order_date_input.setDate(qdate)

        if self.order['IssueDate']:
            self.issue_date_checkbox.setChecked(False)
            self.issue_date_input.setEnabled(True)
            iss = self.order['IssueDate']
            if isinstance(iss, str):
                parts = iss.split('-')
                qdate = QDate(int(parts[0]), int(parts[1]), int(parts[2]))
            else:
                qdate = QDate(iss.year, iss.month, iss.day)
            self.issue_date_input.setDate(qdate)
        else:
            self.issue_date_checkbox.setChecked(True)
            self.issue_date_input.setEnabled(False)

    def _validate(self):
        errors = []
        if self.user_combo.currentIndex() < 0:
            errors.append("• Выберите клиента")
        if not self.address_input.text().strip():
            errors.append("• Укажите адрес доставки")
        return errors

    def _save(self):
        errors = self._validate()
        if errors:
            QMessageBox.warning(
                self, "Ошибка валидации",
                "Пожалуйста, исправьте следующие ошибки:\n\n" + "\n".join(errors)
            )
            return

        user_id = self.user_combo.currentData()
        status = self.status_combo.currentText()
        address = self.address_input.text().strip()
        order_date = self.order_date_input.date().toString("yyyy-MM-dd")

        issue_date = None
        if not self.issue_date_checkbox.isChecked():
            issue_date = self.issue_date_input.date().toString("yyyy-MM-dd")

        try:
            conn = get_connection()
            with conn:
                with conn.cursor() as cursor:
                    if self.order:
                        cursor.execute("""
                            UPDATE Orders SET UserID=%s, Status=%s,
                                   DeliveryAddress=%s, OrderDate=%s, IssueDate=%s
                            WHERE OrderID=%s
                        """, (user_id, status, address, order_date,
                              issue_date, self.order['OrderID']))
                    else:
                        cursor.execute("""
                            INSERT INTO Orders (UserID, Status, DeliveryAddress,
                                   OrderDate, IssueDate)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (user_id, status, address, order_date, issue_date))
                conn.commit()

            action = "обновлён" if self.order else "добавлен"
            QMessageBox.information(self, "Успешно", f"Заказ успешно {action}.")

            if self.parent_window:
                self.parent_window.load_orders()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить заказ:\n{e}")

    def closeEvent(self, event):
        if self.parent_window:
            self.parent_window.order_form = None
        super().closeEvent(event)
