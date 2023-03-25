import socket
import threading
import time
import auth
import room
from enums import ConnectionStatus
from db import reset_all_statuses

game_room = room.Room(max_players_count=2)


def handler(sock, address):
    # костыль: нужно добавить пустого, чтоб при переполнении заблокировать новых игроков
    game_room.add_player((None, None))
    # Регистрация либо вход в существующий аккаунт
    nickname = auth.authorize(sock)
    if (not nickname):
        game_room.remove_player((None, None))
        sock.close()
        return
    # Добавляем
    game_room.add_player((nickname, sock))
    game_room.remove_player((None, None))
    # Ждем пока не заполнится рум
    while (not game_room.is_full()):
        time.sleep(1)
    print("Room is full! Can start game!")

    # сама игра
    try:
        while True:
            data = sock.recv(1024).decode()
            if not data:
                break
            sock.send("Hi".encode())
    except:
        auth.logout(nickname)
        game_room.remove_player((nickname, sock))
        sock.close()
        print("Client was disconnected")
        return
    finally:
        auth.logout(nickname)
        game_room.remove_player((nickname, sock))
        sock.close()



def main():
    print("starting server")
    host = socket.gethostname()
    port = 8080
    sock = socket.socket()
    sock.bind((host, port))
    sock.listen(5)
    reset_all_statuses()
    while (True):
        time.sleep(1)
        if (not game_room.is_full()):
            print("here")
            conn_sock, address = sock.accept()
            conn_sock.send(ConnectionStatus.connected.value.encode())
            print("Connection from: " + str(address))
            thread = threading.Thread(target=handler, args=(conn_sock, address))
            thread.start()
    

if __name__ == '__main__':
    main()