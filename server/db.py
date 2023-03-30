import os
import psycopg2


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


def registrate_new_user(nickname: str, password: str):
    query = f"INSERT INTO users (nickname, password) VALUES ('{nickname}', '{password}');"
    with connect() as connection:
        with connection.cursor() as curs:
            curs.execute(query)
            connection.commit()


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

