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
        layout.setContentsMargins(10, 0, 0, 0)
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


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #2b2b2b;")
        main_frame = QHBoxLayout(self)
        main_frame.setContentsMargins(0, 0, 0, 0)
        main_frame.setSpacing(0)
        contacts_frame = QVBoxLayout(self)
        contacts_frame.setContentsMargins(0, 0, 0, 0)
        contacts_frame.setSpacing(0)
        messages_text = ["Hello!", "How are you?", "Let's meet up.", "See you later!", "Goodbye!"]
        contacts = ["Bob", "Alice", "Charlie", "David", "Eve"]
        contacts_style = """
            QPushButton { 
                background-color: #555555;
                border: none;
                font-size: 20px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #202920;
            }
            QPushButton:active {
                background-color: #111111;
            }
        """
        self.contacts_buttons = {}    
        self.add_buttons(contacts, contacts_frame, contacts_style)
        contacts_frame.addStretch()

        message_frame = QVBoxLayout(self)
        message_frame.setContentsMargins(0, 0, 0, 0)
        message_frame.setSpacing(0)
        messages = QVBoxLayout(self)
        messages.setContentsMargins(10, 10, 10, 10)
        messages.setSpacing(10)





        input_message = QLineEdit()
        input_message.setFixedHeight(40)
        input_message.setStyleSheet("""
            QLineEdit {
                background-color: #444444;
                border: none;  
                font-size: 18px;
                color: #ffffff;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #00ff00;
            }
        """)
        input_message.setPlaceholderText("Type a message...")
        messages.addStretch(1)
        message_frame.addLayout(messages)
        message_frame.addWidget(input_message)
        

        main_frame.addLayout(contacts_frame)
        main_frame.addLayout(message_frame)

    def add_buttons(self, contacts, contacts_frame, contacts_style):
        for contact in contacts:
            self.contact = QPushButton()
            self.contact.setFixedSize(300, 60)
            self.contact.setStyleSheet(contacts_style)
            self.contact.setText(contact)
            self.contact.clicked.connect(lambda checked, c=contact: self.chat_with_contact(c))
            contacts_frame.addWidget(self.contact)
            self.contacts_buttons[contact] = self.contact

    def chat_with_contact(self, contact):
        print(f"Chatting with {contact}")


        
    


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
        main_layout.addWidget(CustomTitleBar(self))
        main_layout.addWidget(MainWidget(self))



        self.setGeometry(100, 100, 1200, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = interface()
    window.show()
    sys.exit(app.exec())