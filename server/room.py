import threading
from enums import *
import time


class User:

    def __init__(self, pair: tuple):
        self.nickname = pair[0]
        self.sock = pair[1]


class Server:

    def __init__(self, pair: tuple):
        self.dislocation = pair[0]
        self.sock = pair[1]


class Room:

    __messages = list()


    def __init__(self, max_users_count):
        self.__lock = threading.Lock()
        self.__max_users_count = max_users_count
        self.__users = list()
        self.__servers = list()


    def is_full(self):
        return self.__get_users_count() >= self.__max_users_count


    def add_user(self, user: User) -> bool:
        status = True
        self.__lock.acquire()
        self.__users.append(user)
        self.__lock.release()
        try:
            self.__send_all_online_members()
            time.sleep(0.1) # Костыль Чтоб в сокет смешанные данные не пришли TODO
            self.__send_to_user_all_messages(user)
            time.sleep(0.1) # Костыль Чтоб в сокет смешанные данные не пришли TODO
        except Exception as e:
            print(e)
            status = False
        return status


    def add_server(self, server: Server):
        self.__lock.acquire()
        self.__servers.append(server)
        self.__lock.release()


    def remove_server(self, server: Server):
        self.__lock.acquire()
        self.__servers.remove(server)
        self.__lock.release()

    def remove_user(self, user: User) -> bool:
        status = True
        self.__lock.acquire()
        self.__users.remove(user)
        self.__lock.release()
        try:
            self.__send_all_online_members()
            time.sleep(0.1) # Костыль Чтоб в сокет смешанные данные не пришли TODO
        except Exception as e:
            print(e)
            status = False
        return status


    def process_traffic(self, user: User) -> bool:
        status = True
        try:
            while True:
                data = user.sock.recv(1024).decode()
                if not data:
                    break
                message = f"{user.nickname}: {data}"
                self.add_message_to_list(message)
                self.__send_all(";".join([Action.new_message.value, message]))
                time.sleep(0.1) # Костыль Чтоб в сокет смешанные данные не пришли TODO
        except Exception as e:
            print(e)
            status = False
        return status


    def get_all_online_users_nicknames(self):
        nicknames = list()
        for user in self.__users:
            nicknames.append(user.nickname)
        return nicknames


    def add_message_to_list(self, message: str):
        self.__lock.acquire()
        self.__messages.append(message)
        self.__lock.release()


    def __get_users_count(self):
        self.__lock.acquire()
        count = len(self.__users)
        self.__lock.release()
        return count


    def __send_all(self, data: str):
        self.__lock.acquire()
        print("!!! " + data)
        for user in self.__users:
            user.sock.send(data.encode())
        for server in self.__servers:
            server.sock.send(data.encode())
        self.__lock.release()


    def __send_all_online_members(self):
        self.__lock.acquire()
        nicknames = self.get_all_online_users_nicknames()
        self.__lock.release()
        if (not nicknames):
            return
        data = PAYLOAD_SEPARATOR.join(nicknames)
        data = Action.update_users.value + PACKET_SEPARATOR + data
        print("!! " + data)
        self.__lock.acquire()
        for user in self.__users:
            user.sock.send(data.encode())
        for server in self.__servers:
            server.sock.send(data.encode())
        self.__lock.release()


    def __send_to_user_all_messages(self, user):
        self.__lock.acquire()
        messages = self.__messages
        self.__lock.release()
        if (not messages):
            return
        data = PAYLOAD_SEPARATOR.join(messages)
        data = Action.all_messages.value + PACKET_SEPARATOR + data
        print("! " + data)
        user.sock.send(data.encode())
