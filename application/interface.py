from unicodedata import name
from PySide6.QtWidgets import (QApplication, QMainWindow, QGridLayout, QWidget, QScrollArea,
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
        main_frame.addLayout(self.contacts_frame_widget())
        main_frame.addLayout(self.message_frame_widget())


    def contacts_frame_widget(self):
        contacts_frame = QVBoxLayout(self)
        contacts_frame.setContentsMargins(0, 0, 0, 0)
        contacts_frame.setSpacing(0)
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
        """
        self.contacts_buttons = {}  
        for name in contacts:  
            self.add_buttons(name, contacts_frame, contacts_style)
        contacts_frame.addStretch()
        return contacts_frame


    def message_frame_widget(self):
        message_frame = QVBoxLayout(self)
        message_frame.setContentsMargins(0, 0, 0, 0)
        message_frame.setSpacing(0)

        message_frame.addWidget(self.scroll_area_widget())
        message_frame.addWidget(self.input_message_widget())
        return message_frame


    def scroll_area_widget(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #2b2b2b;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        scroll_area.setWidget(self.messages_container_widget())
        return scroll_area


    def messages_container_widget(self):
        messages_style = """
            QLabel {
                background-color: #2d4532;
                border-radius: 10px;
                padding: 20px;
                font-size: 16px;
                color: #ffffff;
            }
            """
        messages_text = {"Hello!":1, "How are you?":1, "Let's meet up.":2, "See you later!":2, "Goodbye!":1, "Take care!":2, "What's up?":1, "Long time no see!":2, "Happy to hear from you!":1, "Let's catch up soon.":2}
        messages_container = QWidget()
        messages_container.setStyleSheet("background-color: #2b2b2b;")
        messages = QVBoxLayout(messages_container)
        messages.setSpacing(10)

        for message, sender in messages_text.items():
            self.add_message(message, sender, messages, messages_style)

        messages.addStretch(1)
        return messages_container

    def input_message_widget(self):
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
        return input_message


    def add_message(self, message, sender, messages_layout, messages_style):
        try:
            message_label = QLabel(message)
            message_label.setWordWrap(True)
            message_label.setStyleSheet(messages_style)
            if sender == 1:
                message_label.setAlignment(Qt.AlignLeft)
            else:
                message_label.setAlignment(Qt.AlignRight)
            messages_layout.addWidget(message_label)
            messages_layout.addSpacing(20)
        except Exception as e:
            print(f"Error adding message: {e}")



    def add_buttons(self, name, contacts_frame, contacts_style):
        try:
            contact = QPushButton()
            contact.setFixedSize(300, 60)
            contact.setStyleSheet(contacts_style)
            contact.setText(name)
            contact.clicked.connect(lambda checked, c=name: self.chat_with_contact(c))
            contacts_frame.addWidget(contact)
            self.contacts_buttons[name] = contact
        except Exception as e:
            print(f"Error adding contact button: {e}")

    def chat_with_contact(self, contact):
        try:
            print(f"Chatting with {contact}")
        except Exception as e:
            print(f"Error: {e}")


        
    


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