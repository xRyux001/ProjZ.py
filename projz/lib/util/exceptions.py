class InvalidHeader(Exception):
    """
    - **API Code** : 1000
    - **API Message** : Invalid header
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidRequest(Exception):
    """
    - **API Code** : 1001
    - **API Message** : Bad request. Error code-1001
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class BLOG_NOT_FOUND(Exception):
    """
    - **API Code** : 1202
    - **API Message** : ``Unknown``
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidSession(Exception):
    """
    - **API Code** : 2004
    - **API Message** : Bad request. Error code-2004
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class PasswordTooShort(Exception):
    """
    - **API Code** : 2006
    - **API Message** : Password must contain 6 characters or more with no spaces.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class EmailNotRegistered(Exception):
    """
    - **API Code** : 2009
    - **API Message** : The email has not been registered
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidPassword(Exception):
    """
    - **API Code** : 2010
    - **API Message** : Password is incorrect. Forgot your password? Trying resetting it.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class PHONE_NUMBER_ALREADY_REGISTERED(Exception):
    """
    - **API Code** : 2014
    - **API Message** : ``Unknown``
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class PHONE_NUMBER_NOT_EXIST(Exception):
    """
    - **API Code** : 2016
    - **API Message** : ``Unknown``
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidEmail(Exception):
    """
    - **API Code** : 2022
    - **API Message** : The email format is invalid.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class ZIDAlreadyChanged(Exception):
    """
    - **API Code** : 2028
    - **API Message** : Z-ID cannot be modified.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class USER_NOT_FOUND(Exception):
    """
    - **API Code** : 2034
    - **API Message** : ``Unknown``
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class EMAIL_ALREADY_REGISTERED(Exception):
    """
    - **API Code** : 2038
    - **API Message** : ``Unknown``
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidInvitationCode(Exception):
    """
    - **API Code** : 3301
    - **API Message** : The invitation code does not exist.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidNickname(Exception):
    """
    - **API Code** : 3005
    - **API Message** : This nickname is invalid, please try another one.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class CIRCLE_NOT_FOUND(Exception):
    """
    - **API Code** : 4008
    - **API Message** : ``Unknown``
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class InvalidTag(Exception):
    """
    - **API Code** : 5001
    - **API Message** : The tag is invalid, please try another one.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class TagLimitReached(Exception):
    """
    - **API Code** : 5002
    - **API Message** : The tag count is exceed the max limitation.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class ChatDoesntExistOrNotFound(Exception):
    """
    - **API Code** : 6001
    - **API Message** : The chat does not exist.
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class ROLE_NOT_FOUND(Exception):
    """
    - **API Code** : 6003
    - **API Message** : ``Unknown``
    """
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class BadRequest(Exception):
    """
    - **API Code** : 9001
    - **API Message** : Bad request. Error code-9001
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

class InvalidFileExtension(Exception):
    """
    Raised when you try to upload a picture but the file type is unknown.
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
    elif api_code == 1202: raise BLOG_NOT_FOUND(data)
    elif api_code == 2004: raise InvalidSession(data)
    elif api_code == 2006: raise PasswordTooShort(data)
    elif api_code == 2009: raise EmailNotRegistered(data)
    elif api_code == 2010: raise InvalidPassword(data)
    elif api_code == 2014: raise PHONE_NUMBER_ALREADY_REGISTERED(data)
    elif api_code == 2016: raise PHONE_NUMBER_NOT_EXIST(data)
    elif api_code == 2022: raise InvalidEmail(data)
    elif api_code == 2028: raise ZIDAlreadyChanged(data)
    elif api_code == 2034: raise USER_NOT_FOUND(data)
    elif api_code == 2038: raise EMAIL_ALREADY_REGISTERED(data)
    elif api_code == 3005: raise InvalidNickname(data)
    elif api_code == 3301: raise InvalidInvitationCode(data)
    elif api_code == 4008: raise CIRCLE_NOT_FOUND(data)
    elif api_code == 5001: raise InvalidTag(data)
    elif api_code == 5002: raise TagLimitReached(data)
    elif api_code == 6001: raise ChatDoesntExistOrNotFound(data)
    elif api_code == 6003: raise ROLE_NOT_FOUND(data)
    elif api_code == 9001: raise BadRequest(data)
    else: return data