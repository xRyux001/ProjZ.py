import threading
import time
import websocket
import contextlib

class SocketHandler:
    def __init__(self, client, socket_trace = False):
        websocket.enableTrace(True)
        self.socket_url = "wss://ws.projz.com"
        self.client = client
        self.active = False
        self.headers = None
        self.socket = None
        self.socket_thread = None
        self.reconnect = True

        websocket.enableTrace(socket_trace)

    def on_open(self):
        pass

    def on_close(self):
        self.active = False

        if self.reconnect:
            self.start()

    def on_ping(self, data):
        contextlib.suppress(self.socket.sock.pong(data))

    def handle_message(self, data):
        self.client.handle_socket_message(data)
        return

    def send(self, data):
        self.socket.send(data)

    def start(self):
        self.headers = {
            "rawDeviceId": self.client.device_id,
            "sId": self.client.sid
        }

        self.socket = websocket.WebSocketApp(
            f"{self.socket_url}/?signbody={self.client.device_id}%7C{int(time.time() * 1000)}",
            on_message = self.handle_message,
            on_open = self.on_open,
            on_close = self.on_close,
            on_ping = self.on_ping,
            header = self.headers
        )

        self.socket_thread = threading.Thread(target = self.socket.run_forever, kwargs = {"ping_interval": 60})
        self.socket_thread.start()
        self.active = True

    def close(self):
        self.reconnect = False
        self.active = False
        self.socket.close()