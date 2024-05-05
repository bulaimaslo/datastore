import socket
import threading

def start_client(client_id, host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    messages = [
        "SET key{0} value{0}".format(client_id),
        "GET key{0}".format(client_id),
        "DELETE key{0}".format(client_id),
        "EXISTS key{0}".format(client_id),
        "KEYS",
    ]

    for message in messages:
        client_socket.sendall(message.encode())
        response = client_socket.recv(1024)  # max of 1024
        print("Received from server: ",  response.decode())

    client_socket.close()


HOST = "127.0.0.1"
PORT = 65432

client_threads = []
for i in range(10):  
    client_thread = threading.Thread(target=start_client, args=(i, HOST, PORT))
    client_threads.append(client_thread)
    client_thread.start()

for client_thread in client_threads:
    client_thread.join()