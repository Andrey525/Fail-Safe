import sys
from tkinter import *

sys.path.insert(0, "/home/andrey/Рабочий стол/Institute/4_kurs/Fail-Safe/common")
from enums import *
from enums import PACKET_SEPARATOR
from client import *


def main():
    window = Tk()
    window.title("Chat client")
    window.geometry('1024x768')
    start(window)
    window.mainloop()


if __name__ == '__main__':
    main()