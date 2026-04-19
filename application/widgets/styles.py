TITLE_LABEL = """
    QLabel {
        color: #ffffff;
        font-size: 14px;
        font-weight: bold;
    }
"""

TITLEBAR_BUTTON = """
    QPushButton { 
        background-color: transparent;
        border: none;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #202920;
    }
"""

TITLEBAR_CLOSE_BUTTON = """
    QPushButton {
        background-color: transparent;
        border: none;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #8b0000;
    }
"""

MAIN_BG = "background-color: #1e1e1e;"
PANEL_BG = "background-color: #252525;"
SEPARATOR_BG = "background-color: #3a3a3a;"
CHAT_HEADER_BG = "background-color: #252525; border-bottom: 1px solid #3a3a3a;"
INPUT_CONTAINER_BG = "background-color: #252525; border-top: 1px solid #3a3a3a;"

BTN_PRIMARY = """
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

BTN_CALL = """
    QPushButton {
        background-color: #2d4532;
        border-radius: 17px;
        font-size: 13px;
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

BTN_SEND = """
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
"""

BTN_LOGIN = """
    QPushButton {
        background-color: #2d4532;
        border-radius: 20px;
        font-size: 15px;
        font-weight: bold;
        color: #ffffff;
    }
    QPushButton:hover { background-color: #3a5a3f; }
    QPushButton:pressed { background-color: #1f3025; }
"""

CONTACT_BTN = """
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
"""

CONTACT_BTN_ACTIVE = """
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
"""

INPUT_FIELD = """
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
"""

INPUT_MESSAGE = """
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
"""

SCROLL_CONTACTS = """
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
"""

SCROLL_MESSAGES = """
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
"""

NOTIFICATION_LABEL = """
    QLabel {
        color: #666666;
        font-size: 20px;
        font-weight: 300;
    }
"""

CHAT_CONTACT_LABEL = """
    QLabel {
        color: #ffffff;
        font-size: 18px;
        font-weight: bold;
    }
"""

LOGIN_TITLE = "color: #ffffff; font-size: 24px; font-weight: bold;"

MSG_RECEIVED = """
    QLabel {
        background-color: #2d3a3d;
        border-radius: 15px;
        padding: 12px 16px;
        font-size: 15px;
        color: #ffffff;
    }
"""

MSG_SENT = """
    QLabel {
        background-color: #2d4532;
        border-radius: 15px;
        padding: 12px 16px;
        font-size: 15px;
        color: #ffffff;
    }
"""