import socket
import time
from threading import Thread


def process(client_socket, addr):
    data = client_socket.recv(1024)  # Receive up to 1024 bytes of data
    time.sleep(5)
    client_socket.send(
        f"HTTP/1.1 200 OK\r\n\r\nResponse:{addr}\r\n".encode()
    )  # Send a response to the client
    client_socket.close()


def main():
    server_ip = "127.0.0.1"
    server_port = 9000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.setblocking(False)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(2)
    while True:
        try:
            print("Listening...")
            client_socket, client_address = server_socket.accept()
            thread = Thread(
                target=process, args=(client_socket, client_address), daemon=True
            )
            thread.start()
            # thread.join()
        except Exception as error:
            print(error)
            time.sleep(1)


if __name__ == "__main__":
    main()
