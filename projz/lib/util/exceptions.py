class InvalidHeader(Exception):
    """
    - **API Code** : 1000
    - **API Message** : Invalid header
    - **Debug Message** : ``Unknown``
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidRequest(Exception):
    """
    - **API Code** : 1001
    - **API Message** : Bad request. Error code-1001
    - **Debug Message** : invalid check request body invalid character '}' looking for beginning of object key string
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidSession(Exception):
    """
    - **API Code** : 2004
    - **API Message** : Bad request. Error code-2004
    - **Debug Message** : Invalid session
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidPassword(Exception):
    """
    - **API Code** : 2006
    - **API Message** : Password must contain 6 characters or more with no spaces.
    - **Debug Message** : Password must be more than 5 characters and cannot contain space
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class EmailNotRegistered(Exception):
    """
    - **API Code** : 2009
    - **API Message** : The email has not been registered
    - **Debug Message** : Email not existed: example@example.ex
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidEmail(Exception):
    """
    - **API Code** : 2022
    - **API Message** : The email format is invalid.
    - **Debug Message** : Email Format Error!
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidInvitationCode(Exception):
    """
    - **API Code** : 3301
    - **API Message** : The invitation code does not exist.
    - **Debug Message** : Invitation code not existed
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidNickname(Exception):
    """
    - **API Code** : 3005
    - **API Message** : This nickname is invalid, please try another one.
    - **Debug Message** : Nickyname length is not legal
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidTag(Exception):
    """
    - **API Code** : 5001
    - **API Message** : The tag is invalid, please try another one.
    - **Debug Message** : Tag length exceed the max limitation
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class TagLimitReached(Exception):
    """
    - **API Code** : 5002
    - **API Message** : The tag count is exceed the max limitation.
    - **Debug Message** : User tag count exceed max limitation
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class ChatDoesntExist(Exception):
    """
    - **API Code** : 6001
    - **API Message** : The chat does not exist.
    - **Debug Message** : thread not found
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class SpecifyType(Exception):
    """
    Raised when you need to specify the output of the command.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class WrongType(Exception):
    """
    Raised when you attribute the function the wrong type.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class NotLoggedIn(Exception):
    """
    Raised when you try to make a command but you aren't logged in.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class LibraryUpdateAvailable(Exception):
    """
    Raised when a new library update is available.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)


def CheckException(data):
    api_code = data["apiCode"]

    if api_code == 1000: raise InvalidHeader(data)
    elif api_code == 1001: raise InvalidRequest(data)
    elif api_code == 2004: raise InvalidSession(data)
    elif api_code == 2006: raise InvalidPassword(data)
    elif api_code == 2009: raise EmailNotRegistered(data)
    elif api_code == 2022: raise InvalidEmail(data)
    elif api_code == 3005: raise InvalidNickname(data)
    elif api_code == 3301: raise InvalidInvitationCode(data)
    elif api_code == 5001: raise InvalidTag(data)
    elif api_code == 5002: raise TagLimitReached(data)
    elif api_code == 6001: raise ChatDoesntExist(data)
    else: return data