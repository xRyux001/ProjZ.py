from time import time as timestamp
from projz.lib.util import device

sid = None

class Headers:
    def __init__(self, device = device.DeviceGenerator(), data = None, type = None):
        headers = {
            "rawDeviceId": device.device_id,
            "appType": "MainApp",
            "appVersion": device.app_version,
            "osType": "2",
            "deviceType": "1",
            "countryCode": device.country_code,
            "contentRegion": device.content_region,
            "reqTime": str(int(timestamp() * 1000)),
            "Accept-Language": "en-US",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": device.user_agent,
            "Host": "api.projz.com",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }

        if data: headers["Content-Length"] = str(len(data))
        if sid: headers["sId"] = sid
        if type: headers["Content-Type"] = type
        self.headers = headers
