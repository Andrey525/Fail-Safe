import os
import psycopg2
from enums import DBStatus


dbname = os.environ['DB_NAME']
user = os.environ['DB_USER']
password = os.environ['DB_PASSWORD']
host = os.environ['DB_HOST']
port = os.environ['DB_PORT']


def connect():

    connection = psycopg2.connect(  dbname = dbname,
                                    user = user,
                                    password = password,
                                    host = host,
                                    port = port)
    return connection


def update_status(nickname: str, status: str):
    query = "UPDATE users " + \
            f"SET status = '{status}' " + \
            f"WHERE nickname = '{nickname}'"
    with connect() as connection:
        with connection.cursor() as curs:
            curs.execute(query)
            connection.commit()


def registrate_new_user(nickname: str, password: str):
    query = f"INSERT INTO users (nickname, password) VALUES ('{nickname}', '{password}');"
    with connect() as connection:
        with connection.cursor() as curs:
            curs.execute(query)
            connection.commit()


def login(nickname: str):
    update_status(nickname, status=DBStatus.user_online.name)


def logout(nickname: str):
    update_status(nickname, status=DBStatus.user_offline.name)


def correct_password(nickname: str, password: str) -> bool:
    query = "SELECT password " + \
            "FROM users " + \
            f"WHERE nickname = '{nickname}'"
    with connect() as connection:
        with connection.cursor() as curs:
            curs.execute(query)
            internal_password = curs.fetchone()

    return internal_password is not None and password == internal_password[0]


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

    return status is not None and status[0] == DBStatus.user_online.name


def get_all_online_users() -> str:
    query = "SELECT nickname " + \
            "FROM users " + \
            f"WHERE status = '{DBStatus.user_online.name}'"
    with connect() as connection:
        with connection.cursor() as curs:
            curs.execute(query)
            online_users = curs.fetchall()

    return " ".join(online_users)
