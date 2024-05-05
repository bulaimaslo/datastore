import socket
import threading

def start_client(client_id, host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    messages = [
        "SUBSCRIBE",
        "BEGIN",
        "SET key{0} {0}".format(client_id),
        "GET key{0}".format(client_id),
        "INCR key2{0}".format(client_id),
        "GET key{0}".format(client_id),
        "DECR key2{0}".format(client_id),
        "GET key{0}".format(client_id),
        "COMMIT",
        "EXISTS key{0}".format(client_id),
        "KEYS",
        "END",
    ]

    for message in messages:
        client_socket.sendall(message.encode())
        while True:
            response = client_socket.recv(1024)  # max of 1024
            print("Received from server: ",  response.decode())
            if response.decode() == "END":
                break

    client_socket.close()


HOST = "127.0.0.1"
PORT = 65432

client_threads = []
for i in range(3):  
    client_thread = threading.Thread(target=start_client, args=(i, HOST, PORT))
    client_threads.append(client_thread)
    client_thread.start()

for client_thread in client_threads:
    client_thread.join()