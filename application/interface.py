from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QDialog
from PySide6.QtCore import Qt, Slot
import sys
from nexus_socket import P2PMessenger
import styles
from async_worker import AsyncWorker
from widgets.login_dialog import LoginDialog
from widgets.title_bar import CustomTitleBar
from widgets.contacts_panel import ContactsPanel
from widgets.chat_panel import ChatPanel



SIGNALING_SERVER = "http://localhost:8080"
PEER_ID = None


class MainWidget(QWidget):
    def __init__(self, parent=None, messenger: P2PMessenger = None, async_worker: AsyncWorker = None):
        super().__init__(parent)
        self.messenger = messenger
        self.setStyleSheet(styles.MAIN_BG)
        self.contacts_panel = ContactsPanel(messenger=messenger, async_worker=async_worker)
        self.chat_panel = ChatPanel(messenger=messenger, async_worker=async_worker)
        self.contacts_panel.contact_selected.connect(self.on_contact_selected)

        if self.messenger:
            self.messenger.signals.message_received.connect(self.on_message_received)
            self.messenger.signals.incoming_call.connect(self.on_incoming_call)
            self.messenger.signals.connection_established.connect(self.on_connection_established)
            self.messenger.signals.connection_closed.connect(self.on_connection_closed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.addWidget(self.contacts_panel, 2)
        separator = QWidget()
        separator.setFixedWidth(1)
        separator.setStyleSheet(styles.SEPARATOR_BG)
        layout.addWidget(separator)
        layout.addWidget(self.chat_panel, 8)

    @Slot(str)
    def on_contact_selected(self, name: str):
        self.contacts_panel.highlight(name)
        self.chat_panel.open_contact(name)

    @Slot(str, str)
    def on_message_received(self, peer_id: str, message: str):
        self.chat_panel.receive_message(peer_id, message)

    @Slot(str)
    def on_incoming_call(self, peer_id: str):
        contacts = self.contacts_panel.database.get_contacts()
        if peer_id not in contacts:
            self.contacts_panel.database.add_contact(peer_id)
            self.contacts_panel.refresh_buttons()

    @Slot(str)
    def on_connection_established(self, peer_id: str):
        pass

    @Slot(str)
    def on_connection_closed(self, peer_id: str):
        pass

class Interface(QMainWindow):
    def __init__(self, peer_id: str, signaling_server: str):
        super().__init__()
        self.messenger = P2PMessenger(peer_id, signaling_server)
        self.async_worker = AsyncWorker(self.messenger)
        self.async_worker.start()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(CustomTitleBar(self))
        main_layout.addWidget(MainWidget(self, self.messenger, self.async_worker))
        self.setGeometry(100, 100, 1200, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle(f"Nexus - {peer_id}")

    def closeEvent(self, event):
        self.async_worker.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    dialog = LoginDialog()
    if dialog.exec() != QDialog.Accepted:
        sys.exit(0)
    
    peer_id, server = dialog.get_values()
    if not peer_id:
        sys.exit(0)

    window = Interface(peer_id, server)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
