import json
import requests

from .socket import SocketHandler
from .lib.util import exceptions, headers, device, objects
from typing import BinaryIO
from time import time as timestamp

device = device.DeviceGenerator()

class Client:
    def __init__(self, proxies = None, socket_trace = False):
        self.api = "https://api.projz.com/v1"
        self.authenticated = False
        self.configured = False
        self.user_agent = device.user_agent
        self.device_id = device.device_id
        self.socket = SocketHandler(self, socket_trace=socket_trace)
        self.proxies = proxies

        self.json = None
        self.sid = None
        self.userId = None
        self.account = None
        self.profile = None

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

        response = requests.post(f"{self.api}/auth/login", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))

        else:
            self.authenticated = True
            self.json = json.loads(response.text)
            self.sid = self.json["sId"]
            self.userId = self.json["userProfile"]["uid"]
            self.account = objects.UserProfile(self.json["account"]).UserProfile
            self.profile = objects.UserProfile(self.json["userProfile"]).UserProfile
            headers.sid = self.sid
            self.socket.start()
            return response.status_code

    def logout(self):
        if self.authenticated is False: raise exceptions.NotLoggedIn()
        data = json.dumps({})
        response = requests.post(f"{self.api}/auth/logout", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))

        else:
            self.authenticated, self.json, self.sid, self.userId, self.account, self.profile, headers.sid = False, None, None, None, None, None, None
            self.socket.close()
            return response.status_code

    def register(self, email: str, nickname: str, password: str, school: str, invitationCode: str, securityCode: str):
        data = json.dumps({
            "authType": 1,
            "birthday": "2000-01-01",
            "email": email,
            "gender": 1,
            "invitationCode": invitationCode,
            "nickname": nickname,
            "password": password,
            "phoneNumber": "",
            "purpose": 1,
            "school": school,
            "secret": "",
            "securityCode": securityCode
        })

        response = requests.post(f"{self.api}/auth/register", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
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

        response = requests.post(f"{self.api}/auth/check-invitation-code", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_account_info(self):
        response = requests.get(f"{self.api}/auth/account", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def get_alerts_info(self):
        response = requests.get(f"{self.api}/alerts/check", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.AlertsInfo(json.loads(response.text)).AlertsInfo

    def get_alerts(self, type: str, size: int = 25):
        if type.lower() == "activity": response = requests.get(f"{self.api}/alerts?groupId=1&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        elif type.lower() == "likes": response = requests.get(f"{self.api}/alerts?groupId=2&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        elif type.lower() == "followers": response = requests.get(f"{self.api}/alerts?groupId=3&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        else: raise exceptions.WrongType()

        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.AlertsList(json.loads(response.text)["list"]).AlertsList

    # Todo : Figure out what data is returned
    def get_blocked_users(self):
        response = requests.get(f"{self.api}/users/block-uids", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)["blockedByMeList"]

    # Todo : Figure out what data is returned
    def get_blocker_users(self):
        response = requests.get(f"{self.api}/users/block-uids", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)["blockMeList"]

    def get_content_regions(self):
        response = requests.get(f"{self.api}/configs/content-regions", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.ContentRegionList(json.loads(response.text)["list"]).ContentRegionList

    def get_invitation_code_info(self):
        response = requests.get(f"{self.api}/users/invitation-code-info", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def get_user_info(self, userId: str):
        response = requests.get(f"{self.api}/users/profile/{userId}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfile(json.loads(response.text)).UserProfile

    def get_user_following(self, userId: str, size: int = 25):
        response = requests.get(f"{self.api}/users/membership/{userId}?type=following&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["list"]).UserProfileList

    def get_user_followers(self, userId: str, size: int = 25):
        response = requests.get(f"{self.api}/users/membership/{userId}?type=follower&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["list"]).UserProfileList

    def get_all_users(self, size: int = 25):
        response = requests.get(f"{self.api}/search/users?size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["list"]).UserProfileList

    def get_namecards(self, gender: str, size: int = 25):
        if gender.lower() == "all": response = requests.get(f"{self.api}/users/namecards?gender=0&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        elif gender.lower() == "male": response = requests.get(f"{self.api}/users/namecards?gender=1&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        elif gender.lower() == "female": response = requests.get(f"{self.api}/users/namecards?gender=2&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        elif gender.lower() == "other": response = requests.get(f"{self.api}/users/namecards?gender=100&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        else: raise exceptions.WrongType

        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["list"]).UserProfileList

    def get_blog_info(self, blogId: str):
        response = requests.get(f"{self.api}/blogs/{blogId}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.Blog(json.loads(response.text)).Blog

    def get_blogs(self, type: str, size: int = 25):
        if type.lower() == "latest": response = requests.get(f"{self.api}/blogs?type=latest&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        elif type.lower() == "following": response = requests.get(f"{self.api}/blogs?type=following&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        else: raise exceptions.WrongType()

        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetBlogs(json.loads(response.text)).GetBlogs

    def get_blog_comments(self, blogId: str, size: int = 25):
        response = requests.get(f"{self.api}/comments?{blogId}&replyId=0&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.CommentList(json.loads(response.text)["list"]).CommentList

    def get_blog_likes(self, blogId: str, size: int = 25):
        response = requests.get(f"{self.api}/votes?objectId={blogId}&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.CommentList(json.loads(response.text)["list"]).CommentList

    def like_blog(self, circleId: str = "0", blogId: str = None, commentId: str = None):
        if blogId is not None: objId, objType = blogId, 2
        elif commentId is not None: objId, objType = commentId, 3
        else: raise exceptions.SpecifyType

        data = json.dumps({
            "circleId": int(circleId),
            "objectId": int(objId),
            "objectType": objType
        })

        response = requests.post(f"{self.api}/votes", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_user_blogs(self, userId: str, size: int = 25):
        response = requests.get(f"{self.api}/blogs?type=user&targetUid={userId}&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetBlogs(json.loads(response.text)).GetBlogs

    def follow(self, userId: str):
        data = json.dumps({})
        response = requests.post(f"{self.api}/users/membership/{userId}", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def unfollow(self, userId: str):
        data = json.dumps({})
        response = requests.delete(f"{self.api}/users/membership/{userId}", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def block(self, userId: str):
        data = json.dumps({})
        response = requests.post(f"{self.api}/users/block/{userId}", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def unblock(self, userId: str):
        data = json.dumps({})
        response = requests.delete(f"{self.api}/users/block/{userId}", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def edit_profile(self, nickname: str = None, bio: str = None, background: BinaryIO = None, gender: str = None, school: str = None, showsSchool: bool = None, showsJoinedCircles: bool = None, showsLocation: bool = None, chatInvitationStatus: str = None):
        if gender.lower() is not None and "male": gender = 1
        elif gender.lower() is not None and "female": gender = 2
        elif gender.lower() is not None and "other": gender = 100
        else: raise exceptions.WrongType

        if background is not None: self.upload_media(file=background, fileType="image", target=2)

        if showsSchool is not None and True: showsSchool = "1"
        elif showsSchool is not None and False: showsSchool = "2"
        else: raise exceptions.WrongType

        if showsJoinedCircles is not None and True: showsJoinedCircles = "1"
        elif showsJoinedCircles is not None and False: showsJoinedCircles = "2"
        else: raise exceptions.WrongType

        if showsLocation is not None and True: showsLocation = "1"
        elif showsLocation is not None and False: showsLocation = "2"
        else: raise exceptions.WrongType

        if chatInvitationStatus.lower() is not None and "everyone" or "all": chatInvitationStatus = 1
        elif chatInvitationStatus.lower() is not None and "following": chatInvitationStatus = 2
        elif chatInvitationStatus.lower() is not None and "friends": chatInvitationStatus = 3
        elif chatInvitationStatus.lower() is not None and "off" or "nobody": chatInvitationStatus = 4
        else: raise exceptions.WrongType

        data = json.dumps({
            "nickname": nickname,
            "bio": bio,
            "background": background,
            "gender": gender,
            "school": school,
            "showsSchool": showsSchool,
            "showsJoinedCircles": showsJoinedCircles,
            "showsLocation": showsLocation,
            "chatInvitationStatus": chatInvitationStatus
        })

        response = requests.post(f"{self.api}/users/profile/{self.userId}/update-profile", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def edit_chat(self, chatId: str, title: str = None, content: str = None, pinChat: bool = None, doNotDisturb: bool = None, allowMembersInvite: bool = None):
        data, responses = {}, []

        if title is not None: data["title"] = title
        if content is not None: data["content"] = content

        data = json.dumps(data)

        if pinChat is not None:
            if pinChat is True: response = requests.post(f"{self.api}/chat/threads/{chatId}/pin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
            elif pinChat is False: response = requests.post(f"{self.api}/chat/threads/{chatId}/unpin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
            else: raise exceptions.WrongType

            if response.status_code != 200: responses.append(exceptions.CheckException(json.loads(response.text)))
            else: responses.append(response.status_code)

        if doNotDisturb is not None:
            if doNotDisturb is True: response = requests.post(f"{self.api}/chat/threads/{chatId}/alert-option/2", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
            elif doNotDisturb is False: response = requests.post(f"{self.api}/chat/threads/{chatId}/alert-option/1", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
            else: raise exceptions.WrongType

            if response.status_code != 200: responses.append(exceptions.CheckException(json.loads(response.text)))
            else: responses.append(response.status_code)

        if allowMembersInvite is not None:
            if allowMembersInvite is True: response = requests.post(f"{self.api}/chat/threads/{chatId}/members-invite/enable", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
            elif allowMembersInvite is False: response = requests.post(f"{self.api}/chat/threads/{chatId}/members-invite/disable", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
            else: raise exceptions.WrongType

            if response.status_code != 200: responses.append(exceptions.CheckException(json.loads(response.text)))
            else: responses.append(response.status_code)

        response = requests.post(f"{self.api}/chat/threads/{chatId}", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: responses.append(exceptions.CheckException(json.loads(response.text)))
        else: responses.append(response.status_code)

        return responses

    def get_chat_threads(self, type: str = "joined", size: int = 25):
        if type.lower() == "joined": response = requests.get(f"{self.api}/chat/joined-threads?start=0&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        elif type.lower() == "recommend": response = requests.get(f"{self.api}/chat/threads?type=recommend&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        else: raise exceptions.WrongType

        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetChats(json.loads(response.text)).GetChats

    def get_chat_messages(self, chatId: str, size: int = 25):
        response = requests.get(f"{self.api}/chat/threads/{chatId}/messages?size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.MessageList(json.loads(response.text)["list"]).MessageList

    def get_chat_online_users(self, chatId: str, size: int = 25):
        response = requests.get(f"{self.api}/chat/threads/{chatId}/online-members?size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["list"]).UserProfileList

    def get_chat_users(self, chatId: str, size: int = 25):
        response = requests.get(f"{self.api}/chat/threads/{chatId}/members?size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["list"]).UserProfileList

    def apply_for_role(self, chatId: str, roleId: str):
        data = json.dumps({})
        response = requests.post(f"{self.api}/chat/threads/{chatId}/roles/{roleId}/apply", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def join_chat(self, chatId: str):
        data = json.dumps({})
        response = requests.post(f"{self.api}/chat/threads/{chatId}/members", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def leave_chat(self, chatId: str):
        response = requests.delete(f"{self.api}/chat/threads/{chatId}/members", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_circle_info(self, circleId: str):
        response = requests.get(f"{self.api}/circles/{circleId}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.Circle(json.loads(response.text)).Circle

    def get_circles(self, type: str, size: int = 25):
        if type.lower() == "joined": response = requests.get(f"{self.api}/circles?type=joined&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        elif type.lower() == "latest": response = requests.get(f"{self.api}/circles?type=latest&size={size}", headers=headers.Headers().headers, proxies=self.proxies)
        else: raise exceptions.WrongType()

        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.CircleList(json.loads(response.text)["list"]).CircleList

    def join_circle(self, circleId: str):
        data = json.dumps({})
        response = requests.post(f"{self.api}/circles/{circleId}/members", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def leave_circle(self, circleId: str):
        response = requests.delete(f"{self.api}/circles/{circleId}/members", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_tag_info(self, tagId: str):
        response = requests.get(f"{self.api}/tags?tagId={tagId}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.Tag(json.loads(response.text)).Tag

    def comment(self, message: str, blogId: str = None, replyTo: str = None):
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
        response = requests.post(f"{self.api}/comments", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def delete_comment(self, commentId: str):
        response = requests.delete(f"{self.api}/comments/{commentId}", headers=headers.Headers().headers, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def share(self, userId: str = None, chatId: str = None, circleId: str = None):
        if userId is not None: objId, objType, objPath = 0, 0, f"user/{userId}"
        elif chatId is not None: objId, objType, objPath = 0, 0, f"chat/{chatId}"
        elif circleId is not None: objId, objType, objPath = 0, 0, f"circle/{circleId}"
        else: raise exceptions.SpecifyType()

        data = json.dumps({
            "objectId": objId,
            "objectType": objType,
            "path": objPath
        })

        response = requests.post(f"{self.api}/links/share", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.Share(json.loads(response.text)).Share

    def upload_media(self, file: BinaryIO, fileType: str, target: int):
        data = file.read()
        file_head = file.read(16)

        if "png" in str(file_head).lower(): fileExt = "png"
        elif "jpg" or "jfif" in str(file_head).lower(): fileExt = "jpg"
        elif "jpeg" in str(file_head).lower(): fileExt = "jpeg"
        elif "gif" in str(file_head).lower(): fileExt = "gif"
        else: raise exceptions.InvalidFileExtension(file_head)

        response = requests.post(f"{self.api}/media/upload?target={target}", headers=headers.Headers(type=f"{fileType}/{fileExt}", data=data).headers, data=data, proxies=self.proxies)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def send_message(self, message: str, chatId: str):
        if self.authenticated is False: raise exceptions.NotLoggedIn

        request = self.socket.send(json.dumps({
                "t": 1,
                "threadId": int(chatId),
                "msg": {
                    "type": 1,
                    "status": 1,
                    "threadId": int(chatId),
                    "uid": self.userId,
                    "refId": int(timestamp() * 1000),
                    "content": message,
                    "messageId": 0
                }}))

        return request