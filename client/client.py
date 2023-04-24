import sys
import socket
import threading
from getpass import getpass
from cryptocode import encrypt

sys.path.insert(0, "/home/andrey/Fail-Safe/common")
from enums import *


timeout = 1
disconnected = False


def sender(sock):
    try:
        while(True):
            if (disconnected):
                raise Exception("disconnected")
            message = input()
            if(not message or len(message) > 512):
                print("No message or too long (msg len must be 1-512)")
            else:
                sock.send(message.encode())
    except:
        print(f"Server: {ConnectionStatus.disconnected.value} (from enter)")


def receiver(sock):
    try:
        sock.settimeout(timeout)
        while (True):
            try:
                data = sock.recv(1024).decode()
                if (not data):
                    global disconnected
                    disconnected = True
                    print(f"Server: {ConnectionStatus.disconnected.value} (from receiver)")
                    break
                action, payload = data.split(PACKET_SEPARATOR)
                match action:
                    case Action.update_users.value:
                        nicknames = payload.split(PAYLOAD_SEPARATOR)
                        for nickname in nicknames:
                            print(f"Add user: {nickname}")
                    case Action.new_message.value:
                        print(payload)
                    case Action.all_messages.value:
                        messages = payload.split(PAYLOAD_SEPARATOR)
                        for message in messages:
                            print(message)
            except socket.timeout:
                continue
    except Exception:
        pass


def chat_phase(sock):
    thread = threading.Thread(target=sender, args=(sock,))
    thread.start()
    receiver(sock)
    thread.join()


def authorize_phase(action, nickname, password):
    packet = PACKET_SEPARATOR.join([action, nickname, encrypt(password, PASS_KEY)])
    sock = socket.socket()
    sock.settimeout(timeout)
    while(True):
        global disconnected
        disconnected = False
        try:
            host = "172.20.0.4"
            port = 8080
            sock.connect((host, port))
            sock.send(packet.encode())
            answer = sock.recv(1024).decode()
            if (answer != AuthStatus.success.value):
                sock.close()
                print(f"Server: {answer}, interrupt")
                return
        except:
            try:
                host = "172.20.0.5"
                port = 8081
                sock = socket.socket()
                sock.connect((host, port))
                sock.send(packet.encode())
                answer = sock.recv(1024).decode()
                if (answer != AuthStatus.success.value):
                    sock.close()
                    print(f"Server: {answer}, interrupt")
                    return
            except Exception as e:
                print(f"Server: {e} (from authorize)")
                return
        print(f"connect to {host}, {port}")
        chat_phase(sock)
        sock.close()
        print("reconnection...")
        packet = PACKET_SEPARATOR.join([Action.login.value, nickname, encrypt(password, PASS_KEY)])


def login_phase(action):
    is_valid = False
    while (not is_valid):
        nickname = input("Nickname: ")
        password = getpass()
        is_valid = True
        if (not nickname or len(nickname) > 16):
            is_valid = False
            print("Nickname length must be 1-16 symbols")
        if (len(password) < 8 or len(password) > 16):
            is_valid = False
            print("Password length must be 8-16 symbols")
    authorize_phase(action, nickname, password)


def start_phase():
    action = ""
    while (action.lower() != Action.login.value and action.lower() != Action.registration.value):
        action = input(f"Choose action between '{Action.login.value}' and '{Action.registration.value}': ")
    login_phase(action)
