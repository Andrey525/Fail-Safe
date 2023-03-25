import threading


class Room:
    def __init__(self, max_players_count):
        self.__lock = threading.Lock()
        self.__max_players_count = max_players_count
        self.__players = list()

    def is_full(self):
        print(self.get_players_count())
        return self.get_players_count() >= self.__max_players_count

    def get_players_count(self):
        self.__lock.acquire()
        count = len(self.__players)
        self.__lock.release()
        return count

    def add_player(self, pair: tuple):
        self.__lock.acquire()
        self.__players.append(pair)
        self.__lock.release()

    def remove_player(self, pair: tuple):
        self.__lock.acquire()
        self.__players.remove(pair)
        self.__lock.release()

