from PySide6.QtWidgets import (QApplication, QMainWindow, QGridLayout, QWidget, 
                               QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QLabel)
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QIcon, QPixmap, QScreen
import sys


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.dragging = False
        self.drag_position = QPoint()
        self.setFixedHeight(39)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 5, 0)
        layout.setSpacing(0)
        self.title_label = QLabel("Nexus")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.title_label)
        layout.addStretch()
        button_style = """
            QPushButton { 
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #202920;
            }
        """
        close_button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #8b0000;
            }
        """
        self.minimize_btn = QPushButton()
        self.minimize_btn.setFixedSize(39, 39)
        self.minimize_btn.setIcon(QIcon("icons/minimize.png")) 
        self.minimize_btn.setIconSize(QSize(20, 20))
        self.minimize_btn.setStyleSheet(button_style)
        self.minimize_btn.clicked.connect(self.minimize_window)
        
        self.maximize_btn = QPushButton()
        self.maximize_btn.setFixedSize(39, 39)
        self.maximize_btn.setIcon(QIcon("icons/maximize.png")) 
        self.maximize_btn.setIconSize(QSize(20, 20))
        self.maximize_btn.setStyleSheet(button_style)
        self.maximize_btn.clicked.connect(self.maximize_window)
        
        self.close_btn = QPushButton()
        self.close_btn.setFixedSize(39, 39)
        self.close_btn.setIcon(QIcon("icons/close.png"))
        self.close_btn.setIconSize(QSize(20, 20))
        self.close_btn.setStyleSheet(close_button_style)
        self.close_btn.clicked.connect(self.close_window)
        
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
    
    def minimize_window(self):
        self.parent.showMinimized()
    
    def maximize_window(self):
        print("maximize", self.parent.isMaximized())
        if self.parent.isMaximized():
            print("restore size")
            self.parent.showNormal()
            self.maximize_btn.setIcon(QIcon("icons/maximize.png"))
        else:
            print("maximize to full")
            self.parent.showMaximized()
            self.maximize_btn.setIcon(QIcon("icons/restore.png"))
    
    def close_window(self):
        self.parent.close()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.parent.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.dragging = False
    
    def mouseDoubleClickEvent(self, event):
        self.maximize_window()


class interface(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle("Nexus")
        #self.setWindowIcon(QIcon("icons/Nexus.ico"))
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #1a1a1a;")  # Темный фон для контента
        main_layout.addWidget(self.content_widget)
        self.setGeometry(100, 100, 1200, 900)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = interface()
    window.show()
    sys.exit(app.exec())