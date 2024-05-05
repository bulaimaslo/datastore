import socket
import threading
import json
import os
import time
from rwlock import RWLock


class KeyValueServer:
    def __init__(self, host, port, filename="data.json"):
        self.host = host
        self.port = port
        self.filename = filename
        self.lock = RWLock()
        self.data = {}
        self.transaction_data = None
        self.load_data()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

    def handle_client(self, client_socket, address):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            print(f"Received from {address}: {data.decode()}")

            command, key, value = self.parse_request(data.decode())
            if command == "SET":
                response = self.handle_set(key, value)
            elif command == "GET":
                response = self.handle_get(key)
            elif command == "EXISTS":
                response = self.handle_exists(key)
            elif command == "DELETE":
                response = self.handle_delete(key)
            elif command == "KEYS":
                response = self.handle_keys()
            elif command == "INCR":
                response = self.handle_incr(key)
            elif command == "DECR":
                response = self.handle_decr(key)
            else:
                response = "Unknown command"

            client_socket.sendall(response.encode())

            self.save_data()

    def handle_set(self, key, value):
        self.lock.writer_lock.acquire()
        try:
            if key and value:
                expiration_time = time.time() + 24 * 60 * 60
                self.data[key] = (value, expiration_time)
                return "OK"
            else:
                return "Bad request"
        finally:
            self.lock.writer_lock.release()

    def handle_get(self, key):
        self.lock.writer_lock.acquire()
        try:
            value, expiration_time = self.data.get(key, (None, None))
            if value is None or (expiration_time and time.time() > expiration_time):
                return "Key not found"
            else:
                expiration_time = time.time() + 24 * 60 * 60
                self.data[key] = (value, expiration_time)
                return value
        finally:
            self.lock.writer_lock.release()

    def handle_exists(self, key):
        self.lock.writer_lock.acquire()
        try:
            value, expiration_time = self.data.get(key, (None, None))
            if value is None or (expiration_time and time.time() > expiration_time):
                return "Key not found"
            else:
                expiration_time = time.time() + 24 * 60 * 60
                self.data[key] = (value, expiration_time)
                return "Key exists"
        finally:
            self.lock.writer_lock.release()

    def handle_delete(self, key):
        self.lock.writer_lock.acquire()
        try:
            if key in self.data:
                del self.data[key]
                return "OK"
            else:
                return "Key not found"
        finally:
            self.lock.writer_lock.release()

    def handle_keys(self):
        self.lock.reader_lock.acquire()
        try:
            return ", ".join(self.data.keys())
        finally:
            self.lock.reader_lock.release()

    def handle_incr(self, key):
        self.lock.writer_lock.acquire()
        try:
            value, expiration_time = self.data.get(key, (0, None))
            if not isinstance(value, int):
                return "Value is not an integer"
            value += 1
            self.data[key] = (value, expiration_time)
            return str(value)
        finally:
            self.lock.writer_lock.release()
    
    def handle_decr(self, key):
        self.lock.writer_lock.acquire()  
        try:
            value, expiration_time = self.data.get(key, (0, None))
            if not isinstance(value, int):
                return "Value is not an integer"
            value -= 1
            self.data[key] = (value, expiration_time)
            return str(value)
        finally:
            self.lock.writer_lock.release() 

    def parse_request(self, message):
        parts = message.split(" ")
        command = parts[0]
        key = parts[1] if len(parts) > 1 else None
        value = parts[2] if len(parts) > 2 else None

        return command, key, value

    def save_data(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f)

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                self.data = json.load(f)

    def remove_expired_entries(self):
        while True:
            time.sleep(86400)
            self.lock.writer_lock.acquire()
            try:
                current_time = time.time()
                keys_to_remove = [
                    key
                    for key, (value, expiration_time) in self.data.items()
                    if expiration_time and current_time > expiration_time
                ]
                for key in keys_to_remove:
                    del self.data[key]
            finally:
                self.lock.writer_lock.release()

    def listen(self):
        self.server_socket.listen()
        print(f"listening on {self.host}:{self.port}")
        while True:
            client_socket, address = self.server_socket.accept()
            client_thread = threading.Thread(
                target=self.handle_client, args=(client_socket, address)
            )
            client_thread.start()

    def start(self):
        try:
            self.listen()
            threading.Thread(target=self.remove_expired_entries, daemon=True).start()
        finally:
            self.server_socket.close()


HOST = "127.0.0.1"
PORT = 65432

server = KeyValueServer(HOST, PORT)
server.start()
