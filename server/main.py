import socket
import threading
import time
import auth
import room
from enums import *
from db import reset_all_statuses


chat_room = room.Room(max_users_count=2)


def handler(sock):
    # Регистрация либо вход в существующий аккаунт
    nickname = auth.authorize(sock)
    if (not nickname):
        sock.close()
        return
    time.sleep(0.1) # Костыль Чтоб в сокет смешанные данные не пришли TODO

    # Добавляем
    user = room.User((nickname, sock))
    chat_room.add_user(user)

    # переписка
    chat_room.process_traffic(user)

    # выход
    auth.logout(nickname)
    chat_room.remove_user(user)
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
            thread = threading.Thread(target=handler, args=(conn_sock,))
            thread.start()
        else:
            conn_sock.send(", ".join([ConnectionStatus.conn_ref.value, ConnectionStatus.server_full.value]).encode())
            conn_sock.close()

    
if __name__ == '__main__':
    main()