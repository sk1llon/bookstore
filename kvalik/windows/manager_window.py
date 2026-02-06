# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt6 import uic


class ManagerWindow(QMainWindow):
    def __init__(self, user_id, full_name):
        super().__init__()

