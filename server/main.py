import socket
import threading
import time
import auth
import room
from enums import ConnectionStatus
from db import reset_all_statuses


chat_room = room.Room(max_users_count=2)


def chat(nickname: str, sock: socket):
    while True:
        data = sock.recv(1024).decode()
        if not data:
            break
        chat_room.send_all(f"{nickname}: {data}".encode())


def handler(sock, address):
    # Регистрация либо вход в существующий аккаунт
    nickname = auth.authorize(sock)
    if (not nickname):
        sock.close()
        return

    # Добавляем
    chat_room.add_user((nickname, sock))

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