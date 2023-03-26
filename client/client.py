import sys
import socket
import threading
from tkinter import *

sys.path.insert(0, "/home/andrey/Рабочий стол/Institute/4_kurs/Fail-Safe/common")
from enums import *


def clear_frame(frame):
    for widget in frame.winfo_children():
       widget.destroy()


def authorize(frame, data: tuple):
    host = socket.gethostname()
    port = 8080
    sock = socket.socket()

    window = frame.master
    frame.destroy()

    packet = PACKET_SEPARATOR.join(data)

    sock.settimeout(5)
    try:
        sock.connect((host, port))
        sock.send(packet.encode())
        answer = sock.recv(1024).decode()
        if (answer != AuthStatus.success.value):
            print(f"Server: operation failed, because {answer}")
            sock.close()
            start(window)
    except:
        print(f"Server: {ConnectionStatus.disconnected.value}")
        sock.close()
        start(window)
    finally:
        sock.settimeout(None)
        chat_window(window, sock)


def enter(frame, entry, sock):
    message = entry.get() + '\n'
    entry.delete(0, END)
    try:
        sock.send(message.encode())
    except:
        print(f"Server: {ConnectionStatus.disconnected.value}")
        sock.close()
        window = frame.master
        frame.destroy()
        start(window)


def receiver(sock, txt):
    while (True):
        data = sock.recv(1024).decode()
        txt.insert(END, data)


def chat_window(window, sock):
    frame = Frame(window)
    frame.pack()
    lbl = Label(frame, text="Chat Room")
    lbl.grid(row=0)
    entry = Entry(frame)
    entry.grid(row=1)
    btn = Button(frame, text="Enter", command= lambda: enter(frame, entry, sock))
    btn.grid(row=2)
    txt = Text(frame)
    txt.grid(row=3)

    thread = threading.Thread(target=receiver, args=(sock, txt))
    thread.start()
    
    frame.mainloop()


def login_window(frame, action):
    clear_frame(frame)
    lbl_1 = Label(frame, text="Enter nickname")
    lbl_1.grid(row=0)
    entry_1 = Entry(frame)
    entry_1.grid(row=1)
    lbl_2 = Label(frame, text="Enter password")
    lbl_2.grid(row=2)
    entry_2 = Entry(frame)
    entry_2.grid(row=3)
    btn = Button(frame, text="Confirm", command= lambda: authorize(frame, [action, entry_1.get(), entry_2.get()]))
    btn.grid(row=4)


def start(window):
    frame = Frame(window)
    frame.pack()
    lbl = Label(frame, text="Choose action")
    lbl.grid(row=0)

    btn_1 = Button(frame, text="Login", command= lambda: login_window(frame, "login"))
    btn_1.grid(row=1)

    btn_2 = Button(frame, text="Registration", command= lambda: login_window(frame, "registration"))
    btn_2.grid(row=2)
    frame.mainloop()