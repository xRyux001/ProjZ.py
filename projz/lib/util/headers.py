from time import time as timestamp
from projz.lib.util import device
from binascii import hexlify
from uuid import UUID
import os

sid = None

class Headers:
    def __init__(self, device = device.DeviceGenerator(), data = None, type = None):
        headers = {
            "rawDeviceId": device.device_id,
            "appType": "en-US",
            "appVersion": "1.0.4",
            "osType": "2",
            "deviceType": "1",
            "countryCode": "PT",
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
        if type: headers["Content-Type"] = self.encode_multipart_formdata(fields={"media": str(data)}, length=str(len(data)), type=type)
        self.headers = headers

    @staticmethod
    def encode_multipart_formdata(fields, type, length):
        boundary = UUID(hexlify(os.urandom(16)).decode('ascii'))

        body = "".join("--%s\r\n"
                        "Content-Disposition: form-data; name=\"%s\"; filename=\"media_6999872595940526489.\"\r\n"
                        "Content-Type: %s\r\n"
                        "Content-Length: %s\r\n"
                        "\r\n"
                        "%s\r\n" % (boundary, type, length, field, value)
                        for field, value in fields.items()) + "--%s--\r\n" % boundary

        content_type = "multipart/form-data; boundary=%s" % boundary

        return content_type, body
