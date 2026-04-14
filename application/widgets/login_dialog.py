from PySide6.QtWidgets import QDialog, QPushButton, QLineEdit, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
import styles


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus - Login")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(400, 250)
        self.setStyleSheet(styles.MAIN_BG)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        title = QLabel("Nexus")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(styles.LOGIN_TITLE)
        layout.addWidget(title)

        self.peer_id_input = QLineEdit()
        self.peer_id_input.setFixedHeight(45)
        self.peer_id_input.setPlaceholderText("Enter your peer ID")
        self.peer_id_input.setStyleSheet(styles.INPUT_FIELD)
        layout.addWidget(self.peer_id_input)

        self.server_input = QLineEdit()
        self.server_input.setFixedHeight(45)
        self.server_input.setPlaceholderText("Signaling server (default: http://localhost:8080)")
        self.server_input.setStyleSheet(styles.INPUT_FIELD)
        layout.addWidget(self.server_input)

        connect_btn = QPushButton("Connect")
        connect_btn.setFixedHeight(45)
        connect_btn.setStyleSheet(styles.BTN_LOGIN)
        connect_btn.clicked.connect(self.accept)
        self.peer_id_input.returnPressed.connect(self.accept)
        self.server_input.returnPressed.connect(self.accept)
        layout.addWidget(connect_btn)

    def get_values(self):
        peer_id = self.peer_id_input.text().strip()
        server = self.server_input.text().strip() or "http://localhost:8080"
        return peer_id, server
