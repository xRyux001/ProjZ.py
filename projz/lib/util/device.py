import json
from .helpers import generate_device_info

class DeviceGenerator:
    def __init__(self):
        try:
            with open("device.json", "r") as stream:
                data = json.load(stream)
                self.user_agent = data["user_agent"]
                self.device_id = data["rawDeviceId"]

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            device = generate_device_info()
            with open("device.json", "w") as stream:
                json.dump(device, stream)

            with open("device.json", "r") as stream:
                data = json.load(stream)
                self.user_agent = data["user_agent"]
                self.device_id = data["rawDeviceId"]