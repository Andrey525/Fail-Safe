import sys
import socket

sys.path.insert(0, "/home/andrey/Рабочий стол/Institute/4_kurs/Fail-Safe/common")
from enums import Action
from enums import AuthStatus
from enums import ConnectionStatus
from enums import PACKET_SEPARATOR


def main():
    action = ""
    while (not action or not action in [act.value for act in Action]):
        for act in Action:
            print(f"For {act.name} enter '{act.value}';")
        action = input(f"Enter command: ")

    nickname = ""
    while (not nickname or nickname.find(PACKET_SEPARATOR) != -1):
        nickname = input(f"Enter nickname for {action}: ")
    
    password = ""
    while (not password or password.find(PACKET_SEPARATOR) != -1):
        password = input(f"Enter password for {nickname}: ")

    packet = ";".join([action, nickname, password])

    host = socket.gethostname()
    port = 8080
    sock = socket.socket()

    try:
        sock.settimeout(5)
        sock.connect((host, port))
        sock.send(packet.encode())
        answer = sock.recv(1024).decode()
        if (answer != "success"):
            print(f"Server: operation failed, because {answer}")
            sock.close()
            return

        sock.settimeout(None)
        message = input(f"You({nickname}): ")
        while message.lower().strip() != 'exit':
            sock.send(message.encode())
            data = sock.recv(1024).decode()
            print(data)
            message = input(f"You({nickname}): ")
        sock.close()
    except:
        print(f"Server: {ConnectionStatus.disconnected.value}")
        sock.close()
        return


if __name__ == '__main__':
    main()