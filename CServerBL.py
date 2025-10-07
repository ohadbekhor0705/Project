import socket
import threading
import cryptography
import sqlite3
import json
import os




class CServerBL():
    def __init__(self) -> None:
        self._ip: str = "0.0.0.0"
        self._port = 5000
        self.server_socket = None
        self.run = False
        # save list of clients
        self.clients: list[CClientHandler] =  []
        with sqlite3.connect("Database.db") as conn:
            # create tables if not exist
            cur = conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users(
                    user_id INTEGER PRIMARY KEY,
                    username CHAR(255),
                    password_hash CHAR(255),
                    max_storage INT DEFAULT 100000000,
                    curr_storage INT DEFAULT 0,
                    tries INT DEFAULT 0,
                    disabled BOOLEAN DEFAULT 0
                );


                CREATE TABLE IF NOT EXISTS files(
                file_id CHAR(255) PRIMARY KEY,
                filename CHAR(255),
                filesize INTEGER,
                modified INT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
                """
            )


            conn.commit()
        storage_folder_name = "./StorageFiles"
        if not os.path.exists(storage_folder_name):
            os.mkdir(storage_folder_name)

    # Start the server
    def start_server(self) ->  None:
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.server_socket.bind((self._ip, self._port))
            self.server_socket.listen(5)
            self.run = True
            print(f"[SERVER] is running at \nIP: {socket.gethostbyname(socket.gethostname())} \nPORT: {self._port}")
            while self.run and self.server_socket is not None:
                client_handler = CClientHandler(*self.server_socket.accept(),None)
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
    def table_callback(self) -> None:
        pass


# This class handle every client in a different thread.
class CClientHandler(threading.Thread): #  Inherits  from BASE class Threading.Thread
    def __init__(self, client_socket: socket.socket, client_address, table_callback) -> None:
        super().__init__()
        
        self.client_socket: socket.socket = client_socket
        self.client_address  = client_address
        self.connected = False
        self.table_callback = table_callback
    # This code run for every client in a different thread
    def run(self) -> None:

        self.connected = True
        # Server functionality here
        while self.connected:
            pass




if __name__ == "__main__":
    server = CServerBL()
    server.start_server()
