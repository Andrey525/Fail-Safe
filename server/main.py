import os
import socket
import threading
import time
import auth
import room
from enums import *


chat_room = room.Room(max_users_count=3)


def server_handler(server_bro_sock, sock_for_bro):
    server = room.Server(("Los Angeles", sock_for_bro))
    chat_room.add_server(server)
    try:
        server_bro_sock.settimeout(1)
        while (True):
            try:
                data = server_bro_sock.recv(1024).decode()
                if (not data):
                    print("server bro disconnected")
                    chat_room.remove_server(server)
                    break
                action, payload = data.split(PACKET_SEPARATOR)
                match action:
                    # case Action.update_users.value:
                    #     nicknames = payload.split(PAYLOAD_SEPARATOR)
                    #     for nickname in nicknames:
                    #         print(f"Add user: {nickname}")
                    case Action.new_message.value:
                        # print(payload)
                        chat_room.add_message_to_list(payload)
                    # case Action.all_messages.value:
                    #     messages = payload.split(PAYLOAD_SEPARATOR)
                    #     for message in messages:
                    #         print(message)
            except socket.timeout:
                continue
    except Exception:
        pass


def handler(sock):
    # Регистрация либо вход в существующий аккаунт
    online_nicknames = chat_room.get_all_online_users_nicknames()
    nickname = auth.authorize(sock, online_nicknames)
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
    chat_room.remove_user(user)
    sock.close()


def main():
    # try:
        print("Starting server")
        host = os.environ['SERVER_IP_ADDR']
        port = int(os.environ['SERVER_PORT'])
        sock = socket.socket()
        sock.bind((host, port))
        sock.listen(5)

        host_bro = os.environ['BRO_SERVER_IP_ADDR']
        port_bro = int(os.environ['BRO_SERVER_PORT'])
        sock_for_bro = socket.socket()
        sock_for_bro.connect((host_bro, port_bro))

        server_bro_sock, server_bro_address = sock.accept()
        thread = threading.Thread(target=server_handler, args=(server_bro_sock, sock_for_bro))
        thread.start()
        print("server bro connected")
        while (True):
            conn_sock, address = sock.accept()
            print("Connection from: " + str(address))
            if (not chat_room.is_full()):
                thread = threading.Thread(target=handler, args=(conn_sock,))
                thread.start()
            else:
                conn_sock.send(", ".join([ConnectionStatus.conn_ref.value, ConnectionStatus.server_full.value]).encode())
                conn_sock.close()
    # except:
    #     print("Critical error, interrupt")
    
if __name__ == '__main__':
    main()