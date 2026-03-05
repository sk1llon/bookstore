import os
import shutil

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

from database.db_utils import get_connection

UI_PATH = os.path.join(os.path.dirname(__file__), '..', 'interfaces', 'book_form.ui')
PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
COVERS_DIR = os.path.join(PROJECT_DIR, 'covers')
MAX_IMG_WIDTH = 300
MAX_IMG_HEIGHT = 200


class BookForm(QWidget):
    def __init__(self, book=None, parent_window=None):
        super().__init__()
        uic.loadUi(UI_PATH, self)

        self.book = book
        self.parent_window = parent_window
        self.new_image_path = None
        self.current_cover_path = None

        icon_path = os.path.join(PROJECT_DIR, 'resources', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._load_combos()
        self._connect_signals()

        if book:
            self.setWindowTitle("Редактирование книги")
            self.form_title_label.setText("Редактирование книги")
            self._fill_form()
        else:
            self.setWindowTitle("Добавление книги")
            self.form_title_label.setText("Добавление книги")
            self.id_input.setVisible(False)
            if hasattr(self, 'id_label_text'):
                self.id_label_text.setVisible(False)

    def _load_combos(self):
        try:
            conn = get_connection()
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT GenreID, Name FROM Genres ORDER BY Name")
                    genres = cursor.fetchall()
                    cursor.execute("SELECT AuthorID, FullName FROM Authors ORDER BY FullName")
                    authors = cursor.fetchall()
                    cursor.execute("SELECT PublisherID, Name FROM Publishers ORDER BY Name")
                    publishers = cursor.fetchall()

            for g in genres:
                self.genre_combo.addItem(g['Name'], g['GenreID'])
            for a in authors:
                self.author_combo.addItem(a['FullName'], a['AuthorID'])
            for p in publishers:
                self.publisher_combo.addItem(p['Name'], p['PublisherID'])

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить справочники:\n{e}")

    def _connect_signals(self):
        self.save_button.clicked.connect(self._save)
        self.cancel_button.clicked.connect(self.close)
        self.change_image_button.clicked.connect(self._change_image)

    def _fill_form(self):
        self.id_input.setText(str(self.book['BookID']))
        self.title_input.setText(self.book['Title'])
        self.description_input.setPlainText(self.book.get('Description', '') or '')
        self.price_input.setValue(float(self.book['Price']))
        self.year_input.setValue(int(self.book['Year'] or 2025))
        self.stock_input.setValue(int(self.book['StockQuantity'] or 0))
        self.discount_input.setValue(int(self.book['Discount'] or 0))

        idx = self.genre_combo.findData(self.book['GenreID'])
        if idx >= 0:
            self.genre_combo.setCurrentIndex(idx)

        idx = self.author_combo.findData(self.book['AuthorID'])
        if idx >= 0:
            self.author_combo.setCurrentIndex(idx)

        idx = self.publisher_combo.findData(self.book['PublisherID'])
        if idx >= 0:
            self.publisher_combo.setCurrentIndex(idx)

        self.current_cover_path = self.book.get('CoverPath')
        self._display_image(self.current_cover_path)

    def _display_image(self, cover_path):
        if cover_path:
            full_path = os.path.join(PROJECT_DIR, cover_path)
        else:
            full_path = None

        if full_path and os.path.exists(full_path):
            pixmap = QPixmap(full_path)
        else:
            placeholder = os.path.join(COVERS_DIR, 'picture.png')
            if os.path.exists(placeholder):
                pixmap = QPixmap(placeholder)
            else:
                self.image_label.setText("Нет изображения")
                return

        pixmap = pixmap.scaled(
            MAX_IMG_WIDTH, MAX_IMG_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)

    def _change_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            pixmap = QPixmap(file_path)
            if pixmap.width() > MAX_IMG_WIDTH or pixmap.height() > MAX_IMG_HEIGHT:
                pixmap = pixmap.scaled(
                    MAX_IMG_WIDTH, MAX_IMG_HEIGHT,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

            self.image_label.setPixmap(pixmap)
            self.new_image_path = file_path

    def _validate(self):
        errors = []
        if not self.title_input.text().strip():
            errors.append("• Укажите наименование книги")
        if self.price_input.value() <= 0:
            errors.append("• Цена должна быть больше 0")
        if self.genre_combo.currentIndex() < 0:
            errors.append("• Выберите жанр")
        if self.author_combo.currentIndex() < 0:
            errors.append("• Выберите автора")
        if self.publisher_combo.currentIndex() < 0:
            errors.append("• Выберите издательство")
        return errors

    def _save(self):
        errors = self._validate()
        if errors:
            QMessageBox.warning(
                self, "Ошибка валидации",
                "Пожалуйста, исправьте следующие ошибки:\n\n" + "\n".join(errors)
            )
            return

        title = self.title_input.text().strip()
        genre_id = self.genre_combo.currentData()
        description = self.description_input.toPlainText().strip()
        author_id = self.author_combo.currentData()
        publisher_id = self.publisher_combo.currentData()
        price = self.price_input.value()
        year = self.year_input.value()
        stock = self.stock_input.value()
        discount = self.discount_input.value()

        cover_path = self.current_cover_path

        if self.new_image_path:
            os.makedirs(COVERS_DIR, exist_ok=True)
            ext = os.path.splitext(self.new_image_path)[1]
            filename = f"{title.replace(' ', '_').replace('/', '_')}{ext}"
            dest = os.path.join(COVERS_DIR, filename)

            pixmap = QPixmap(self.new_image_path)
            if pixmap.width() > MAX_IMG_WIDTH or pixmap.height() > MAX_IMG_HEIGHT:
                pixmap = pixmap.scaled(
                    MAX_IMG_WIDTH, MAX_IMG_HEIGHT,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            pixmap.save(dest)

            if self.book and self.current_cover_path:
                old_file = os.path.join(PROJECT_DIR, self.current_cover_path)
                if os.path.exists(old_file) and 'picture.png' not in old_file:
                    os.remove(old_file)

            cover_path = f"covers/{filename}"

        try:
            conn = get_connection()
            with conn:
                with conn.cursor() as cursor:
                    if self.book:
                        cursor.execute("""
                            UPDATE Books SET Title=%s, GenreID=%s, Description=%s,
                                   AuthorID=%s, PublisherID=%s, Price=%s, Year=%s,
                                   StockQuantity=%s, Discount=%s, CoverPath=%s
                            WHERE BookID=%s
                        """, (title, genre_id, description, author_id, publisher_id,
                              price, year, stock, discount, cover_path,
                              self.book['BookID']))
                    else:
                        cursor.execute("""
                            INSERT INTO Books (Title, GenreID, Description, AuthorID,
                                   PublisherID, Price, Year, StockQuantity, Discount, CoverPath)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (title, genre_id, description, author_id, publisher_id,
                              price, year, stock, discount, cover_path))
                conn.commit()

            action = "обновлена" if self.book else "добавлена"
            QMessageBox.information(self, "Успешно", f"Книга успешно {action}.")

            if self.parent_window:
                self.parent_window.load_books()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные:\n{e}")

    def closeEvent(self, event):
        if self.parent_window:
            self.parent_window.book_form = None
        super().closeEvent(event)
