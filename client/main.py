import sys
import socket

sys.path.insert(0, "/home/andrey/Рабочий стол/Institute/4_kurs/Fail-Safe/common")
from enums import Action
from enums import AuthStatus
from enums import ConnectionStatus


def main():
    host = socket.gethostname()
    port = 8080
    sock = socket.socket()

    sock.settimeout(5)
    try:
        sock.connect((host, port))
        # confirm connection
        status = sock.recv(1024).decode()
        if (not status or status != ConnectionStatus.connected.value):
            raise Exception()
    except:
        print(f"Server: {ConnectionStatus.conn_ref.value}")
        sock.close()
        return

    try:
        action = ""
        while (not action or not action in [act.value for act in Action]):
            for act in Action:
                print(f"For {act.name} enter '{act.value}';")
            action = input(f"Enter command: ")
        sock.send(action.encode())

        nickname = ""
        while (not nickname):
            nickname = input(f"Enter nickname for {action}: ")

        sock.send(nickname.encode())
        answer = sock.recv(1024).decode()
        if (action == Action.login.value and answer != AuthStatus.nickname_busy.value or
            action == Action.registration.value and answer != AuthStatus.no_such_user.value):
            print(f"Server: operation failed, because {answer}")
            sock.close()
            return
    
        password = ""
        while (not password):
            password = input(f"Enter password for {nickname}: ")

        sock.send(password.encode())
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
            print('Server: ' + data)
            message = input(f"You({nickname}): ")
        sock.close()
    except:
        print(f"Server: {ConnectionStatus.disconnected.value}")
        sock.close()
        return


if __name__ == '__main__':
    main()