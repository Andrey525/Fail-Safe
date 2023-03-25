from enum import Enum


class ConnectionStatus(Enum):
    connected = "connected"
    disconnected = "disconnected"
    conn_ref = "connection refused"

class Action(Enum):
    login = "login"
    registration = "registration"


class AuthStatus(Enum):
    success = "success"
    already_logged_in = "already logged in"
    nickname_busy = "nickname busy"
    no_such_user = "user doesn't exist"
    invalid_password = "invalid password"


class DBStatus(Enum):
    user_offline = "user offline"
    user_online = "user online"
