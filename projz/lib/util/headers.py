from time import time as timestamp
from projz.lib.util import device

sid = None

class Headers:
    def __init__(self, deviceId = None, data = None, type = None):
        if deviceId is not None: dev = device.DeviceGenerator(deviceId=deviceId)
        else: dev = device.DeviceGenerator()

        headers = {
            "rawDeviceId": dev.device_id,
            "appType": "MainApp",
            "appVersion": dev.app_version,
            "osType": "2",
            "deviceType": "1",
            "countryCode": dev.country_code,
            "contentRegion": dev.content_region,
            "reqTime": str(int(timestamp() * 1000)),
            "Accept-Language": "en-US",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": dev.user_agent,
            "Host": "api.projz.com",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }

        if data: headers["Content-Length"] = str(len(data))
        if sid: headers["sId"] = sid
        if type: headers["Content-Type"] = type
        self.headers = headers
