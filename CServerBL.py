import socket
import threading
import cryptography
import sqlite3
import json
import os
from tkinter.ttk import Treeview
from typing import Callable,List,Tuple

class CServerBL():
    def __init__(self) -> None:
        self._ip: str = "0.0.0.0"
        self._port: int = 5000
        self.server_socket: socket.socket = None
        self.clients_table: Treeview = None
                # save list of clients
        self.clients: List[CClientHandler]  =  []
        self.event = threading.Event()
        self.main_thread: threading.Thread = None
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
        print(self)
        try:
            self.event.set()
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.server_socket.bind((self._ip, self._port))
            self.server_socket.listen(5)
            print(f"[SERVER] is running at \nIP: {socket.gethostbyname(socket.gethostname())} \nPORT: {self._port}")
            print(self)
            while self.event.is_set() and self.server_socket is not None:
                client_handler = CClientHandler(*self.server_socket.accept(),self.table_callback)
                client_handler.start()
                self.clients.append(client_handler)
        except OSError as e:
            pass
        except Exception as e:
            print(f"[ServerBL] Exception at start_server(): {e}")
    
    def stop_server(self) -> None:
        print(f"[ServerBL] stop_server() called")
        try:
            self.event.clear()
            print(f"[ServerBL] cleared flag!")
            if len(self.clients) > 0:
                for client in self.clients:
                    print(f"closing {client.client_address}")
                    client.disconnect()
                    client.join()
                self.clients = []
                self.clients_table.delete(*self.clients_table.get_children())
            
            if self.server_socket is not None:
                self.server_socket.close()
                self.server_socket = None
            
            self.main_thread = None
        except Exception as e:
            print(f"[ServerBL] Exception at close_server(): {e}")
    
    def table_callback(self, c_socket:socket.socket,addr ,action: str) -> None:
        if action == "add":
            self.clients_table.insert("", "end", values=(socket.gethostbyaddr(addr[0])[0],addr[0],"None","❌"))
    

    def __repr__ (self) -> str:
        return f"<Server(ip={self._ip}, port={self._port}, flag={self.event.is_set()}, {self.server_socket})>"

# This class handle every client in a different thread.
class CClientHandler(threading.Thread): #  Inherits  from BASE class Threading.Thread
    def __init__(self, client_socket: socket.socket, client_address, table_callback: Callable[[socket.socket,Tuple[str, int],str],None]) -> None:
        super().__init__()
        
        self.client_socket: socket.socket = client_socket
        self.client_address: Tuple[str,int]  = client_address
        self.connected = False
        self.table_callback: Callable[[socket.socket, Tuple[str, int], str], None]= table_callback
    # This code run for every client in a different thread
    def run(self) -> None:
        self.connected = True
        self.table_callback(self.client_socket,self.client_address,"add")
        # Server functionality here
        while self.connected:
            try:
                pass
            except Exception as e:
                print(f"[ClientHandler] Exception at run(): {e}")
    def disconnect(self):
        self.connected = False




if __name__ == "__main__":
    try:
        print("Press Ctrl + C to exit.")
        server = CServerBL()
        server.main_thread = threading.Thread(target=server.start_server)
        server.main_thread.start()
    except KeyboardInterrupt:
        print("closing program")
        exit()