import threading
from enums import *


class User:

    def __init__(self, pair: tuple):
        self.nickname = pair[0]
        self.sock = pair[1]


class Room:

    __MAX_COUNT_LINES = 100
    __message_list_file = "message_dump.txt"
    __count_lines = 0


    def __init__(self, max_users_count):
        self.__lock = threading.Lock()
        self.__max_users_count = max_users_count
        self.__users = list()


    def is_full(self):
        return self.__get_users_count() >= self.__max_users_count


    def add_user(self, user: User) -> bool:
        status = True
        self.__lock.acquire()
        self.__users.append(user)

        try:
            self.__send_all_online_members()
            self.__send_to_user_all_messages(user)
        except Exception as e:
            print(e)
            status = False

        self.__lock.release()
        return status


    def remove_user(self, user: User) -> bool:
        status = True
        self.__lock.acquire()
        self.__users.remove(user)

        try:
            self.__send_all_online_members()
        except Exception as e:
            print(e)
            status = False

        self.__lock.release()
        return status


    def process_traffic(self, user: User) -> bool:
        status = True
        try:
            while True:
                data = user.sock.recv(1024).decode()
                if not data:
                    break
                message = f"{user.nickname}: {data}"
                self.__add_message_to_file(message)
                self.__send_all(";".join([Action.new_message.value, message]).encode())
        except Exception as e:
            print(e)
            status = False
        return status


    def get_all_online_users_nicknames(self):
        nicknames = list()
        for user in self.__users:
            nicknames.append(user.nickname)
        return nicknames


    def __get_users_count(self):
        self.__lock.acquire()
        count = len(self.__users)
        self.__lock.release()
        return count


    def __send_all(self, data: bytes):
        self.__lock.acquire()
        for user in self.__users:
            user.sock.send(data)
        self.__lock.release()


    def __add_message_to_file(self, message: str):
        self.__lock.acquire()
        if (self.__count_lines >= self.__MAX_COUNT_LINES):
            try:
                with open(self.__message_list_file, "r+") as file:
                    messages = file.readlines()[50:]
                    file.truncate(0)
                    file.writelines(messages)
                    self.__count_lines = self.__MAX_COUNT_LINES - 50
            except Exception as e:
                print(e)

        with open(self.__message_list_file, "a+") as file:
            file.write(message + '\n')
            self.__count_lines += 1
        self.__lock.release()


    # no mutex
    def __send_all_online_members(self):
        nicknames = self.get_all_online_users_nicknames()

        if (not nicknames):
            return

        data = PAYLOAD_SEPARATOR.join(nicknames)
        data = Action.update_users.value + PACKET_SEPARATOR + data

        for user in self.__users:
            user.sock.send(data.encode())


    # no mutex
    def __send_to_user_all_messages(self, user):
        try:
            with open(self.__message_list_file, "r") as file:
                messages = file.read().split('\n')
        except:
            return

        if (not messages):
            return
        messages.pop()
        data = PAYLOAD_SEPARATOR.join(messages)
        data = Action.all_messages.value + PACKET_SEPARATOR + data
        user.sock.send(data.encode())
