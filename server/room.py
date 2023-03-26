import threading
import socket


class Room:
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

    def send_all(self, data: bytes):
        self.__lock.acquire()
        for user in self.__users:
            sock = user[1]
            sock.send(data)
        self.__lock.release()

