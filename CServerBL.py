import socket
import threading
import cryptography
import sqlite3
import json


class CServerBL():
    def __init__(self):
        self._ip: str = "0.0.0.0"
        self._port = 5000
        self.server_socket = None
        self.run = False

        self.clients: list[CClientHandler] =  []
        with sqlite3.connect("Database.db") as conn:
            cur = conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users(
                    uid INTEGER PRIMARY KEY,
                    username CHAR(255),
                    password_hash CHAR(255),
                    max_storage INT,
                    curr_storage INT,
                    tries INT,
                    disabled BOOLEAN
                )

                CREATE TABLE IF NOT EXISTS files (
                    file_id INTEGER PRIMARY KEY
                    filename CHAR(255),
                    filesize INTEGER,
                    modified TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(uid)
                )
                """
            )
            conn.commit()
    def start_server(self) ->  None:
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.server_socket.bind((self._ip, self._port))
            self._server_socket.listen(5)
            while self.run and self.server_socket is not None:
                client_socket, client_address = self.server_socket.accept()
                
                client_handler: CClientHandler = CClientHandler(client_socket, client_address)
                client_handler.start()
                self.clients.append(client_handler)
        except Exception as e:
            print(e)
    
    def stop_server(self):
        for client in self.clients:
            client.join()
        if self.run:
            self.run = False
        if self.server_socket:
            self.server_socket = None
        self.clients = []



class CClientHandler(threading.Thread):
    def __init__(self, client_socket: socket.socket, client_address: socket._Address) -> None:
        super().__init__()
        
        self.client_socket: socket.socket = client_socket
        self.client_address: socket._Address  = client_address
        self.connected = False
    
    # This code run for every client in a different thread
    def run(self) -> None:

        self.connected = True
        # Server functionality here
        while self.connected:
            pass