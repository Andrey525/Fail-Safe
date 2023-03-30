import socket
import db
from cryptocode import decrypt
from enums import *


def authorize(sock: socket, online_nicknames: list) -> str | None:
    try:
        packet = sock.recv(1024).decode()
        if (not packet):
            raise Exception("Connection is broken")

        entity = packet.split(PACKET_SEPARATOR)
        action = entity[0]
        nickname = entity[1]
        password = decrypt(entity[2], PASS_KEY)

        if (not action or not nickname or not password):
            raise Exception("Broken package")

        if (nickname in online_nicknames):
            sock.send(AuthStatus.already_logged_in.value.encode())
            sock.close()
            return None

        if (action == Action.login.value):
            if (db.user_exist(nickname)):
                if (not db.correct_password(nickname, password)):
                    sock.send(AuthStatus.invalid_password.value.encode())
                    sock.close()
                    return None 
            else:
                sock.send(AuthStatus.no_such_user.value.encode())
                sock.close()
                return None
        elif (action == Action.registration.value):
            if (not db.user_exist(nickname)):
                db.registrate_new_user(nickname, password)
            else:
                sock.send(AuthStatus.nickname_busy.value.encode())
                sock.close()
                return None

        sock.send(AuthStatus.success.value.encode())

    except Exception as e:
        sock.close()
        print(e)
        return None

    return nickname
