import sys
import socket
import time
import threading
from cryptocode import encrypt
from tkinter import *

sys.path.insert(0, "/home/andrey/Рабочий стол/Institute/4_kurs/Fail-Safe/common")
from enums import *


stop_event = threading.Event()
timeout = 1


def stop(window):
    global stop_event
    stop_event.set()
    time.sleep(1)
    window.destroy()


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

    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        sock.send(packet.encode())
        answer = sock.recv(1024).decode()
        if (answer != AuthStatus.success.value):
            if (not answer):
                answer = UNKNOWN_ERROR
            print(f"Server: operation failed, because {answer}")
            sock.close()
            start_window(window, answer)
    except:
        print(f"Server: {ConnectionStatus.disconnected.value}")
        sock.close()
        start_window(window, ConnectionStatus.disconnected.value)
    finally:
        chat_window(window, sock)


def enter(frame, entry, sock):
    message = entry.get()
    entry.delete(0, END)
    try:
        if (message):
            sock.send(message.encode())
    except:
        print(f"Server: {ConnectionStatus.disconnected.value}")
        sock.close()
        window = frame.master
        frame.destroy()
        start_window(window, ConnectionStatus.disconnected.value)


def receiver(sock, text_boxes):
    chat_textbox = text_boxes[0]
    users_textbox = text_boxes[1]
    sock.settimeout(timeout)
    while (not stop_event.is_set()):
        try:
            data = sock.recv(1024).decode()
            if (not data ):
                print(f"Server: {UNKNOWN_ERROR}")
                break
            action, payload = data.split(PACKET_SEPARATOR)
            match action:
                case Action.update_users.value:
                    nicknames = payload.split(PAYLOAD_SEPARATOR)
                    users_textbox.configure(state=NORMAL)
                    users_textbox.delete("1.0", END)
                    for nickname in nicknames:
                        users_textbox.insert(END, nickname + '\n')
                    users_textbox.configure(state=DISABLED)
                case Action.new_message.value:
                    chat_textbox.configure(state=NORMAL)
                    chat_textbox.insert(END, payload + '\n')
                    chat_textbox.configure(state=DISABLED)
                case Action.all_messages.value:
                    messages = payload.split(PAYLOAD_SEPARATOR)
                    chat_textbox.configure(state=NORMAL)
                    for message in messages:
                        chat_textbox.insert(END, message + '\n')
                    chat_textbox.configure(state=DISABLED)
        except socket.timeout:
            continue


def chat_window(window, sock):
    frame = Frame(window)
    frame.pack()

    lbl = Label(frame, text="Chat Room", font=("Arial", 16))
    lbl.grid(row=0, column=0, pady=20)
    chat_textbox = Text(frame, width=60, font=("Arial", 16), state=DISABLED)
    chat_textbox.grid(row=1, column=0, columnspan=2, padx=5)
    entry = Entry(frame, width=50, font=("Arial", 16))
    entry.grid(row=2, column=0, pady=10)
    btn = Button(frame, text="Enter", font=("Arial", 16), command= lambda: enter(frame, entry, sock))
    btn.grid(row=2, column=1, pady=10)
    lbl_users = Label(frame, text="Online users", font=("Arial", 16))
    lbl_users.grid(row=0, column=2)
    users_textbox = Text(frame, width=20, font=("Arial", 16), state=DISABLED)
    users_textbox.grid(row=1, column=2, padx=5)

    thread = threading.Thread(target=receiver, args=(sock, [chat_textbox, users_textbox]))
    thread.start()
    
    frame.mainloop()


def login_window(old_frame, action):
    window = old_frame.master
    old_frame.destroy()
    frame= Frame(window)
    frame.pack()

    lbl_1 = Label(frame, text="Enter nickname", font=("Arial", 16))
    lbl_1.grid(row=0, pady=10)
    entry_1 = Entry(frame, font=("Arial", 16))
    entry_1.grid(row=1)
    lbl_2 = Label(frame, text="Enter password", font=("Arial", 16))
    lbl_2.grid(row=2)
    entry_2 = Entry(frame, show="*", font=("Arial", 16))
    entry_2.grid(row=3)
    btn = Button(frame, text="Confirm", font=("Arial", 16), command= lambda: authorize(frame, [action, entry_1.get(), encrypt(entry_2.get(), PASS_KEY)]))
    btn.grid(row=4)

    frame.mainloop()


def start_window(window, err: str=None):
    frame = Frame(window)
    frame.pack()

    lbl = Label(frame, text="Choose action", font=("Arial", 16))
    lbl.grid(row=0, pady=10)
    btn_1 = Button(frame, text="Login", font=("Arial", 16), command= lambda: login_window(frame, Action.login.value))
    btn_1.grid(row=1)
    btn_2 = Button(frame, text="Registration", font=("Arial", 16), command= lambda: login_window(frame, Action.registration.value))
    btn_2.grid(row=2)

    if (err):
        lbl = Label(frame, text=f"Error: {err}", font=("Arial", 16), fg='#c30010')
        lbl.grid(row=3, pady=20)

    frame.mainloop()