import ujson as json
from .helpers import generate_device_info

class DeviceGenerator:
    def __init__(self, deviceId: str = None):
        try:
            with open("device.json", "r") as stream:
                data = json.load(stream)

                if deviceId is not None: self.device_id = deviceId
                else: self.device_id = data["RawDeviceId"]

                self.app_version = data["AppVersion"]
                self.user_agent = data["UserAgent"]
                self.country_code = data["CountryCode"]
                self.content_region = data["ContentRegion"]

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            device = generate_device_info()
            if deviceId is not None: device["RawDeviceId"] = deviceId

            with open("device.json", "w") as stream:
                json.dump(device, stream, indent=4)

            with open("device.json", "r") as stream:
                data = json.load(stream)
                self.device_id = data["RawDeviceId"]
                self.app_version = data["AppVersion"]
                self.user_agent = data["UserAgent"]
                self.country_code = data["CountryCode"]
                self.content_region = data["ContentRegion"]