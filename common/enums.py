from enum import Enum


class ConnectionStatus(Enum):
    connected = "connected"
    disconnected = "disconnected"
    conn_ref = "connection refused"
    server_full = "server is full"

class Action(Enum):
    login = "login"
    registration = "registration"
    update_users = "update users"
    new_message = "new message"
    all_messages = "all messages"


class AuthStatus(Enum):
    success = "success"
    already_logged_in = "already logged in"
    nickname_busy = "nickname busy"
    no_such_user = "user doesn't exist"
    invalid_password = "invalid password"


PACKET_SEPARATOR = ";"
PAYLOAD_SEPARATOR = "|"
PASS_KEY = "baobab"
UNKNOWN_ERROR = "unknown error"
