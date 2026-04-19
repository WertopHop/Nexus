from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
import widgets.styles as styles
from utils import resource_path


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(39)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)
        self.title_label = QLabel("Nexus")
        self.title_label.setStyleSheet(styles.TITLE_LABEL)
        layout.addWidget(self.title_label)
        layout.addStretch()
        self.minimize_btn = QPushButton()
        self.minimize_btn.setFixedSize(39, 39)
        self.minimize_btn.setIcon(QIcon(resource_path("icons/minimize.png")))
        self.minimize_btn.setIconSize(QSize(20, 20))
        self.minimize_btn.setStyleSheet(styles.TITLEBAR_BUTTON)
        self.minimize_btn.clicked.connect(self.minimize_window)
        self.maximize_btn = QPushButton()
        self.maximize_btn.setFixedSize(39, 39)
        self.maximize_btn.setIcon(QIcon(resource_path("icons/maximize.png")))
        self.maximize_btn.setIconSize(QSize(20, 20))
        self.maximize_btn.setStyleSheet(styles.TITLEBAR_BUTTON)
        self.maximize_btn.clicked.connect(self.maximize_window)
        self.close_btn = QPushButton()
        self.close_btn.setFixedSize(39, 39)
        self.close_btn.setIcon(QIcon(resource_path("icons/close.png")))
        self.close_btn.setIconSize(QSize(20, 20))
        self.close_btn.setStyleSheet(styles.TITLEBAR_CLOSE_BUTTON)
        self.close_btn.clicked.connect(self.close_window)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)

    def minimize_window(self):
        self.parent.showMinimized()

    def maximize_window(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_btn.setIcon(QIcon(resource_path("icons/maximize.png")))
        else:
            self.parent.showMaximized()
            self.maximize_btn.setIcon(QIcon(resource_path("icons/restore.png")))

    def close_window(self):
        self.parent.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.windowHandle().startSystemMove()
            event.accept()

    def mouseMoveEvent(self, event):
        event.accept()

    def mouseReleaseEvent(self, event):
        event.accept()

    def mouseDoubleClickEvent(self, event):
        self.maximize_window()
