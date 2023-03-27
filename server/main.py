import socket
import threading
import time
import auth
import room
from enums import *
from db import reset_all_statuses


chat_room = room.Room(max_users_count=2)


def chat(nickname: str, sock: socket):
    while True:
        data = sock.recv(1024).decode()
        if not data:
            break
        message = f"{nickname}: {data}"
        chat_room.add_message(message)
        chat_room.send_all(";".join([Action.new_message.value, message]).encode())


def handler(sock, address):
    # Регистрация либо вход в существующий аккаунт
    nickname = auth.authorize(sock)
    if (not nickname):
        sock.close()
        return

    # Добавляем
    chat_room.add_user((nickname, sock))
    time.sleep(0.1) # Костыль Чтоб в сокет смешанные данные не пришли TODO
    # Отправляем новому пользователю список онлайн пользователей
    chat_room.send_to_user_all_online_members(sock)
    time.sleep(0.1) # Костыль Чтоб в сокет смешанные данные не пришли TODO
    # Отправляем всем ник нового пользователя (включая самого пользователя)
    chat_room.send_all(PACKET_SEPARATOR.join([Action.new_user.value, nickname]).encode())
    time.sleep(0.1) # Костыль Чтоб в сокет смешанные данные не пришли TODO
    # Отправляем новому пользователю список сообщений
    chat_room.send_to_user_all_messages(sock)
    time.sleep(0.1) # Костыль Чтоб в сокет смешанные данные не пришли TODO

    # переписка
    chat(nickname, sock)

    # выход
    auth.logout(nickname)
    chat_room.remove_user((nickname, sock))
    sock.close()


def main():
    print("Starting server")
    host = socket.gethostname()
    port = 8080
    sock = socket.socket()
    sock.bind((host, port))
    sock.listen(5)
    reset_all_statuses()
    while (True):
        conn_sock, address = sock.accept()
        print("Connection from: " + str(address))
        if (not chat_room.is_full()):
            thread = threading.Thread(target=handler, args=(conn_sock, address))
            thread.start()
        else:
            conn_sock.send(", ".join([ConnectionStatus.conn_ref.value, ConnectionStatus.server_full.value]).encode())
            conn_sock.close()

    
if __name__ == '__main__':
    main()