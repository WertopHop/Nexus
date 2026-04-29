from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QDialog
from PySide6.QtCore import Qt, QPoint, Slot
import sys
from nexus_socket import P2PMessenger
import widgets.styles as styles
from async_worker import AsyncWorker
from widgets.login_dialog import LoginDialog
from widgets.title_bar import CustomTitleBar
from widgets.contacts_panel import ContactsPanel
from widgets.chat_panel import ChatPanel



SIGNALING_SERVER = "http://localhost:8080"
PEER_ID = None
NARROW_THRESHOLD = 700


class MainWidget(QWidget):
    def __init__(self, parent=None, messenger: P2PMessenger = None, async_worker: AsyncWorker = None, database=None):
        super().__init__(parent)
        self.messenger = messenger
        self.setStyleSheet(styles.MAIN_BG)
        self.contacts_panel = ContactsPanel(messenger=messenger, async_worker=async_worker, database=database)
        self.chat_panel = ChatPanel(messenger=messenger, async_worker=async_worker, database=database)
        self.contacts_panel.contact_selected.connect(self.on_contact_selected)

        if self.messenger:
            self.messenger.signals.message_received.connect(self.on_message_received)
            self.messenger.signals.incoming_call.connect(self.on_incoming_call)
            self.messenger.signals.connection_established.connect(self.on_connection_established)
            self.messenger.signals.connection_closed.connect(self.on_connection_closed)

        self._narrow_mode = False
        self._show_contacts = True
        self.chat_panel.back_requested.connect(self._on_back_requested)
        self.contacts_panel.contact_selected.connect(self.on_contact_selected)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.contacts_panel, 3)
        self.separator = QWidget()
        self.separator.setFixedWidth(1)
        self.separator.setStyleSheet(styles.SEPARATOR_BG)
        layout.addWidget(self.separator)
        layout.addWidget(self.chat_panel, 7)

    @Slot(str)
    def on_contact_selected(self, name: str):
        self.contacts_panel.highlight(name)
        self.chat_panel.open_contact(name)
        if self._narrow_mode:
            self._show_contacts = False
            self._apply_layout()

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        is_narrow = self.width() < NARROW_THRESHOLD
        if is_narrow != self._narrow_mode:
            self._narrow_mode = is_narrow
            self.chat_panel.set_back_button_visible(is_narrow)
            self._apply_layout()

    def _apply_layout(self):
        if not self._narrow_mode:
            self.contacts_panel.show()
            self.chat_panel.show()
            self.separator.show()
        else:
            self.separator.hide()
            if self._show_contacts:
                self.contacts_panel.show()
                self.chat_panel.hide()
            else:
                self.contacts_panel.hide()
                self.chat_panel.show()

    def _on_back_requested(self):
        self._show_contacts = True
        self._apply_layout()


class Interface(QMainWindow):
    def __init__(self, peer_id: str, signaling_server: str, database):
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
        main_layout.addWidget(MainWidget(self, self.messenger, self.async_worker, database))
        self.setGeometry(100, 100, 1200, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle(f"Nexus - {peer_id}")

    def nativeEvent(self, eventType, message):
        if eventType == b"windows_generic_MSG":
            import ctypes
            import ctypes.wintypes
            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == 0x0084:
                x = ctypes.c_int16(msg.lParam & 0xFFFF).value
                y = ctypes.c_int16((msg.lParam >> 16) & 0xFFFF).value
                dpr = self.devicePixelRatio()
                pos = self.mapFromGlobal(QPoint(round(x / dpr), round(y / dpr)))
                border = 6
                left   = pos.x() < border
                right  = pos.x() > self.width()  - border
                top    = pos.y() < border
                bottom = pos.y() > self.height() - border
                if not self.isMaximized():
                    if top    and left:  return True, 13
                    if top    and right: return True, 14
                    if bottom and left:  return True, 16
                    if bottom and right: return True, 17
                    if left:             return True, 10
                    if right:            return True, 11
                    if top:              return True, 12
                    if bottom:           return True, 15
        return super().nativeEvent(eventType, message)

    def closeEvent(self, event):
        self.async_worker.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    dialog = LoginDialog()
    if dialog.exec() != QDialog.Accepted:
        sys.exit(0)
    
    peer_id, password, server, database = dialog.get_values()
    if not peer_id or not password:
        sys.exit(0)

    window = Interface(peer_id, server, database)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
