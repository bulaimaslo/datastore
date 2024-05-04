import socket


def start_client(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # message = "SET myKey myValue"
    messages = [
        "SET myKey myValue",
        "GET myKey",
        "DELETE myKey",
        "EXISTS myKey",
        "KEYS myKey",
    ]

    for message in messages:
        client_socket.sendall(message.encode())
        response = client_socket.recv(1024)  # max of 1024
        print("Received from server: ",  response.decode())

    # client_socket.close()


HOST = "127.0.0.1"
PORT = 65432

start_client(HOST, PORT)
