import threading
import websocket
import contextlib
import ujson as json

from time import time as timestamp
from .lib.util import objects

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
        return self.client.handle_socket_message(json.loads(data))

    def send(self, data):
        return self.socket.send(data)

    def start(self):
        self.headers = {
            "Upgrade": "websocket",
            "Connection": "Upgrade",
            "Sec-WebSocket-Key": "pxY4vNlXRCcFhsCh0hQ1vg==",
            "Sec-WebSocket-Version": "13",
            "rawDeviceId": self.client.device_id,
            "appType": "MainApp",
            "appVersion": "3.0.0",
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
            self.socket_url,
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
        try: self.socket.close()
        except websocket.WebSocketConnectionClosedException: return

class Callbacks:
    def __init__(self, client):
        self.client = client
        self.handlers = {}

        self.chat_methods = {
            "1": self.on_text_message,
            "2": self.on_image_message,
            "3": self.on_audio_message,
            "4": self.on_video_message,
            "5": self.on_delete_message,
            "10": self.on_user_join,
            "11": self.on_user_leave,
            "12": self.on_user_invite,
            "13": self.on_user_kick,
            "14": self.on_user_remove,
            "15": self.on_cohost_remove,
            "16": self.on_cohost_add,
            "17": self.on_host_delete_message,
            "18": self.on_cohost_delete_message,
            "20": self.on_role_play_invite,
            "21": self.on_free_talk_start,
            "22": self.on_free_talk_end,
            "23": self.on_role_play_start,
            "24": self.on_role_play_end,
            "25": self.on_voice_call_start,
            "26": self.on_voice_call_end,
            "27": self.on_voice_call_reject,
            "28": self.on_voice_call_cancel,
            "29": self.on_voice_call_accept,
            "30": self.on_free_talk_add_user,
            "31": self.on_free_talk_remove_user,
            "32": self.on_free_talk_invite,
            "33": self.on_free_talk_apply,
            "34": self.on_free_talk_accept,
            "35": self.on_live_talking_users,
            "36": self.on_free_talk_apply_count,
            "37": self.on_role_play_roles,
            "38": self.on_role_play_role_update,
            "39": self.on_role_play_apply_count,
            "40": self.on_conversation_level,
            "41": self.on_role_play_accept_apply,
            "42": self.on_role_play_user_role_remove,
            "43": self.on_chat_user_online,
            "50": self.on_chat_delete,
            "51": self.on_chat_host_update,
            "53": self.on_chat_disable,
            "60": self.on_user_typing,
            "90": self.on_chat_activity_type,
            "120": self.on_voice_call_not_answered,
        }

    def resolve(self, data):
        parsed = json.loads(json.dumps(data))
        methd = parsed["t"]
        if str(methd) == "1":
            key = parsed["msg"]["type"]
            return self.chat_methods.get(str(key), self.unknown)(parsed)

        if str(methd) == "11":
            return self.on_new_login_location(parsed)

    def call(self, type, data):
        if type in self.handlers:
            for handler in self.handlers[type]:
                handler(data)

    def event(self, type):
        def registerHandler(handler):
            if type in self.handlers:
                self.handlers[type].append(handler)
            else:
                self.handlers[type] = [handler]
            return handler

        return registerHandler

    def on_text_message(self, data): self.call("on_text_message", objects.Message(data["msg"]).Message)
    def on_image_message(self, data): self.call("on_image_message", objects.Message(data["msg"]).Message)
    def on_audio_message(self, data): self.call("on_audio_message", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_video_message(self, data): self.call("on_video_message", objects.Message(data["msg"]).Message)
    def on_delete_message(self, data): self.call("on_delete_message", objects.Message(data["msg"]).Message)
    def on_user_join(self, data): self.call("on_user_join", objects.Message(data["msg"]).Message)
    def on_user_leave(self, data): self.call("on_user_leave", objects.Message(data["msg"]).Message)
    def on_user_invite(self, data): self.call("on_user_invite", objects.Message(data["msg"]).Message)
    def on_user_kick(self, data): self.call("on_user_kick", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_user_remove(self, data): self.call("on_user_remove", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_cohost_remove(self, data): self.call("on_cohost_remove", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_cohost_add(self, data): self.call("on_cohost_add", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_host_delete_message(self, data): self.call("on_host_delete_message", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_cohost_delete_message(self, data): self.call("on_cohost_delete_message", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_role_play_invite(self, data): self.call("on_role_play_invite", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_free_talk_start(self, data): self.call("on_free_talk_start", objects.Message(data["msg"]).Message)
    def on_free_talk_end(self, data): self.call("on_free_talk_end", objects.Message(data["msg"]).Message)
    def on_role_play_start(self, data): self.call("on_role_play_start", objects.Message(data["msg"]).Message)
    def on_role_play_end(self, data): self.call("on_role_play_end", objects.Message(data["msg"]).Message)
    def on_voice_call_start(self, data): self.call("on_voice_call_start", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_voice_call_end(self, data): self.call("on_voice_call_end", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_voice_call_reject(self, data): self.call("on_voice_call_reject", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_voice_call_cancel(self, data): self.call("on_voice_call_cancel", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_voice_call_accept(self, data): self.call("on_voice_call_accept", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_free_talk_add_user(self, data): self.call("on_free_talk_add_user", objects.Message(data["msg"]).Message)
    def on_free_talk_remove_user(self, data): self.call("on_free_talk_remove_user", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_free_talk_invite(self, data): self.call("on_free_talk_invite", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_free_talk_apply(self, data): self.call("on_free_talk_apply", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_free_talk_accept(self, data): self.call("on_free_talk_accept", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_live_talking_users(self, data): self.call("on_live_talking_users", objects.Message(data["msg"]).Message)
    def on_free_talk_apply_count(self, data): self.call("on_free_talk_apply_count", objects.Message(data["msg"]).Message)
    def on_role_play_roles(self, data): self.call("on_role_play_roles", objects.Message(data["msg"]).Message)
    def on_role_play_role_update(self, data): self.call("on_role_play_role_update", objects.Message(data["msg"]).Message)
    def on_role_play_apply_count(self, data): self.call("on_role_play_apply_count", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_conversation_level(self, data): self.call("on_conversation_level", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_role_play_accept_apply(self, data): self.call("on_role_play_accept_apply", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_role_play_user_role_remove(self, data): self.call("on_role_play_user_role_remove", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_chat_user_online(self, data): self.call("on_chat_user_online", objects.Message(data["msg"]).Message)
    def on_chat_delete(self, data): self.call("on_chat_delete", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_chat_host_update(self, data): self.call("on_chat_host_update", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_chat_disable(self, data): self.call("on_chat_disable", objects.Message(data["msg"]).Message)  # TODO : Get actual response
    def on_user_typing(self, data): self.call("on_user_typing", objects.Message(data["msg"]).Message)
    def on_chat_activity_type(self, data): self.call("on_chat_activity_type", objects.Message(data["msg"]).Message)
    def on_voice_call_not_answered(self, data): self.call("on_voice_call_not_answered", objects.Message(data["msg"]).Message)  # TODO : Get actual response

    @staticmethod
    def unknown(data): print("UNKNOWN EVENT", data)

    def on_new_login_location(self, data): self.call("on_new_login_location", data)