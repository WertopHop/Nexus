from unicodedata import name
from PySide6.QtWidgets import (QApplication, QMainWindow, QGridLayout, QWidget, QScrollArea,
                               QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QLabel)
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QIcon, QPixmap, QScreen
import sys
import database as db


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
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_btn.setIcon(QIcon("icons/maximize.png"))
        else:
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
        self.setStyleSheet("background-color: #1e1e1e;")
        self.main_frame = QHBoxLayout(self)
        self.main_frame.setContentsMargins(0, 0, 0, 0)
        self.main_frame.setSpacing(1)
        self.main_frame.addLayout(self.contacts_frame_widget(), 2)
        separator = QWidget()
        separator.setFixedWidth(1)
        separator.setStyleSheet("background-color: #3a3a3a;")
        self.main_frame.addWidget(separator)
        
        self.main_frame.addLayout(self.mainframe_notification(), 8)

    def contacts_frame_widget(self):
        contacts_frame = QVBoxLayout()
        contacts_frame.setContentsMargins(0, 0, 0, 0)
        contacts_frame.setSpacing(0)
        contacts_frame.addWidget(self.button_add_widget())
        contacts_frame.addWidget(self.scroll_area_contacts_widget(), 1)
        return contacts_frame

    def button_add_widget(self):
        button_add_frame = QWidget()
        button_add_frame.setFixedSize(300, 150)
        button_add_frame.setStyleSheet("background-color: #252525;")
        
        button_add_style = """
            QPushButton { 
                background-color: #2d4532;
                border-radius: 20px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #3a5a3f;
            }
            QPushButton:pressed {
                background-color: #1f3025;
            }
        """
        line_edit = QLineEdit()
        line_edit.setFixedSize(240, 45)
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                border: 2px solid #2d4532;
                border-radius: 20px;
                font-size: 14px;
                color: #ffffff;
                padding: 10px 15px;
            }
            QLineEdit:focus {
                border: 2px solid #3a5a3f;
            }
        """)
        line_edit.setPlaceholderText("Enter peer ID")
        
        self.button_add = QPushButton()
        self.button_add.setFixedSize(240, 50)
        self.button_add.setStyleSheet(button_add_style)
        self.button_add.setText("Add Contact")
        self.button_add.clicked.connect(lambda checked: self.add_contact(line_edit.text()))
        
        button_add_frame_layout = QVBoxLayout(button_add_frame)
        button_add_frame_layout.setContentsMargins(30, 15, 30, 15)
        button_add_frame_layout.setSpacing(10)
        button_add_frame_layout.addWidget(line_edit, alignment=Qt.AlignHCenter)
        button_add_frame_layout.addWidget(self.button_add, alignment=Qt.AlignHCenter)
        return button_add_frame

    def scroll_area_contacts_widget(self):
        scroll_area_contacts = QScrollArea()
        scroll_area_contacts.setWidgetResizable(True)
        scroll_area_contacts.setFixedWidth(300)
        scroll_area_contacts.setStyleSheet("""
            QScrollArea {
                background-color: #252525;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #252525;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a3a;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a4a4a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        scroll_area_contacts.setWidget(self.contacts_container_widget())
        return scroll_area_contacts

    def contacts_container_widget(self):
        contacts_container = QWidget()
        contacts_container.setStyleSheet("background-color: #252525;")
        self.contacts_frame = QVBoxLayout(contacts_container)
        self.contacts_frame.setContentsMargins(8, 5, 8, 5)
        self.contacts_frame.setSpacing(5)
        self.contacts_buttons = {}
        self.active_contact = None
        self.add_buttons()
        self.contacts_frame.addStretch()
        return contacts_container

    def mainframe_notification(self):
        self.frame_notification = QVBoxLayout()
        self.frame_notification.setContentsMargins(0, 0, 0, 0)
        self.frame_notification.addStretch(1)
        notification = QLabel("select a contact to start chatting")
        notification.setAlignment(Qt.AlignCenter)
        notification.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 20px;
                font-weight: 300;
            }
        """)
        self.frame_notification.addWidget(notification)
        self.frame_notification.addStretch(1)
        return self.frame_notification

    def message_frame_widget(self):
        message_frame = QVBoxLayout()
        message_frame.setContentsMargins(0, 0, 0, 0)
        message_frame.setSpacing(0)
        chat_header = QWidget()
        chat_header.setFixedHeight(60)
        chat_header.setStyleSheet("background-color: #252525; border-bottom: 1px solid #3a3a3a;")
        header_layout = QHBoxLayout(chat_header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        self.contact_name_label = QLabel("Contact")
        self.contact_name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.contact_name_label)
        header_layout.addStretch()
        message_frame.addWidget(chat_header)
        message_frame.addWidget(self.scroll_area_message_widget())
        message_frame.addWidget(self.input_message_widget())
        return message_frame

    def scroll_area_message_widget(self):
        scroll_area_message = QScrollArea()
        scroll_area_message.setWidgetResizable(True)
        scroll_area_message.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a3a;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a4a4a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        scroll_area_message.setWidget(self.messages_container_widget())
        return scroll_area_message

    def messages_container_widget(self):
        messages_container = QWidget()
        messages_container.setStyleSheet("background-color: #1e1e1e;")
        self.messages = QVBoxLayout(messages_container)
        self.messages.setContentsMargins(20, 20, 20, 20)
        self.messages.setSpacing(10)
        return messages_container

    def input_message_widget(self):
        input_container = QWidget()
        input_container.setFixedHeight(80)
        input_container.setStyleSheet("background-color: #252525; border-top: 1px solid #3a3a3a;")
        
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(20, 15, 20, 15)
        input_layout.setSpacing(10)
        
        self.input_message = QLineEdit()
        self.input_message.setFixedHeight(50)
        self.input_message.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                border: 2px solid #2d4532;
                border-radius: 25px;
                font-size: 15px;
                color: #ffffff;
                padding: 10px 20px;
            }
            QLineEdit:focus {
                border: 2px solid #3a5a3f;
            }
        """)
        self.input_message.setPlaceholderText("Type a message...")
        self.input_message.returnPressed.connect(self.send_message)
        
        send_button = QPushButton("Send")
        send_button.setFixedSize(100, 50)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #2d4532;
                border-radius: 25px;
                font-size: 15px;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #3a5a3f;
            }
            QPushButton:pressed {
                background-color: #1f3025;
            }
        """)
        send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_message)
        input_layout.addWidget(send_button)
        
        return input_container

    def send_message(self):
        print("Sending message...")
        message_text = self.input_message.text().strip()
        if message_text:
            if hasattr(self, 'contact_name') and self.contact_name:
                print("Found contact button")
                db.Database().add_message(self.contact_name, message_text, direction=False)
                self.add_message([(message_text, 0)])
                self.input_message.clear()

    def remove_messages(self):        
        while self.messages.count():
            item = self.messages.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def add_contact(self, name):
        if name.strip():
            self.button_add.setEnabled(False)
            db.Database().add_contact(name)
            self.add_buttons()
            self.button_add.setEnabled(True)

    def add_message(self, data_messages):
        try:
            for message, sender in data_messages:
                message_container = QWidget()
                message_layout = QHBoxLayout(message_container)
                message_layout.setContentsMargins(0, 0, 0, 0)
                
                message_label = QLabel(message)
                message_label.setWordWrap(True)
                message_label.setMaximumWidth(600)
                
                if sender == 1:
                    message_label.setStyleSheet("""
                        QLabel {
                            background-color: #2d3a3d;
                            border-radius: 15px;
                            padding: 12px 16px;
                            font-size: 15px;
                            color: #ffffff;
                        }
                    """)
                    message_layout.addWidget(message_label, alignment=Qt.AlignLeft)
                    message_layout.addStretch()
                else:
                    message_label.setStyleSheet("""
                        QLabel {
                            background-color: #2d4532;
                            border-radius: 15px;
                            padding: 12px 16px;
                            font-size: 15px;
                            color: #ffffff;
                        }
                    """)
                    message_layout.addStretch()
                    message_layout.addWidget(message_label, alignment=Qt.AlignRight)
                
                self.messages.addWidget(message_container)
        except Exception as e:
            print(f"Error adding message: {e}")

    def add_buttons(self):
        try:
            for name, button in list(self.contacts_buttons.items()):
                button.deleteLater()
            self.contacts_buttons.clear()
            
            contacts = db.Database().get_contacts()
            
            for name in contacts:
                contact_button = QPushButton()
                contact_button.setFixedHeight(65)
                contact_button.setText(name)
                
                contact_button.setStyleSheet("""
                    QPushButton { 
                        background-color: #2d2d2d;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        color: #ffffff;
                        text-align: left;
                        padding: 15px 20px;
                    }
                    QPushButton:hover {
                        background-color: #3a3a3a;
                    }
                    QPushButton:pressed {
                        background-color: #2d4532;
                    }
                """)
                
                contact_button.clicked.connect(lambda checked, n=name: self.chat_with_contact(n))
                self.contacts_frame.insertWidget(self.contacts_frame.count() - 1, contact_button)
                self.contacts_buttons[name] = contact_button
                
        except Exception as e:
            print(f"Error adding contact button: {e}")

    def highlight_active_contact(self, contact_name):
        for name, button in self.contacts_buttons.items():
            if name == contact_name:
                button.setStyleSheet("""
                    QPushButton { 
                        background-color: #2d4532;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        color: #ffffff;
                        text-align: left;
                        padding: 15px 20px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #3a5a3f;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton { 
                        background-color: #2d2d2d;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        color: #ffffff;
                        text-align: left;
                        padding: 15px 20px;
                    }
                    QPushButton:hover {
                        background-color: #3a3a3a;
                    }
                    QPushButton:pressed {
                        background-color: #2d4532;
                    }
                """)

    def chat_with_contact(self, contact):
        try:
            self.contact_name = contact
            self.highlight_active_contact(contact)
            if self.main_frame.itemAt(2).layout() == self.frame_notification:
                self.main_frame.removeItem(self.frame_notification)
                self.main_frame.addLayout(self.message_frame_widget(), 8)
            self.contact_name_label.setText(contact)
            print(f"Chatting with {contact}")
            self.remove_messages()
            self.messages.addStretch(1)
            messages = db.Database().get_messages(contact)
            self.add_message(messages)
        except Exception as e:
            print(f"Error: {e}")


class Interface(QMainWindow):
    def __init__(self):
        super().__init__()
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
    window = Interface()
    window.show()
    sys.exit(app.exec())