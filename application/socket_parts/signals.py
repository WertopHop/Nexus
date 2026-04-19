from PySide6.QtCore import QObject, Signal


class P2PMessengerSignals(QObject):
    message_received = Signal(str, str)
    connection_established = Signal(str)
    connection_closed = Signal(str)
    peer_registered = Signal(str)
    error_occurred = Signal(str)
    incoming_call = Signal(str)
    dh_key_established = Signal(str)
