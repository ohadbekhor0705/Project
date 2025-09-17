import socket
import threading
import cryptography
import sqlite3



class CServerBL():
    def __init__(self, ip: str, port: int):
        self._ip = ip
        self._port = port
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
                    curr_storage INT
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




class CClientHandler(threading.Thread):
    def __init__(self, client_socket, client_address):
        super().__init__()
        
        self.client_socket: socket.socket = client_socket
        self.client_address  = client_address
        self.connected = False
    

