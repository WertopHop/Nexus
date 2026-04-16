from PySide6.QtWidgets import QWidget, QScrollArea, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QMenu
from PySide6.QtCore import Qt, Signal
import database as db
import styles


class ContactsPanel(QWidget):
    contact_selected = Signal(str)
    def __init__(self, parent=None, messenger=None, async_worker=None):
        super().__init__(parent)
        self.database = db.Database()
        self.contacts_buttons = {}
        self.messenger = messenger
        self.async_worker = async_worker

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_add_widget())
        layout.addWidget(self._build_scroll_area(), 1)

    def _build_add_widget(self):
        frame = QWidget()
        frame.setFixedSize(300, 150)
        frame.setStyleSheet(styles.PANEL_BG)

        self.peer_id_input = QLineEdit()
        self.peer_id_input.setFixedSize(240, 45)
        self.peer_id_input.setStyleSheet(styles.INPUT_FIELD)
        self.peer_id_input.setPlaceholderText("Enter peer ID")

        self.button_add = QPushButton("Add Contact")
        self.button_add.setFixedSize(240, 50)
        self.button_add.setStyleSheet(styles.BTN_PRIMARY)
        self.button_add.clicked.connect(lambda: self.add_contact(self.peer_id_input.text()))

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(30, 15, 30, 15)
        frame_layout.setSpacing(10)
        frame_layout.addWidget(self.peer_id_input, alignment=Qt.AlignHCenter)
        frame_layout.addWidget(self.button_add, alignment=Qt.AlignHCenter)
        return frame

    def _build_scroll_area(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedWidth(300)
        scroll_area.setStyleSheet(styles.SCROLL_CONTACTS)

        contacts_container = QWidget()
        contacts_container.setStyleSheet(styles.PANEL_BG)
        self.contacts_frame = QVBoxLayout(contacts_container)
        self.contacts_frame.setContentsMargins(8, 5, 8, 5)
        self.contacts_frame.setSpacing(5)
        self.refresh_buttons()
        self.contacts_frame.addStretch()

        scroll_area.setWidget(contacts_container)
        return scroll_area

    def add_contact(self, name: str):
        if name.strip():
            self.button_add.setEnabled(False)
            self.database.add_contact(name)
            self.refresh_buttons()
            self.peer_id_input.clear()
            self.button_add.setEnabled(True)

    def refresh_buttons(self):
        try:
            for name, button in list(self.contacts_buttons.items()):
                button.deleteLater()
            self.contacts_buttons.clear()
            contacts = self.database.get_contacts()
            for name in contacts:
                contact_button = QPushButton()
                contact_button.setFixedHeight(65)
                contact_button.setText(name)
                contact_button.setStyleSheet(styles.CONTACT_BTN)
                contact_button.clicked.connect(lambda checked, n=name: self.contact_selected.emit(n))
                contact_button.setContextMenuPolicy(Qt.CustomContextMenu)
                contact_button.customContextMenuRequested.connect(lambda pos, n=name: self._show_contact_menu(pos, n))
                self.contacts_frame.insertWidget(self.contacts_frame.count() - 1, contact_button)
                self.contacts_buttons[name] = contact_button
                self.initiate_call(name)
        except Exception as e:
            pass

    def initiate_call(self, contact_name: str):
        if contact_name and self.async_worker:
            self.async_worker.run_coroutine(self.messenger.call_peer(contact_name))

    def highlight(self, contact_name: str):
        for name, button in self.contacts_buttons.items():
            if name == contact_name:
                button.setStyleSheet(styles.CONTACT_BTN_ACTIVE)
            else:
                button.setStyleSheet(styles.CONTACT_BTN)

    def _show_contact_menu(self, pos, contact_name: str):
        button = self.contacts_buttons.get(contact_name)
        if button is None:
            return

        menu = QMenu(self)
        delete_action = menu.addAction("Delete contact")
        # menu.addAction("...")

        action = menu.exec(button.mapToGlobal(pos))
        if action == delete_action:
            self._delete_contact(contact_name)

    def _delete_contact(self, contact_name: str):
        self.database.delete_contact(contact_name)
        self.refresh_buttons()
