import threading
import time
import websocket
import contextlib
from time import time as timestamp

class SocketHandler:
    def __init__(self, client, socket_trace = False):
        websocket.enableTrace(True)
        self.socket_url = "wss://ws.projz.com/v1/chat/ws"
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
        sock = websocket.create_connection(url=self.socket_url, header = self.headers)
        return sock.send(data)

    def start(self):
        self.headers = {
            "Upgrade": "websocket",
            "Connection": "Upgrade",
            "Sec-WebSocket-Key": "pxY4vNlXRCcFhsCh0hQ1vg==",
            "Sec-WebSocket-Version": "13",
            "rawDeviceId": self.client.device_id,
            "appType": "MainApp",
            "appVersion": "1.0.3",
            "osType": "2",
            "deviceType": "1",
            "sId": self.client.sid,
            "countryCode": "PT",
            "reqTime": str(int(timestamp() * 1000)),
            "User-Agent": self.client.user_agent,
            "ContentRegion": "4",
            "Host": "ws.projz.com",
            "Accept-Encoding": "gzip"
        }

        self.socket = websocket.WebSocketApp(
            f"{self.socket_url}/?signbody={self.client.device_id}%7C{int(time.time() * 1000)}",
            on_message = self.handle_message,
            on_open = self.on_open,
            on_close = self.on_close,
            on_ping = self.on_ping,
            header = self.headers
        )

        self.socket_thread = threading.Thread(target = self.socket.run_forever, kwargs = {"ping_interval": 30})
        self.socket_thread.start()
        self.active = True

    def close(self):
        self.reconnect = False
        self.active = False
        self.socket.close()