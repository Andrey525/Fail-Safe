import threading
import socket
from enums import *


class Room:
    __MAX_COUNT_LINES = 100
    __message_list_file = "message_dump.txt"
    __count_lines = 0
    def __init__(self, max_users_count):
        self.__lock = threading.Lock()
        self.__max_users_count = max_users_count
        self.__users = list()

    def is_full(self):
        return self.get_users_count() >= self.__max_users_count

    def get_users_count(self):
        self.__lock.acquire()
        count = len(self.__users)
        self.__lock.release()
        return count

    def add_user(self, pair: tuple):
        self.__lock.acquire()
        self.__users.append(pair)
        self.__lock.release()

    def remove_user(self, pair: tuple):
        self.__lock.acquire()
        self.__users.remove(pair)
        self.__lock.release()

    def add_message(self, message: str):
        self.__lock.acquire()
        if (self.__count_lines >= self.__MAX_COUNT_LINES):
            with open(self.__message_list_file, "r+") as file:
                messages = file.readlines()[50:]
                file.truncate(0)
                print(messages)
                file.writelines(messages)
                self.__count_lines = self.__MAX_COUNT_LINES - 50
        with open(self.__message_list_file, "a+") as file:
            file.write(message + '\n')
            self.__count_lines += 1
        self.__lock.release()

    def send_all(self, data: bytes):
        self.__lock.acquire()
        for user in self.__users:
            sock = user[1]
            sock.send(data)
        self.__lock.release()

    def send_to_user_all_online_members(self, user_sock):
        nicknames = list()
        self.__lock.acquire()
        for user in self.__users:
            if user_sock == user[1]:
                continue
            nickname = user[0]
            nicknames.append(nickname)
        self.__lock.release()

        if (not nicknames):
            return

        data = PAYLOAD_SEPARATOR.join(nicknames)
        data = Action.all_users.value + PACKET_SEPARATOR + data
        user_sock.send(data.encode())

    def send_to_user_all_messages(self, user_sock):
        try:
            with open(self.__message_list_file, "r") as file:
                messages = file.read().split('\n')
        except:
            return

        if (not messages):
            return
        messages.pop()
        self.__lock.acquire()
        data = PAYLOAD_SEPARATOR.join(messages)
        self.__lock.release()
        data = Action.all_messages.value + PACKET_SEPARATOR + data
        user_sock.send(data.encode())

