import os

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget, QTableWidgetItem, QMessageBox, QLabel, QHBoxLayout, QHeaderView
)
from PyQt6.QtGui import QPixmap, QFont, QColor, QIcon
from PyQt6.QtCore import Qt

from database.db_utils import get_connection

UI_PATH = os.path.join(os.path.dirname(__file__), '..', 'interfaces', 'catalog_window.ui')
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')

COLUMNS = [
    'Фото', 'Наименование', 'Жанр', 'Описание', 'Автор',
    'Издательство', 'Цена', 'Год', 'Ед. изм.', 'Кол-во на складе', 'Скидка'
]

COLOR_DISCOUNT = QColor('#2E8B57')
COLOR_OUT_OF_STOCK = QColor('#ADD8E6')


class CatalogWindow(QWidget):
    def __init__(self, user, login_window):
        super().__init__()
        uic.loadUi(UI_PATH, self)

        self.user = user
        self.login_window = login_window
        self.role = user['Role'] if user else 'guest'
        self.all_books = []
        self.book_form = None

        icon_path = os.path.join(PROJECT_DIR, 'resources', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._setup_ui()
        self._connect_signals()
        self._load_data()

    def _setup_ui(self):
        role_titles = {
            'guest': 'Каталог книг (Гость)',
            'client': 'Каталог книг (Клиент)',
            'manager': 'Каталог книг (Менеджер)',
            'admin': 'Каталог книг (Администратор)'
        }
        title = role_titles.get(self.role, 'Каталог книг')
        self.setWindowTitle(title)
        self.role_label.setText(title)

        if self.user:
            self.fio_label.setText(self.user['FIO'])
        else:
            self.fio_label.setText('')

        has_controls = self.role in ('manager', 'admin')
        self.search_input.setVisible(has_controls)
        self.sort_combo.setVisible(has_controls)
        self.filter_combo.setVisible(has_controls)

        self.orders_button.setVisible(self.role in ('manager', 'admin'))

        is_admin = self.role == 'admin'
        self.add_button.setVisible(is_admin)
        self.delete_button.setVisible(is_admin)

        if has_controls:
            self.sort_combo.addItems([
                'Без сортировки',
                'Кол-во на складе ↑',
                'Кол-во на складе ↓'
            ])

        self.books_table.setColumnCount(len(COLUMNS))
        self.books_table.setHorizontalHeaderLabels(COLUMNS)
        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.books_table.setColumnWidth(0, 90)
        for i in range(1, len(COLUMNS)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

    def _connect_signals(self):
        self.logout_button.clicked.connect(self._logout)
        self.orders_button.clicked.connect(self._open_orders)

        if self.role in ('manager', 'admin'):
            self.search_input.textChanged.connect(self._apply_filters)
            self.sort_combo.currentIndexChanged.connect(self._apply_filters)
            self.filter_combo.currentIndexChanged.connect(self._apply_filters)

        if self.role == 'admin':
            self.add_button.clicked.connect(self._open_add_form)
            self.delete_button.clicked.connect(self._delete_book)
            self.books_table.doubleClicked.connect(self._open_edit_form)

    def _load_data(self):
        self._load_publishers()
        self.load_books()

    def _load_publishers(self):
        if self.role not in ('manager', 'admin'):
            return
        try:
            conn = get_connection()
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT PublisherID, Name FROM Publishers ORDER BY Name")
                    publishers = cursor.fetchall()
            self.filter_combo.blockSignals(True)
            self.filter_combo.clear()
            self.filter_combo.addItem('Все поставщики', 0)
            for pub in publishers:
                self.filter_combo.addItem(pub['Name'], pub['PublisherID'])
            self.filter_combo.blockSignals(False)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить поставщиков:\n{e}")

    def load_books(self):
        try:
            conn = get_connection()
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT b.BookID, b.Title, g.Name AS Genre, b.Description,
                               a.FullName AS Author, p.Name AS Publisher,
                               b.Price, b.Year, b.StockQuantity, b.Discount,
                               b.CoverPath, b.GenreID, b.AuthorID, b.PublisherID
                        FROM Books b
                        JOIN Genres g ON b.GenreID = g.GenreID
                        JOIN Authors a ON b.AuthorID = a.AuthorID
                        JOIN Publishers p ON b.PublisherID = p.PublisherID
                    """)
                    self.all_books = cursor.fetchall()
            self._apply_filters()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить книги:\n{e}")

    def _apply_filters(self):
        books = list(self.all_books)

        if self.role in ('manager', 'admin'):
            search_text = self.search_input.text().strip().lower()
            if search_text:
                books = [
                    b for b in books
                    if search_text in str(b['Title']).lower()
                    or search_text in str(b['Genre']).lower()
                    or search_text in str(b['Description']).lower()
                    or search_text in str(b['Author']).lower()
                    or search_text in str(b['Publisher']).lower()
                ]

            publisher_id = self.filter_combo.currentData()
            if publisher_id:
                books = [b for b in books if b['PublisherID'] == publisher_id]

            sort_index = self.sort_combo.currentIndex()
            if sort_index == 1:
                books.sort(key=lambda b: b['StockQuantity'])
            elif sort_index == 2:
                books.sort(key=lambda b: b['StockQuantity'], reverse=True)

        self._update_table(books)

    def _update_table(self, books):
        self.books_table.setRowCount(0)
        self.books_table.setRowCount(len(books))

        for row, book in enumerate(books):
            self.books_table.setRowHeight(row, 80)

            img_label = QLabel()
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cover_path = os.path.join(PROJECT_DIR, book['CoverPath'] or '')
            placeholder = os.path.join(PROJECT_DIR, 'covers', 'picture.png')

            if book['CoverPath'] and os.path.exists(cover_path):
                pixmap = QPixmap(cover_path)
            elif os.path.exists(placeholder):
                pixmap = QPixmap(placeholder)
            else:
                pixmap = QPixmap(80, 60)
                pixmap.fill(QColor(220, 220, 220))

            pixmap = pixmap.scaled(
                80, 60, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            img_label.setPixmap(pixmap)
            self.books_table.setCellWidget(row, 0, img_label)

            discount = int(book['Discount'] or 0)
            stock = int(book['StockQuantity'] or 0)
            price = float(book['Price'])

            row_bg = None
            if stock == 0:
                row_bg = COLOR_OUT_OF_STOCK
            elif discount > 15:
                row_bg = COLOR_DISCOUNT

            values = [
                '', str(book['Title']), str(book['Genre']),
                str(book['Description'] or ''), str(book['Author']),
                str(book['Publisher']), '', str(book['Year'] or ''),
                'шт.', str(stock), f"{discount}%"
            ]

            for col in range(len(COLUMNS)):
                if col == 0:
                    item = QTableWidgetItem()
                    item.setData(Qt.ItemDataRole.UserRole, book['BookID'])
                elif col == 6:
                    item = QTableWidgetItem()
                else:
                    item = QTableWidgetItem(values[col])

                if row_bg:
                    item.setBackground(row_bg)
                self.books_table.setItem(row, col, item)

            if discount > 0:
                price_widget = self._create_price_widget(price, discount, row_bg)
                self.books_table.setCellWidget(row, 6, price_widget)
            else:
                self.books_table.item(row, 6).setText(f"{price:.2f} ₽")

        self.count_label.setText(f"Записей: {len(books)}")

    def _create_price_widget(self, price, discount, bg_color):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(6)

        old_label = QLabel(f"{price:.2f}")
        font = old_label.font()
        font.setStrikeOut(True)
        old_label.setFont(font)
        old_label.setStyleSheet("color: red;")

        new_price = price * (1 - discount / 100)
        new_label = QLabel(f"{new_price:.2f} ₽")
        new_label.setStyleSheet("color: black; font-weight: bold;")

        layout.addWidget(old_label)
        layout.addWidget(new_label)
        layout.addStretch()

        if bg_color:
            widget.setStyleSheet(f"background-color: {bg_color.name()};")

        return widget

    def _open_add_form(self):
        if self.book_form and self.book_form.isVisible():
            QMessageBox.information(
                self, "Внимание",
                "Окно редактирования уже открыто.\n"
                "Закройте текущее окно, прежде чем открывать новое."
            )
            self.book_form.activateWindow()
            return

        from windows.book_form import BookForm
        self.book_form = BookForm(parent_window=self)
        self.book_form.show()

    def _open_edit_form(self):
        if self.role != 'admin':
            return

        row = self.books_table.currentRow()
        if row < 0:
            return

        if self.book_form and self.book_form.isVisible():
            QMessageBox.information(
                self, "Внимание",
                "Окно редактирования уже открыто.\n"
                "Закройте текущее окно, прежде чем открывать новое."
            )
            self.book_form.activateWindow()
            return

        book_id = self.books_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        book = next((b for b in self.all_books if b['BookID'] == book_id), None)
        if book:
            from windows.book_form import BookForm
            self.book_form = BookForm(book=book, parent_window=self)
            self.book_form.show()

    def _delete_book(self):
        row = self.books_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Информация", "Выберите книгу для удаления.")
            return

        book_id = self.books_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        book = next((b for b in self.all_books if b['BookID'] == book_id), None)
        if not book:
            return

        try:
            conn = get_connection()
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT COUNT(*) AS cnt FROM OrderItems WHERE BookID=%s",
                        (book_id,)
                    )
                    result = cursor.fetchone()
                    if result['cnt'] > 0:
                        QMessageBox.warning(
                            self, "Невозможно удалить",
                            f"Книга «{book['Title']}» присутствует в заказах.\n"
                            "Удаление невозможно."
                        )
                        return

            reply = QMessageBox.question(
                self, "Подтверждение удаления",
                f"Вы уверены, что хотите удалить книгу\n«{book['Title']}»?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                conn = get_connection()
                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute("DELETE FROM Books WHERE BookID=%s", (book_id,))
                    conn.commit()

                if book['CoverPath']:
                    cover_file = os.path.join(PROJECT_DIR, book['CoverPath'])
                    if os.path.exists(cover_file) and 'picture.png' not in cover_file:
                        os.remove(cover_file)

                QMessageBox.information(self, "Успешно", "Книга успешно удалена.")
                self.load_books()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить книгу:\n{e}")

    def _open_orders(self):
        from windows.orders_window import OrdersWindow
        self.orders_window = OrdersWindow(self.role, self)
        self.orders_window.show()
        self.hide()

    def _logout(self):
        self.login_window.on_return()
        self.close()

    def closeEvent(self, event):
        if self.book_form and self.book_form.isVisible():
            self.book_form.close()
        super().closeEvent(event)
