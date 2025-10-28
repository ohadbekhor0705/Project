import socket
import threading
import json
import os
from tkinter.ttk import Treeview
from typing import Callable,List,Tuple, Dict
from protocol import *

class CServerBL():
    def __init__(self) -> None:
        self._ip: str = "0.0.0.0"
        self._port: int = 5000
        self.server_socket: socket.socket = None
        self.clients_table: Treeview = None
                # save list of clients
        self.clientHandlers: List[CClientHandler] = []
        self.event = threading.Event()
        self.main_thread: threading.Thread = None


        
        storage_folder_name = "./StorageFiles"
        if not os.path.exists(storage_folder_name):
            os.mkdir(storage_folder_name)

    # Start the server
    def start_server(self) ->  None:
        write_to_log(self)
        try:
            self.event.set()
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.server_socket.bind((self._ip, self._port))
            self.server_socket.listen(5)
            write_to_log(f"[SERVER] is running at \nIP: {socket.gethostbyname(socket.gethostname())} \nPORT: {self._port}")
            write_to_log(self)
            while self.event.is_set() and self.server_socket is not None:
                client, address = self.server_socket.accept()
                registration = json.loads(client.recv(1024))
                if registration["username"] == "ohad5200":
                    client_handler = CClientHandler(client,address,self.table_callback)
                    self.clientHandlers.append(client_handler)
                    client_handler.start()
                    
                    client.send(json.dumps(
                    {
                        "status": True,
                        "message": f"Welcome, {registration["username"]}"
                    }
                    ).encode())
                else:
                    self.client.send(json.dumps(
                        {
                            "status": False,
                            "message": f"Invalid Data!"
                        }
                    ).encode())
        except OSError as e:
            pass
        except Exception as e:
            write_to_log(f"[ServerBL] Exception at start_server(): {e}")
    
    def stop_server(self) -> None:
        write_to_log(f"[ServerBL] stop_server() called")
        try:
            self.event.clear()
            write_to_log(f"[ServerBL] cleared flag!")
            if len(self.clientHandlers) > 0:
                for clientHandler in self.clientHandlers:
                    write_to_log(f"closing {clientHandler}")
                    if clientHandler is not None:
                        clientHandler.disconnect()
                        clientHandler.join()
                self.clientHandlers = []
                self.clients_table.delete(*self.clients_table.get_children())
            
            if self.server_socket is not None:
                self.server_socket.close()
                self.server_socket = None
            
            self.main_thread = None
            write_to_log("[CServerBL] Closed server!")
        except Exception as e:
            write_to_log(f"[ServerBL] Exception at stop_server(): {e}")
    
    def table_callback(self, c_socket:socket.socket,addr ,action: str) -> None:
        if action == "add":
            self.clients_table.insert("", "end", values=(socket.gethostbyaddr(addr[0])[0],addr[0],"None","❌"))
    

    def __repr__ (self) -> str:
        return f"<Server(ip={self._ip}, port={self._port}, flag={self.event.is_set()}, {self.server_socket})>"

# This class handle every client in a different thread.
class CClientHandler(threading.Thread): #  Inherits  from BASE class Threading.Thread
    def __init__(self, client_socket: socket.socket, client_address, table_callback: Callable[[socket.socket,Tuple[str, int],str],None]) -> None:
        super().__init__()
        
        self.client: socket.socket = client_socket
        self.address: Tuple[str,int]  = client_address
        self.connected = False
        self.table_callback: Callable[[socket.socket, Tuple[str, int], str], str]= table_callback
    # This code run for every client in a different thread
    def run(self) -> None:
        self.table_callback(self.client,self.address,'add')
        # Server functionality here
        while self.connected:
            try:
                write_to_log("connected")
            except Exception as e:
                write_to_log(f"[CServerBL] -> [ClientHandler] Exception at run(): {e}")
        self.disconnect()
    def disconnect(self):
        self.connected = False
        self.client.close()
    
    def __repr__(self):
        return f"<ClientHandler({self.address=}, {self.client=})>"

if __name__ == "__main__":
    try:
        write_to_log("Press Ctrl + C to exit.")
        server = CServerBL()
        server.main_thread = threading.Thread(target=server.start_server)
        server.main_thread.start()
    except KeyboardInterrupt:
        write_to_log("closing program")
        exit()