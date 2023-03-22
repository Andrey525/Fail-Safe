import os
import time
import socket
import threading
import psycopg2


dbname = os.environ['DB_NAME']
user = os.environ['DB_USER']
password = os.environ['DB_PASSWORD']
host = os.environ['DB_HOST']
port = os.environ['DB_PORT']

lock = threading.Lock()


def connect():
    try:
        connection = psycopg2.connect(  dbname = dbname,
                                        user = user,
                                        password = password,
                                        host = host,
                                        port = port)
    except:
        print("No connection")
        exit()
    return connection


def update_status(nickname: str, status: str) -> bool:
    query = "UPDATE users " + \
            f"SET status = '{status}' " + \
            f"WHERE nickname = '{nickname}'"
    with connect() as connection:
        with connection.cursor() as curs:
            curs.execute(query)
            connection.commit()
    return True


def registrate_new_user(nickname: str, password: str) -> bool:
    query = f"INSERT INTO users (nickname, password) VALUES ('{nickname}', '{password}');"
    with connect() as connection:
        with connection.cursor() as curs:
            curs.execute(query)
            connection.commit()
    return update_status(nickname, status="busy")


def login(nickname: str, password: str) -> bool:
    query = "SELECT password " + \
            "FROM users " + \
            f"WHERE nickname = '{nickname}'"
    with connect() as connection:
        with connection.cursor() as curs:
            curs.execute(query)
            internal_password = curs.fetchone()

    if (internal_password is None or password != internal_password[0]):
        return False

    return update_status(nickname, status="busy")


def user_exist(nickname: str) -> bool:
    query = "SELECT nickname " + \
            "FROM users " + \
            f"WHERE nickname = '{nickname}'"
    with connect() as connection:
        with connection.cursor() as curs:
            curs.execute(query)
            item = curs.fetchone()
    return item is not None


def user_is_already_playing(nickname: str) -> bool:
    query = "SELECT status " + \
            "FROM users " + \
            f"WHERE nickname = '{nickname}'"
    with connect() as connection:
        with connection.cursor() as curs:
            curs.execute(query)
            status = curs.fetchone()
    if (status is None):
        return False
    return status[0] == "busy"


def handler(sock, address):
    # Регистрация либо вход в существующий аккаунт
    try:
        action = sock.recv(1024).decode()

        if (action != "login" and action != "registration"):
            sock.send("bad action".encode())
            sock.close()
            return
        sock.send("success".encode())

        nickname = sock.recv(1024).decode()
        if (user_is_already_playing(nickname)):
            sock.send("user is already playing".encode())
            sock.close()
            return
        sock.send("success".encode())

        if (action == "login"):
            if (user_exist(nickname)):
                password = sock.recv(1024).decode()
                if (not login(nickname, password)):
                    sock.send("invalid password".encode())
                    sock.close()
                    return  
            else:
                sock.send("user does not exist".encode())
                sock.close()
                return
        elif (action == "registration"):
            if (not user_exist(nickname)):
                password = sock.recv(1024).decode()
                registrate_new_user(nickname, password)
            else:
                sock.send("user exists".encode())
                sock.close()
                return
        sock.send("success".encode())

    except:
        update_status(nickname, status="free")
        sock.close()
        print("Exception")
        return

    # Определяться в какой рум закидывать игрока
    # 

    # сама игра
    try:
        while True:
            data = sock.recv(1024).decode()
            if not data:
                break
            sock.send("Hi".encode())
    except:
        update_status(nickname, status="free")
        sock.close()
        print("Exception")
        return

    update_status(nickname, status="free")
    sock.close()
    return


def main():
    print("starting server")
    host = socket.gethostname()
    port = 8080
    sock = socket.socket()
    sock.bind((host, port))
    sock.listen(5)
    while (True):
        conn_sock, address = sock.accept()
        print("Connection from: " + str(address))
        thread = threading.Thread(target=handler, args=(conn_sock, address))
        thread.start()
    

if __name__ == '__main__':
    main()