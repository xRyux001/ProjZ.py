import ffmpeg
import requests

import ujson as json
from uuid import UUID
from os import urandom
from random import choice
from typing import BinaryIO
from binascii import hexlify
from io import BufferedReader
from time import time as timestamp

from .socket import SocketHandler, Callbacks
from .lib.util import exceptions, headers, device, objects

class Client:
    def __init__(self, deviceId: str = None, callback = Callbacks, proxies: dict = None, certificatePath = None, socket_trace = False):
        if deviceId is not None:
            self.device = device.DeviceGenerator(deviceId=deviceId)
            self.headers = headers.Headers(deviceId=deviceId).headers

        else:
            self.device = device.DeviceGenerator()
            self.headers = headers.Headers().headers

        self.api = "https://api.projz.com/v1"
        self.apiWeb = "https://projz.com/api/web"
        self.authenticated = False
        self.configured = False
        self.device_id = self.device.device_id
        self.user_agent = self.device.user_agent
        self.socket = SocketHandler(self, socket_trace=socket_trace)
        self.callbacks = callback(self)
        self.proxies = proxies
        self.certificatePath = certificatePath

        self.json = None
        self.sid = None
        self.userId = None
        self.account: objects.UserProfile = objects.UserProfile(None)
        self.profile: objects.UserProfile = objects.UserProfile(None)

    @staticmethod
    def type_(obj):
        return type(obj)

    def login(self, email: str = None, phone_number: str = None, *, password: str):
        if email is not None: authType = 1
        elif phone_number is not None: authType = 2
        else: raise exceptions.SpecifyType

        data = json.dumps({
            "authType": authType,
            "birthday": "",
            "email": email,
            "gender": 0,
            "invitationCode": "",
            "nickname": "",
            "password": password,
            "phoneNumber": "",
            "purpose": 0,
            "school": "",
            "secret": "",
            "securityCode": ""
        })

        response = requests.post(f"{self.api}/auth/login", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))

        else:
            self.authenticated = True
            self.json = json.loads(response.text)
            self.sid = self.json["sId"]
            self.userId = self.json["userProfile"]["uid"]
            self.account: objects.UserProfile = objects.UserProfile(self.json["account"]).UserProfile
            self.profile: objects.UserProfile = objects.UserProfile(self.json["userProfile"]).UserProfile
            headers.sid = self.sid
            self.socket.start()
            return response.status_code

    def logout(self):
        if self.authenticated is False: raise exceptions.NotLoggedIn()
        data = json.dumps({})
        response = requests.post(f"{self.api}/auth/logout", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))

        else:
            self.authenticated, self.json, self.sid, self.userId, self.account, self.profile, headers.sid = False, None, None, None, None, None, None
            self.socket.close()
            return response.status_code

    def register(self, email: str, nickname: str, password: str, icon: BinaryIO, invitationCode: str, securityCode: str, birthday: str = None, school: str = None, gender: str = None, contentRegion: str = None):
        if contentRegion is not None:
            if contentRegion.lower() in ["english", "en"]: contentRegion = 1
            elif contentRegion.lower() in ["arabic", "ar"]: contentRegion = 2
            elif contentRegion.lower() in ["russian", "ru"]: contentRegion = 3
            elif contentRegion.lower() in ["portuguese", "pt"]: contentRegion = 4
            elif contentRegion.lower() in ["spanish", "es"]: contentRegion = 5
            elif contentRegion.lower() in ["german", "de"]: contentRegion = 6
            elif contentRegion.lower() in ["french", "fr"]: contentRegion = 7
            elif contentRegion.lower() in ["rest", "other", "all"]: contentRegion = 100
            else: raise exceptions.InvalidRegion(contentRegion)

        if gender is not None:
            if gender.lower() == "male": gender = 1
            elif gender.lower() == "female": gender = 2
            elif gender.lower() == "other": gender = 100
            else: raise exceptions.WrongType(gender)

        else: gender = 100

        # Format yyyy-mm-dd
        if birthday is not None: birthday = birthday
        else: birthday = "2000-01-01"

        data = json.dumps({
            "authType": 1,
            "birthday": birthday,
            "icon": self.upload_media(file=icon, target=1),
            "contentRegion": contentRegion,
            "email": email,
            "gender": gender,
            "invitationCode": invitationCode,
            "nickname": nickname,
            "password": password,
            "phoneNumber": "",
            "purpose": 1,
            "school": school,
            "secret": "",
            "securityCode": securityCode
        })

        response = requests.post(f"{self.api}/auth/register", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def change_password(self, oldPassword: str, newPassword: str):
        data = json.dumps({
            "newPassword": newPassword,
            "oldPassword": oldPassword
        })

        response = requests.post(f"{self.api}/auth/change-password", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else:
            self.sid = json.loads(response.text)["sId"]
            return response.status_code

    def request_code(self, email: str = None, phoneNumber: str = None, registerEmail: bool = False, changeEmail: bool = False, changePhoneNumber: bool = False):
        data = {
            "birthday": "",
            "contentRegion": 0,
            "email": email,
            "gender": 0,
            "invitationCode": "",
            "nickname": "",
            "password": "",
            "phoneNumber": phoneNumber,
            "school": "",
            "secret": "",
            "securityCode": ""
        }

        if registerEmail is True: data["authType"], data["purpose"] = 1, 1
        if changeEmail is True: data["authType"], data["purpose"] = 1, 3
        if changePhoneNumber is True: data["authType"], data["purpose"] = 2, 4

        data = json.dumps(data)
        response = requests.post(f"{self.api}/auth/request-security-validation", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def check_invitation_code(self, code: str):
        data = json.dumps({
            "authType": 1,
            "birthday": "",
            "email": "",
            "gender": 0,
            "invitationCode": code,
            "nickname": "",
            "password": "",
            "phoneNumber": " ",
            "purpose": 1,
            "school": "",
            "secret": "",
            "securityCode": ""
        })

        response = requests.post(f"{self.api}/auth/check-invitation-code", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_account_info(self):
        response = requests.get(f"{self.api}/auth/account", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def get_alerts_info(self):
        response = requests.get(f"{self.api}/alerts/check", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.AlertsInfo(json.loads(response.text)).AlertsInfo

    def get_gift_info(self):
        response = requests.get(f"{self.api}/users/gift-info", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GiftInfo(json.loads(response.text)).GiftInfo

    def claim_gift(self):
        data = json.dumps({})
        response = requests.post(f"{self.api}/users/claim-gift", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_alerts(self, type: str, size: int = 25, pageToken: str = None):
        if type.lower() == "activity":
            if pageToken is not None: url = f"{self.api}/alerts?groupId=1&size={size}&pageToken={pageToken}"
            else: url = f"{self.api}/alerts?groupId=1&size={size}"
        elif type.lower() == "likes":
            if pageToken is not None: url = f"{self.api}/alerts?groupId=2&size={size}&pageToken={pageToken}"
            else: url = f"{self.api}/alerts?groupId=2&size={size}"
        elif type.lower() == "followers":
            if pageToken is not None: url = f"{self.api}/alerts?groupId=3&size={size}&pageToken={pageToken}"
            else: url = f"{self.api}/alerts?groupId=3&size={size}"
        elif type.lower() == "announcements":
            if pageToken is not None: url = f"{self.api}/alerts/global-announcement?size={size}&pageToken={pageToken}"
            else: url = f"{self.api}/alerts/global-announcement?size={size}"

        else: raise exceptions.WrongType(type)

        response = requests.get(url, headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetAlerts(json.loads(response.text)).GetAlerts

    def get_global_announcements(self, size: int = 25):
        response = requests.get(f"{self.api}/alerts/global-announcement?size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.BlogList(json.loads(response.text)["list"]).BlogList

    def get_invitation_codes(self, size: int = 25):
        response = requests.get(f"{self.api}/users/invitation-codes?size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.InviteCodeList(json.loads(response.text)["list"]).InviteCodeList

    def get_invitation_count(self):
        response = requests.get(f"{self.api}/users/invitation-codes/count", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.InviteCodeCount(json.loads(response.text)).InviteCodeCount

    # Todo : Figure out what data is returned
    def get_blocked_users(self):
        response = requests.get(f"{self.api}/users/block-uids", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)["blockedByMeList"]

    # Todo : Figure out what data is returned
    def get_blocker_users(self):
        response = requests.get(f"{self.api}/users/block-uids", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)["blockMeList"]

    def get_content_regions(self):
        response = requests.get(f"{self.api}/configs/content-regions", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.ContentRegionList(json.loads(response.text)["list"]).ContentRegionList

    def get_invitation_code_info(self):
        response = requests.get(f"{self.api}/users/invitation-code-info", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def get_user_info(self, userId: int):
        response = requests.get(f"{self.api}/users/profile/{userId}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfile(json.loads(response.text)).UserProfile

    def get_user_following(self, userId: int, size: int = 25):
        response = requests.get(f"{self.api}/users/membership/{userId}?type=following&size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["list"]).UserProfileList

    def get_user_followers(self, userId: int, size: int = 25):
        response = requests.get(f"{self.api}/users/membership/{userId}?type=follower&size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["list"]).UserProfileList

    def get_user_achievements(self, userId: int, size: int = 25):
        response = requests.get(f"{self.api}/users/achievements?uid={userId}&size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.AchievementList(json.loads(response.text)["list"]).AchievementList

    def get_all_users(self, size: int = 25, pageToken: str = None):
        if pageToken is not None: url = f"{self.api}/search/users?size={size}&pageToken={pageToken}"
        else: url = f"{self.api}/search/users?size={size}"

        response = requests.get(url, headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetUsers(json.loads(response.text)).GetUsers

    def get_rec_following(self, size: int = 25, pageToken: str = None):
        if pageToken is not None: url = f"{self.api}/users/rec-following?size={size}&pageToken={pageToken}"
        else: url = f"{self.api}/users/rec-following?size={size}"

        response = requests.get(url, headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetUsers(json.loads(response.text)).GetUsers

    def get_namecards(self, gender: str, size: int = 25, pageToken: str = None):
        if gender.lower() == "all":
            if pageToken is not None: url = f"{self.api}/users/namecards?gender=0&pageToken={pageToken}&size={size}"
            else: url = f"{self.api}/users/namecards?gender=0&size={size}"

        elif gender.lower() == "male":
            if pageToken is not None: url = f"{self.api}/users/namecards?gender=1&pageToken={pageToken}&size={size}"
            else: url = f"{self.api}/users/namecards?gender=1&size={size}"

        elif gender.lower() == "female":
            if pageToken is not None: url = f"{self.api}/users/namecards?gender=2&pageToken={pageToken}&size={size}"
            else: url = f"{self.api}/users/namecards?gender=2&size={size}"

        elif gender.lower() == "other":
            if pageToken is not None: url = f"{self.api}/users/namecards?gender=100&pageToken={pageToken}&size={size}"
            else: url = f"{self.api}/users/namecards?gender=100&size={size}"

        else: raise exceptions.WrongType(gender)

        response = requests.get(url, headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetUsers(json.loads(response.text)).GetUsers

    def get_blog_info(self, blogId: int):
        response = requests.get(f"{self.api}/blogs/{blogId}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.Blog(json.loads(response.text)).Blog

    def get_blogs(self, type: str = "latest", circleId: int = None, start: int = 0, size: int = 25, pageToken: str = None):
        if type.lower() == "latest":
            if pageToken is not None: url = f"{self.api}/blogs?type=latest&pageToken={pageToken}&size={size}"
            else: url = f"{self.api}/blogs?type=latest&start={start}&size={size}"

        elif type.lower() == "popular":
            if pageToken is not None: url = f"{self.api}/blogs?type=popular&pageToken={pageToken}&size={size}"
            else: url = f"{self.api}/blogs?type=popular&start={start}&size={size}"

        elif type.lower() == "following":
            if pageToken is not None: url = f"{self.api}/blogs?type=following&pageToken={pageToken}&size={size}"
            else: url = f"{self.api}/blogs?type=following&start={start}&size={size}"

        elif type.lower() == "circle":
            if pageToken is not None: url = f"{self.api}/blogs?type=circle&circleId={circleId}&pageToken={pageToken}&size={size}"
            else: url = f"{self.api}/blogs?type=circle&circleId={circleId}&size={size}"

        else: raise exceptions.WrongType(type)

        response = requests.get(url, headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetBlogs(json.loads(response.text)).GetBlogs

    def get_blog_comments(self, blogId: int, size: int = 25):
        response = requests.get(f"{self.api}/comments?{blogId}&replyId=0&size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.CommentList(json.loads(response.text)["list"]).CommentList

    def get_blog_likes(self, blogId: int, size: int = 25):
        response = requests.get(f"{self.api}/votes?objectId={blogId}&size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.CommentList(json.loads(response.text)["list"]).CommentList

    def post_blog(self, content: str, fileList: list = None, circleIdList: list = None, visibility: str = None, commentsDisabled: bool = False):
        # all public pages - a
        # public profile - b
        # a,n b,y - 252 (linked circle, public profile)
        # a,n b,n - 254 (linked circle only)
        # a,y b,y - 0 (all)
        # a,y b,n - 2 (linked circle, public pages)
        # only me - 255

        if circleIdList is not None: circleIdList = [i for i in circleIdList]
        if visibility is not None:
            if "all" in visibility or "everyone" in visibility: visibility = 0
            elif "circles" in visibility and "pages" in visibility: visibility = 2
            elif "circles" in visibility and "profile" in visibility: visibility = 252
            elif "circles" in visibility: visibility = 254
            elif "nobody" in visibility or "none" in visibility: visibility = 255
            else: visibility = 0

        if fileList is not None:
            mediaList = []
            for file in fileList:
                if type(file) == BinaryIO or type(file) == BufferedReader:
                    mediaList.append(self.upload_media(file=file, target=3))
                else:
                    raise exceptions.InvalidFile(type(file))

        else: mediaList = None

        data = json.dumps({
            "blogId": 0,
            "circleIdList": circleIdList,
            "content": content,
            "extensions": {
                "contentStatus": 1,
                "commentDisabled": commentsDisabled
            },
            "mediaList": mediaList,
            "status": 1,
            "type": 1,
            "visibility": visibility,
            "uid": 0
        })

        response = requests.post(f"{self.api}/blogs", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def edit_blog(self, blogId: int, content: str, mediaList: list = None, circleIdList: list = None, visibility: str = None, commentsDisabled: bool = False, type: int = 1):
        if circleIdList is not None: circleIdList = [i for i in circleIdList]
        if visibility is not None:
            if "all" in visibility or "everyone" in visibility: visibility = 0
            elif "circles" in visibility and "pages" in visibility: visibility = 2
            elif "circles" in visibility and "profile" in visibility: visibility = 252
            elif "circles" in visibility: visibility = 254
            elif "nobody" in visibility or "none" in visibility: visibility = 255
            else: visibility = 0

        data = json.dumps({
            "blogId": 0,
            "circleIdList": circleIdList,
            "content": content,
            "extensions": {
                "contentStatus": 1,
                "commentDisabled": commentsDisabled
            },
            "mediaList": mediaList,
            "status": 1,
            "type": type,
            "visibility": visibility,
            "uid": 0
        })

        response = requests.post(f"{self.api}/blogs/{blogId}", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def delete_blog(self, blogId: int, circleId: int = None):
        if circleId is not None: url = f"{self.api}/circles/{circleId}/blogs/{blogId}"
        else: url = f"{self.api}/blogs/{blogId}"

        response = requests.delete(url, headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def remove_blog(self, blogId: int, circleId: int = None):
        self.delete_blog(blogId, circleId)

    def like_blog(self, circleId: int = None, blogId: int = None, commentId: str = None):
        if circleId is not None: circleId = circleId
        else: circleId = 0

        if blogId is not None: objId, objType = blogId, 2
        elif commentId is not None: objId, objType = commentId, 3
        else: raise exceptions.SpecifyType

        data = json.dumps({
            "circleId": circleId,
            "objectId": objId,
            "objectType": objType
        })

        response = requests.post(f"{self.api}/votes", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_user_blogs(self, userId: int, size: int = 25):
        response = requests.get(f"{self.api}/blogs?type=user&targetUid={userId}&size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetBlogs(json.loads(response.text)).GetBlogs

    def follow(self, userId: int):
        data = json.dumps({})
        response = requests.post(f"{self.api}/users/membership/{userId}", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def unfollow(self, userId: int):
        data = json.dumps({})
        response = requests.delete(f"{self.api}/users/membership/{userId}", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def block(self, userId: int):
        data = json.dumps({})
        response = requests.post(f"{self.api}/users/block/{userId}", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def unblock(self, userId: int):
        data = json.dumps({})
        response = requests.delete(f"{self.api}/users/block/{userId}", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def edit_profile(self, nickname: str = None, bio: str = None, background: BinaryIO = None, voiceBio: BinaryIO = None, gender: str = None, school: str = None, address: str = None, socialId: str = None, nameCard: bool = None, showsSchool: bool = None, showsJoinedCircles: bool = None, showsLocation: bool = None, nameCardBackground: BinaryIO = None, contentRegion: str = None, chatInvitationStatus: str = None, latitude: float = None, longitude: float = None):
        if gender is not None:
            if gender.lower() == "male": gender = 1
            elif gender.lower() == "female": gender = 2
            elif gender.lower() == "other": gender = 100
            else: raise exceptions.WrongType(gender)

        if background is not None: background = self.upload_media(file=background, target=2)
        if voiceBio is not None: voiceBio = self.upload_media(file=voiceBio, target=5)
        if nameCardBackground is not None: nameCardBackground = self.upload_media(file=nameCardBackground, target=11)

        if showsSchool is not None:
            if showsSchool is True: showsSchool = "1"
            elif showsSchool is False: showsSchool = "2"
            else: raise exceptions.WrongType(showsSchool)

        if showsJoinedCircles is not None:
            if showsJoinedCircles is True: showsJoinedCircles = "1"
            elif showsJoinedCircles is False: showsJoinedCircles = "2"
            else: raise exceptions.WrongType(showsJoinedCircles)

        if showsLocation is not None:
            if showsLocation is True: showsLocation = "1"
            elif showsLocation is False: showsLocation = "2"
            else: raise exceptions.WrongType(showsLocation)

        if chatInvitationStatus is not None:
            if chatInvitationStatus.lower() == "everyone" or chatInvitationStatus.lower() == "all": chatInvitationStatus = 1
            elif chatInvitationStatus.lower() == "following": chatInvitationStatus = 2
            elif chatInvitationStatus.lower() == "friends": chatInvitationStatus = 3
            elif chatInvitationStatus.lower() == "off" or chatInvitationStatus.lower() == "nobody": chatInvitationStatus = 4
            else: raise exceptions.WrongType(chatInvitationStatus)

        if contentRegion is not None:
            if contentRegion.lower() in ["english", "en"]: contentRegion = 1
            elif contentRegion.lower() in ["arabic", "ar"]: contentRegion = 2
            elif contentRegion.lower() in ["russian", "ru"]: contentRegion = 3
            elif contentRegion.lower() in ["portuguese", "pt"]: contentRegion = 4
            elif contentRegion.lower() in ["spanish", "es"]: contentRegion = 5
            elif contentRegion.lower() in ["german", "de"]: contentRegion = 6
            elif contentRegion.lower() in ["french", "fr"]: contentRegion = 7
            elif contentRegion.lower() in ["rest", "other", "all"]: contentRegion = 100
            else: raise exceptions.InvalidRegion(contentRegion)

        if nameCard is not None:
            if nameCard: nameCard = 1
            else: nameCard = 2

        data = json.dumps({
            "nickname": nickname,
            "bio": bio,
            "background": background,
            "voiceBio": voiceBio,
            "gender": gender,
            "school": school,
            "socialId": socialId,
            "location": {
                "address": {
                    "en": address
                },
                "latitude": latitude,
                "longitude": longitude
            },
            "showsSchool": showsSchool,
            "nameCardEnabled": nameCard,
            "nameCardBackground": nameCardBackground,
            "showsJoinedCircles": showsJoinedCircles,
            "showsLocation": showsLocation,
            "chatInvitationStatus": chatInvitationStatus,
            "contentRegion": contentRegion,
            "status": 1
        })

        response = requests.post(f"{self.api}/users/profile/{self.userId}/update-profile", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def edit_chat(self, chatId: int, title: str = None, content: str = None, coHosts: list = None, pinChat: bool = None, doNotDisturb: bool = None, allowMembersInvite: bool = None):
        data, responses = {}, []

        if title is not None: data["title"] = title
        if content is not None: data["content"] = content

        data = json.dumps(data)

        if coHosts is not None:
            data_coHosts = json.dumps({"coHostUids": [i for i in coHosts]})
            response = requests.post(f"{self.api}/chat/threads/{chatId}/co-host", headers=headers.Headers(data=data_coHosts).headers, data=data_coHosts, proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: responses.append(exceptions.CheckException(json.loads(response.text)))
            else: responses.append(response.status_code)

        if pinChat is not None:
            if pinChat is True: response = requests.post(f"{self.api}/chat/threads/{chatId}/pin", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
            elif pinChat is False: response = requests.post(f"{self.api}/chat/threads/{chatId}/unpin", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
            else: raise exceptions.WrongType(pinChat)

            if response.status_code != 200: responses.append(exceptions.CheckException(json.loads(response.text)))
            else: responses.append(response.status_code)

        if doNotDisturb is not None:
            if doNotDisturb is True: response = requests.post(f"{self.api}/chat/threads/{chatId}/alert-option/2", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
            elif doNotDisturb is False: response = requests.post(f"{self.api}/chat/threads/{chatId}/alert-option/1", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
            else: raise exceptions.WrongType(doNotDisturb)

            if response.status_code != 200: responses.append(exceptions.CheckException(json.loads(response.text)))
            else: responses.append(response.status_code)

        if allowMembersInvite is not None:
            if allowMembersInvite is True: response = requests.post(f"{self.api}/chat/threads/{chatId}/members-invite/enable", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
            elif allowMembersInvite is False: response = requests.post(f"{self.api}/chat/threads/{chatId}/members-invite/disable", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
            else: raise exceptions.WrongType(allowMembersInvite)

            if response.status_code != 200: responses.append(exceptions.CheckException(json.loads(response.text)))
            else: responses.append(response.status_code)

        response = requests.post(f"{self.api}/chat/threads/{chatId}", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: responses.append(exceptions.CheckException(json.loads(response.text)))
        else: responses.append(response.status_code)

        return responses

    def transfer_host(self, chatId: int, userId: int):
        data = json.dumps({})
        response = requests.post(f"{self.api}/chat/threads/{chatId}/host/{userId}", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def kick(self, chatId: int, userId: int, blockRejoin: bool = False):
        data = json.dumps({})
        response = requests.delete(f"{self.api}/chat/threads/{chatId}/members/{userId}?block={blockRejoin}", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_chat_threads(self, type: str = "joined", circleId: int = None, start: int = 0, size: int = 25, pageToken: str = None):
        if type.lower() == "joined":
            if pageToken is not None: url = f"{self.api}/chat/joined-threads?pageToken={pageToken}&size={size}"
            else: url = f"{self.api}/chat/joined-threads?start={start}&size={size}"

        elif type.lower() == "recommended":
            if pageToken is not None: url = f"{self.api}/chat/threads?type=recommend&pageToken={pageToken}&size={size}"
            else: url = f"{self.api}/chat/threads?type=recommend&start={start}&size={size}"

        elif type.lower() == "circle":
            if pageToken is not None: url = f"{self.api}/chat/threads?type=circle&objectId={circleId}&pageToken={pageToken}&size={size}"
            else: url = f"{self.api}/chat/threads?type=circle&objectId={circleId}&start={start}&size={size}"

        elif type.lower() == "hot":
            if pageToken is not None: url = f"{self.api}/chat/hot-threads?pageToken={pageToken}&size={size}"
            else: url = f"{self.api}/chat/hot-threads?size={size}"

        else: raise exceptions.WrongType(type)

        response = requests.get(url, headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetChats(json.loads(response.text)).GetChats

    def get_chat_messages(self, chatId: int, size: int = 25, pageToken: str = None):
        if pageToken is None: response = requests.get(f"{self.api}/chat/threads/{chatId}/messages?size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        else: response = requests.get(f"{self.api}/chat/threads/{chatId}/messages?size={size}&pageToken={pageToken}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetChatMessages(json.loads(response.text)).GetChatMessages

    def get_chat_online_users(self, chatId: int, size: int = 25):
        response = requests.get(f"{self.api}/chat/threads/{chatId}/online-members?size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["list"]).UserProfileList

    def get_chat_users(self, chatId: int, size: int = 25):
        response = requests.get(f"{self.api}/chat/threads/{chatId}/members?size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["list"]).UserProfileList

    def apply_for_role(self, chatId: int, roleId: str):
        data = json.dumps({})
        response = requests.post(f"{self.api}/chat/threads/{chatId}/roles/{roleId}/apply", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def join_chat(self, chatId: int):
        data = json.dumps({})
        response = requests.post(f"{self.api}/chat/threads/{chatId}/members", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def leave_chat(self, chatId: int):
        response = requests.delete(f"{self.api}/chat/threads/{chatId}/members", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_circle_info(self, circleId: int):
        response = requests.get(f"{self.api}/circles/{circleId}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.Circle(json.loads(response.text)).Circle

    def get_circles(self, type: str, size: int = 25):
        if type.lower() == "joined": url = f"{self.api}/circles?type=joined&size={size}"
        elif type.lower() == "latest": url = f"{self.api}/circles?type=latest&size={size}"
        else: raise exceptions.WrongType(type)

        response = requests.get(url, headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetUsers(json.loads(response.text)).GetUsers

    def get_circle_users(self, circleId: int, type: str = "normal", start: int = 0, size: int = 25, pageToken: str = None):
        # type can be "normal" or "blocked"

        if pageToken is not None: url = f"{self.api}/circles/{circleId}/members?type={type}&pageToken={pageToken}&size={size}"
        else: url = f"{self.api}/circles/{circleId}/members?type={type}&start={start}&size={size}"

        response = requests.get(url, headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.Circle(json.loads(response.text)).Circle

    def create_circle(self, title: str, tagline: str, icon: BinaryIO, description: str = None, tagList: list = None, language: str = "en", background: BinaryIO = None):
        if icon is not None:
            if type(icon) == BinaryIO: icon = self.upload_media(file=icon, target=1)
            else: raise exceptions.InvalidFile

        if background is not None:
            if type(background) == BinaryIO: background = self.upload_media(file=background, target=1)
            else: raise exceptions.InvalidFile

        else:
            background = choice(self.get_default_backgrounds())

        data = json.dumps({
            "background": background,
            "circleId": 0,
            "icon": icon,
            "language": language,
            "name": title,
            "status": 1,
            "tagStrList": tagList,
            "tagline": tagline,
            "description": description,
            "uid": 0
        })

        response = requests.post(f"{self.api}/circles", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def edit_circle(self, circleId: int, title: str, tagline: str, icon: BinaryIO, description: str = None, tagList: list = None, language: str = "en", background: BinaryIO = None):
        if icon is not None:
            if type(icon) == BinaryIO: icon = self.upload_media(file=icon, target=1)
            else: raise exceptions.InvalidFile

        if background is not None:
            if type(background) == BinaryIO: background = self.upload_media(file=background, target=1)
            else: raise exceptions.InvalidFile

        else:
            background = choice(self.get_default_backgrounds())

        data = json.dumps({
            "background": background,
            "circleId": 0,
            "icon": icon,
            "language": language,
            "name": title,
            "status": 1,
            "tagStrList": tagList,
            "tagline": tagline,
            "description": description,
            "uid": 0
        })

        response = requests.post(f"{self.api}/circles/{circleId}", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def delete_circle(self, circleId: int):
        response = requests.delete(f"{self.api}/circles/{circleId}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def join_circle(self, circleId: int):
        data = json.dumps({})
        response = requests.post(f"{self.api}/circles/{circleId}/members", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def leave_circle(self, circleId: int):
        response = requests.delete(f"{self.api}/circles/{circleId}/members", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def pin_blog(self, blogId: int, circleId: int):
        data = json.dumps({})
        response = requests.post(f"{self.api}/circles/{circleId}/blogs/{blogId}/pin", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def unpin_blog(self, blogId: int, circleId: int):
        data = json.dumps({})
        response = requests.post(f"{self.api}/circles/{circleId}/blogs/{blogId}/unpin", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_tag_info(self, tagId: str):
        response = requests.get(f"{self.api}/tags?tagId={tagId}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.Tag(json.loads(response.text)).Tag

    def comment(self, message: str, blogId: int = None, replyTo: str = None):
        if blogId is not None: targetId = blogId
        else: raise exceptions.SpecifyType

        if replyTo is not None: replyTo = replyTo
        else: replyTo = 0

        data = json.dumps({
            "circleId": 0,
            "commentId": 0,
            "commentType": 1,
            "content": message,
            "mediaList": [],
            "parentId": targetId,
            "parentType": 2,
            "replyId": replyTo,
            "status": 1,
            "subComments": [],
            "subCommentsCount": 0,
            "uid": 0
        })

        response = requests.post(f"{self.api}/comments", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def delete_comment(self, commentId: str):
        response = requests.delete(f"{self.api}/comments/{commentId}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def share(self, url: str = None, userId: int = None, chatId: int = None, circleId: int = None):
        if url is not None:
            if "www.projz.com" in url:
                data = json.dumps({"link": url})
                response = requests.post(f"{self.api}/links/path", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

            else: raise exceptions.InvalidUrl(url)

        else:
            if userId is not None: objId, objType, objPath = 0, 0, f"user/{userId}"
            elif chatId is not None: objId, objType, objPath = 0, 0, f"chat/{chatId}"
            elif circleId is not None: objId, objType, objPath = 0, 0, f"circle/{circleId}"
            else: raise exceptions.SpecifyType()

            data = json.dumps({
                "objectId": objId,
                "objectType": objType,
                "path": objPath
            })

            response = requests.post(f"{self.api}/links/share", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.Share(json.loads(response.text)).Share

    def upload_media(self, file: BinaryIO, target: int):
        data = file.read()
        boundary = UUID(hexlify(urandom(16)).decode('ascii'))

        prob = ffmpeg.probe(file.name)["format"]

        if prob["format_name"] == "aac":
            duration = round(float(prob["duration"]) * 1000)
            fileExt = "aac"; fileExt2 = "aac"; fileType = "audio"; target = 5
        else:
            duration = 0
            if "png" in str(data).lower(): fileExt = "png"; fileExt2 = "png"; fileType = "image"
            elif "jpg" or "jfif" in str(data).lower(): fileExt = "jpg"; fileExt2 = "jpeg"; fileType = "image"
            elif "jpeg" in str(data).lower(): fileExt = "jpeg"; fileExt2 = "jpeg"; fileType = "image"
            elif "gif" in str(data).lower(): fileExt = "gif"; fileExt2 = "gif"; fileType = "image"
            else: raise exceptions.InvalidFileExtension(data)

        head = headers.Headers(type=f"multipart/form-data; boundary={boundary}").headers
        files = {'media': (f"projzpy_media_{fileExt}", data, f"{fileType}/{fileExt2}", {'Content-Type': f"{fileType}/{fileExt2}", "Content-Length": len(data)})}
        session = requests.Session()
        request = requests.Request("POST", f"https://api.projz.com/v1/media/upload?target={target}&duration={duration}", files=files, headers=head)
        prepped = request.prepare()
        reqbody = str(prepped.body)
        reqbody.replace(reqbody[:36][4:], str(UUID(reqbody[:36][4:])))
        prepped.headers["Content-Type"] = f"multipart/form-data; boundary={reqbody[:36][4:]}"
        response = session.send(prepped, proxies=self.proxies, verify=self.certificatePath)

        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def get_default_backgrounds(self):
        response = requests.get(f"{self.api}/media/default?type=5", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def send_message(self, message: str, chatId: int, messageType: int = 1, file: BinaryIO = None, replyMessageId: int = None):
        if self.authenticated is False: raise exceptions.NotLoggedIn

        if file is not None: file = self.upload_media(file=file, target=8)

        request = self.socket.send(json.dumps({
                "t": 1,
                "threadId": chatId,
                "msg": {
                    "type": messageType,
                    "status": 1,
                    "threadId": chatId,
                    "uid": self.userId,
                    "extensions": {
                        "friendshipLevel": 1,
                        "replyMessageId": replyMessageId
                    },
                    "media": file,
                    "refId": int(timestamp() * 1000),
                    "content": message,
                    "messageId": 0
                }}))

        return request

    def send_chat_active(self, chatId: int):
        if self.authenticated is False: raise exceptions.NotLoggedIn
        return self.socket.send(json.dumps({"t": 6, "threadId": chatId}))

    def send_chat_unactive(self, chatId: int):
        if self.authenticated is False: raise exceptions.NotLoggedIn
        return self.socket.send(json.dumps({"t": 7, "threadId": chatId}))

    def mark_message_as_read(self, chatId: int, messageId: int):
        if self.authenticated is False: raise exceptions.NotLoggedIn
        return self.socket.send(json.dumps({"t": 3, "threadId": chatId, "clientAck": {"threadId": chatId, "messageId": messageId, "markAsRead": True}}))

    def mark_chat_as_read(self, chatId: int):
        data = json.dumps({})
        response = requests.post(f"{self.api}/chat/threads/{chatId}/mark-as-read", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def send_control_message(self, message: str, chatId: int, messageType: int, messageId: int = None, userList: list = None, extensions: dict = None):
        if userList is None: userList = []

        if messageId is None: messageId = 0
        else: messageId = messageId

        data = json.dumps({
            "applyCount": 0,
            "asSummary": False,
            "createdTime": 0,
            "memberList": [],
            "messageId": messageId,
            "refId": 0,
            "roleList": [],
            "rolePlayMode": 0,
            "status": 1,
            "threadActivityType": 0,
            "threadId": 0,
            "type": messageType,
            "extensions": extensions,
            "content": message,
            "uid": 0,
            "userList": userList
        })

        response = requests.post(f"{self.api}/chat/threads/{chatId}/control-messages", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def delete_message(self, messageId: int, chatId: int):
        response = requests.delete(f"{self.api}/chat/threads/{chatId}/messages/{messageId}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def search(self, content: str, type: str, size: int = 25):
        if type == "chat":
            response = requests.get(f"{self.api}/search/chat?word={content}&size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
            else: return objects.ChatList(json.loads(response.text)["list"]).ChatList

        elif type == "blogs":
            response = requests.get(f"{self.api}/search/blogs?word={content}&size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
            else: return objects.BlogList(json.loads(response.text)["list"]).BlogList

        elif type == "circles":
            response = requests.get(f"{self.api}/search/circles?word={content}&size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
            else: return objects.CircleList(json.loads(response.text)["list"]).CircleList

        elif type == "users":
            response = requests.get(f"{self.api}/search/users?word={content}&size={size}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
            else: return objects.UserProfileList(json.loads(response.text)["list"]).UserProfileList

        else: raise exceptions.WrongType(type)

    def start_chat(self, message: str, userId: [int, list], type: str, title: str = None, tagStrList: list = None):
        if type.lower() == "private": type = 2
        elif type.lower() == "global": type = 0
        else: raise exceptions.WrongType(type)

        if isinstance(userId, int): userId = [userId]
        elif isinstance(userId, list): userId = userId
        else: raise exceptions.WrongType(self.type_(userId))

        data = json.dumps({
            "createdTime": 0,
            "hostUid": 0,
            "invitedUids": userId,
            "latestMessageId": 0,
            "tagStrList": tagStrList,
            "initialMessageContent": message,
            "status": 1,
            "threadId": 0,
            "type": type,
            "title": title,
            "uid": 0
        })

        response = requests.post(f"{self.api}/chat/threads", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def start_roleplay(self, chatId: int, mode: str, roleIds: list):
        if mode.lower() == "text": mode = 1
        elif mode.lower() == "voice": mode = 2
        else: raise exceptions.WrongType(mode)

        data = json.dumps({
            "mode": mode,
            "roleIds": roleIds
        })

        response = requests.post(f"{self.api}/chat/threads/{chatId}/start-role-play", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def end_roleplay(self, chatId: int):
        data = json.dumps({})
        response = requests.post(f"{self.api}/chat/threads/{chatId}/end-role-play", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def delete_chat(self, chatId: int):
        response = requests.delete(f"{self.api}/chat/threads/{chatId}", headers=headers.Headers(deviceId=self.device_id).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def flag(self, message: str, target: str, flagType: str, objectId: int, chatId: int = None):
        # Flag Types
        # 0 - UNKNOWN // UNKNOWN
        # 1 - Suicide or Self-Harm // SUICIDE
        # 2 - Illegal Activities // ILLEGAL
        # 3 - Violent or Graphic Content // VIOLENT
        # 4 - Pornography and Nudity // PORN
        # 5 - Hate Speech // HATE
        # 6 - Bullying or Harassment // BULLYING
        # 7 - Spam or Trolling // SPAM
        # 100 - Others // OTHERS

        extensions = None
        if target.lower() == "chat": objectType = 1
        elif target.lower() == "blog": objectType = 2
        elif target.lower() == "comment": objectType = 3
        elif target.lower() == "user": objectType = 4
        elif target.lower() == "circle": objectType = 5
        elif target.lower() == "message": objectType = 7; extensions = {"threadId": chatId}
        else: raise exceptions.WrongType(target)

        if flagType.lower() == "suicide": flagType = 1
        elif flagType.lower() == "illegal": flagType = 2
        elif flagType.lower() == "violent": flagType = 3
        elif flagType.lower() == "porn": flagType = 4
        elif flagType.lower() == "hate": flagType = 5
        elif flagType.lower() == "bullying": flagType = 6
        elif flagType.lower() == "spam": flagType = 7
        elif flagType.lower() == "other": flagType = 100
        else: raise exceptions.WrongType(flagType)

        data = json.dumps({
            "extensions": extensions,
            "flagType": flagType,
            "message": message,
            "objectId": objectId,
            "objectType": objectType
        })

        response = requests.post(f"{self.api}/flags", headers=headers.Headers(data=data, deviceId=self.device_id).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def generate_invitation_code(self, linkId: str):
        response = requests.get(f"{self.apiWeb}/invitation-code?linkId={linkId}", proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)["invitationCode"]

    def handle_socket_message(self, data):
        return self.callbacks.resolve(data)
