from enum import Enum


class NotificationType(Enum):
    NEW_MESSAGE = "new_message"
    NEW_ROOM = "Nova mistnost"


class Language(Enum):
    CS = "czech"
    EN = "english"


TOKEN_PATH = 'creds/refreshToken.json'
PORT = 8085
