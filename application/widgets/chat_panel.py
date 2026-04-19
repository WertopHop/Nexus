from PySide6.QtWidgets import (QWidget, QScrollArea, QPushButton, QLineEdit,
                               QHBoxLayout, QVBoxLayout, QLabel, QStackedWidget)
from PySide6.QtCore import Qt
from datetime import datetime
import database as db
import styles


class ChatPanel(QWidget):
    def __init__(self, parent=None, messenger=None, async_worker=None):
        super().__init__(parent)
        self.messenger = messenger
        self.async_worker = async_worker
        self.database = db.Database()
        self.contact_name = None

        self.stack = QStackedWidget()

        notification_widget = QWidget()
        notif_layout = QVBoxLayout(notification_widget)
        notif_layout.addStretch(1)
        notification = QLabel("select a contact to start chatting")
        notification.setAlignment(Qt.AlignCenter)
        notification.setStyleSheet(styles.NOTIFICATION_LABEL)
        notif_layout.addWidget(notification)
        notif_layout.addStretch(1)

        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        chat_header = QWidget()
        chat_header.setFixedHeight(60)
        chat_header.setStyleSheet(styles.CHAT_HEADER_BG)
        header_layout = QHBoxLayout(chat_header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        self.contact_name_label = QLabel("Contact")
        self.contact_name_label.setStyleSheet(styles.CHAT_CONTACT_LABEL)
        header_layout.addWidget(self.contact_name_label)
        header_layout.addStretch()
        '''self.call_button = QPushButton("Connect")
        self.call_button.setFixedSize(100, 35)
        self.call_button.setStyleSheet(styles.BTN_CALL)
        self.call_button.clicked.connect(self.initiate_call)
        header_layout.addWidget(self.call_button)'''

        chat_layout.addWidget(chat_header)
        chat_layout.addWidget(self._build_scroll_area(), 1)
        chat_layout.addWidget(self._build_input_widget())

        self.stack.addWidget(notification_widget)
        self.stack.addWidget(chat_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

    def _build_scroll_area(self):
        self.scroll_area_message = QScrollArea()
        self.scroll_area_message.setWidgetResizable(True)
        self.scroll_area_message.setStyleSheet(styles.SCROLL_MESSAGES)

        messages_container = QWidget()
        messages_container.setStyleSheet(styles.MAIN_BG)
        self.messages = QVBoxLayout(messages_container)
        self.messages.setContentsMargins(20, 20, 20, 20)
        self.messages.setSpacing(10)

        self.scroll_area_message.setWidget(messages_container)
        return self.scroll_area_message

    def _build_input_widget(self):
        input_container = QWidget()
        input_container.setFixedHeight(80)
        input_container.setStyleSheet(styles.INPUT_CONTAINER_BG)

        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(20, 15, 20, 15)
        input_layout.setSpacing(10)

        self.input_message = QLineEdit()
        self.input_message.setFixedHeight(50)
        self.input_message.setStyleSheet(styles.INPUT_MESSAGE)
        self.input_message.setPlaceholderText("Type a message...")
        self.input_message.returnPressed.connect(self.send_message)

        send_button = QPushButton("Send")
        send_button.setFixedSize(100, 50)
        send_button.setStyleSheet(styles.BTN_SEND)
        send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_message)
        input_layout.addWidget(send_button)
        return input_container

    def open_contact(self, name: str):
        self.contact_name = name
        self.contact_name_label.setText(name)
        self.stack.setCurrentIndex(1)
        self._remove_messages()
        self.messages.addStretch(1)
        messages = self.database.get_messages(name)
        self.add_message(messages)
        self.scroll_to_bottom()

    def receive_message(self, sender_name: str, message_text: str):
        self.database.add_message(sender_name, message_text, direction=True)
        if self.contact_name == sender_name and self.stack.currentIndex() == 1:
            self.add_message([(message_text, 1, datetime.now())])
            self.scroll_to_bottom()

    def send_message(self):
        message_text = self.input_message.text().strip()
        if message_text and self.contact_name:
            self.database.add_message(self.contact_name, message_text, direction=False)
            self.add_message([(message_text, 0, datetime.now())])
            if self.async_worker and self.messenger:
                self.async_worker.run_coroutine(
                    self.messenger.send_message(self.contact_name, message_text)
                )
            self.input_message.clear()
            self.scroll_to_bottom()

    def add_message(self, data_messages):
        try:
            for message, sender, timestamp in data_messages:
                message_container = QWidget()
                message_layout = QHBoxLayout(message_container)
                message_layout.setContentsMargins(0, 0, 0, 0)
                message_label = QLabel(message)
                message_label.setWordWrap(True)
                message_label.setMaximumWidth(600)
                if sender == 1:
                    message_label.setStyleSheet(styles.MSG_RECEIVED)
                    message_layout.addWidget(message_label, alignment=Qt.AlignLeft)
                    message_layout.addStretch()
                else:
                    message_label.setStyleSheet(styles.MSG_SENT)
                    message_layout.addStretch()
                    message_layout.addWidget(message_label, alignment=Qt.AlignRight)
                self.messages.addWidget(message_container)
        except Exception as e:
            pass

    def scroll_to_bottom(self):
        scrollbar = self.scroll_area_message.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _remove_messages(self):
        while self.messages.count():
            item = self.messages.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
