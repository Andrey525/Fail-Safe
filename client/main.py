import socket


def main():
    host = socket.gethostname()
    port = 8080
    sock = socket.socket()
    sock.connect((host, port))

    action = ""
    while (not action):
        action = input("Enter action type (login or registration): ")


    sock.send(action.encode())
    answer = sock.recv(1024).decode()
    if (answer != "success"):
        print(f"Server: operation failed, because {answer}")
        sock.close()
        return

    nickname = ""
    while (not nickname):
        nickname = input(f"Enter nickname for {action}: ")

    sock.send(nickname.encode())
    answer = sock.recv(1024).decode()
    if (answer != "success"):
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

    message = input(f"You({nickname}): ")
    while message.lower().strip() != 'exit':
        sock.send(message.encode())
        data = sock.recv(1024).decode()
        print('Server: ' + data)
        message = input(f"You({nickname}): ")
    sock.close()


if __name__ == '__main__':
    main()