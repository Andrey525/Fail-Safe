import db
from enums import Action
from enums import AuthStatus


def authorize(sock) -> str | None:
    try:
        action = sock.recv(1024).decode()
        if (not action):
            raise Exception("Connection is broken")

        nickname = sock.recv(1024).decode()
        if (not nickname):
            raise Exception("Connection is broken")

        if (db.user_is_already_playing(nickname)):
            sock.send(AuthStatus.already_logged_in.value.encode())
            sock.close()
            return None

        if (action == Action.login.value):
            if (db.user_exist(nickname)):
                sock.send(AuthStatus.nickname_busy.value.encode())
                password = sock.recv(1024).decode()
                if (not password):
                    raise Exception("Connection is broken")
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
                sock.send(AuthStatus.no_such_user.value.encode())
                password = sock.recv(1024).decode()
                if (not password):
                    raise Exception("Connection is broken")
                db.registrate_new_user(nickname, password)
            else:
                sock.send(AuthStatus.nickname_busy.value.encode())
                sock.close()
                return None
    except Exception as e:
        sock.close()
        print(e)
        return None

    try:
        db.login(nickname)
        sock.send(AuthStatus.success.value.encode())
    except Exception as e:
        db.logout(nickname)
        sock.close()
        print(e)
        return None

    return nickname
    

def logout(nickname: str):
    db.logout(nickname)