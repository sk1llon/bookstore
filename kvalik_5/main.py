import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from windows.login_window import LoginWindow

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def ensure_resources():
    """Создаёт директории и placeholder-ресурсы, если они отсутствуют."""
    covers_dir = os.path.join(BASE_DIR, 'covers')
    resources_dir = os.path.join(BASE_DIR, 'resources')
    os.makedirs(covers_dir, exist_ok=True)
    os.makedirs(resources_dir, exist_ok=True)

    from PyQt6.QtGui import QImage, QPainter, QFont, QColor
    from PyQt6.QtCore import Qt, QRect

    placeholder_path = os.path.join(covers_dir, 'picture.png')
    if not os.path.exists(placeholder_path):
        img = QImage(300, 200, QImage.Format.Format_RGB32)
        img.fill(QColor(220, 220, 220))
        painter = QPainter(img)
        painter.setPen(QColor(120, 120, 120))
        painter.setFont(QFont('Arial', 18))
        painter.drawText(QRect(0, 0, 300, 200), Qt.AlignmentFlag.AlignCenter, 'Нет фото')
        painter.end()
        img.save(placeholder_path)

    icon_path = os.path.join(resources_dir, 'icon.png')
    if not os.path.exists(icon_path):
        img = QImage(64, 64, QImage.Format.Format_ARGB32)
        img.fill(QColor(0, 0, 0, 0))
        painter = QPainter(img)
        painter.setBrush(QColor('#2E8B57'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(4, 4, 56, 56, 10, 10)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont('Arial', 28, QFont.Weight.Bold))
        painter.drawText(QRect(4, 4, 56, 56), Qt.AlignmentFlag.AlignCenter, 'К')
        painter.end()
        img.save(icon_path)

    logo_path = os.path.join(resources_dir, 'logo.png')
    if not os.path.exists(logo_path):
        img = QImage(120, 120, QImage.Format.Format_ARGB32)
        img.fill(QColor(0, 0, 0, 0))
        painter = QPainter(img)
        painter.setBrush(QColor('#2E8B57'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(10, 10, 100, 100, 16, 16)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont('Arial', 20, QFont.Weight.Bold))
        painter.drawText(QRect(10, 20, 100, 50), Qt.AlignmentFlag.AlignCenter, 'Книжный')
        painter.setFont(QFont('Arial', 16))
        painter.drawText(QRect(10, 60, 100, 40), Qt.AlignmentFlag.AlignCenter, 'магазин')
        painter.end()
        img.save(logo_path)


def main():
    app = QApplication(sys.argv)

    ensure_resources()

    icon_path = os.path.join(BASE_DIR, 'resources', 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    app.setStyle('Fusion')

    window = LoginWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
