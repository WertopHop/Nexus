from PySide6.QtCore import QThread
import asyncio
from nexus_socket import P2PMessenger


class AsyncWorker(QThread):
    def __init__(self, messenger: P2PMessenger):
        super().__init__()
        self.messenger = messenger
        self.loop = None
        self.running = True

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.messenger.connect_to_signaling())
        while self.running:
            self.loop.run_until_complete(asyncio.sleep(0.01))
        self.loop.run_until_complete(self.messenger.disconnect())
        self.loop.close()

    def stop(self):
        self.running = False
        self.wait()

    def run_coroutine(self, coro):
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, self.loop)
