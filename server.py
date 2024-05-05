import socket
import threading
import json
import os


class KeyValueServer:
    def __init__(self, host, port, filename='data.json'):
        self.host = host
        self.port = port
        self.filename = filename
        self.data = {}
        self.load_data()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

    def handle_client(self, client_socket, address):
        print(f"Handling connection from {address}")
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            print(f"Received from {address}: {data.decode()}")
            # decode, endoce bytes to string

            command, key, value = self.parse_request(data.decode())
            if command == "SET":
                if key and value:
                    self.data[key] = value # what if data already exists
                    response = "OK"
                else:
                    response = "Bad request"
            elif command == "GET":
                response = self.data.get(key, "Key not found")
            elif command == "DELETE":
                if key in self.data:
                    del self.data[key]
                    response = "OK"
                else:
                    response = "Key not found"
            elif command == "EXISTS":
                response = "True" if key in self.data else "False"
            elif command == "KEYS":
                response = ", ".join(self.data.keys())
            else:
                response = "Unknown command"

            client_socket.sendall(response.encode())
            self.save_data()

        # Uncomment for request-response model
        # print(f"Connection from {address} closed") 
        # client_socket.close()

    def parse_request(self, message):
        parts = message.split(' ')
        command = parts[0]
        key = parts[1] if len(parts) > 1 else None
        value = parts[2] if len(parts) > 2 else None

        return command, key, value

    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)
    
    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.data = json.load(f)

    def listen(self):
        self.server_socket.listen()
        print(f"listening on {self.host}:{self.port}")
        while True:
            client_socket, address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.start()


    def start(self):
        try:
            self.listen()
        finally:
            self.server_socket.close()



HOST = "127.0.0.1" 
PORT = 65432 

server = KeyValueServer(HOST, PORT)
server.start()
