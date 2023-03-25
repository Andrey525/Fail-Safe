import socket
import threading
import auth


def handler(sock, address):
    # Регистрация либо вход в существующий аккаунт
    nickname = auth.authorize(sock)
    if (not nickname):
        sock.close()
        return

    # Определяться в какой рум закидывать игрока
    # 

    # сама игра
    try:
        while True:
            data = sock.recv(1024).decode()
            if not data:
                break
            sock.send("Hi".encode())
    except:
        auth.logout(nickname)
        sock.close()
        print("Exception")
        return
    finally:
        auth.logout(nickname)
        sock.close()



def main():
    print("starting server")
    host = socket.gethostname()
    port = 8080
    sock = socket.socket()
    sock.bind((host, port))
    sock.listen(5)
    while (True):
        conn_sock, address = sock.accept()
        print("Connection from: " + str(address))
        thread = threading.Thread(target=handler, args=(conn_sock, address))
        thread.start()
    

if __name__ == '__main__':
    main()