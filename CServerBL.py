import socket
import threading
import json
import os
from tkinter.ttk import Treeview
from typing import Callable,List,Tuple, Dict
from protocol import *
import bcrypt
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
        """
        Start the TCP server and enter the accept loop.
        Initializes and binds a TCP socket to self._ip and self._port, sets self.event,
        and begins listening for incoming client connections. The method blocks in a
        loop while self.event.is_set() and self.server_socket is not None, accepting
        connections and handling an initial JSON-encoded message (recv buffer 1024 bytes)
        from each client. Expected initial messages and behavior:
        - "login": verifies credentials using db.is_exists(user_data). On success,
            creates a CClientHandler(client, address, self.table_callback), appends the
            handler to self.clientHandlers, starts the handler thread, and sends a JSON
            response with {"status": True, "message": "Welcome, <username>"}.
        - "register": checks username availability using db.username_exists(user_data["username"])
            and, if already taken, sends {"status": False, "message": "This username is already taken."}.
        - Any other or malformed data: sends {"status": False, "message": "Invalid Data!"}.
        All outgoing responses are JSON-encoded and sent through the client socket.
        Logging is performed via write_to_log. The method swallows OSError (pass) and
        logs other exceptions via write_to_log.
        Args:
                self: Instance of the server class. Expected attributes used by this method:
                        - _ip (str): IP address to bind to.
                        - _port (int): Port to bind to.
                        - event (threading.Event-like): Controls the server run loop.
                        - server_socket (socket.socket | None): Socket object created and assigned here.
                        - clientHandlers (list): Container to store started CClientHandler instances.
                        - table_callback: Callback passed to each CClientHandler.
                        - db: Object/module exposing is_exists(user_data) and username_exists(username).
                        - write_to_log: Callable used for logging messages.
        Returns:
                None
        Notes:
                - This method blocks until the server is stopped (event cleared) or an error occurs.
                - The initial client message is assumed to be JSON and is parsed without schema validation
                    beyond checking the "cmd" key; messages larger than 1024 bytes may be truncated.
                - The method has side effects: it modifies self.server_socket, sets self.event,
                    appends to self.clientHandlers, and starts new threads for client handlers.
                - Callers should ensure thread-safety for shared attributes if accessed concurrently.
        """

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
                user_data = json.loads(client.recv(1024))
                if user_data["cmd"] == "login":
                    if db.is_exists(user_data):
                        client_handler: CClientHandler = CClientHandler(client,address,self.table_callback)
                        self.clientHandlers.append(client_handler)
                        client_handler.start()
                        client.send(json.dumps(
                            {
                                "status": True,
                                "message": f"Welcome, {user_data["username"]}"
                            }
                    ).encode())
                elif user_data["cmd"] == "register":
                    if db.username_exists(user_data["username"]):
                        client.send(
                            json.dumps({
                                "status" : False,
                                "message" : "This username is already taken."
                            }).encode()
                        )
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

class CClientHandler(threading.Thread):
    """
    A client handler class that manages individual client connections in separate threads.
    This class inherits from threading.Thread to handle each client connection concurrently.
    It maintains the client socket connection, processes client requests, and manages
    disconnection events.
    Attributes:
        client (socket.socket): The client's socket connection
        address (Tuple[str,int]): Client's address info (IP, port)
        connected (bool): Connection status flag
        table_callback (Callable): Callback function to update client table
    Methods:
        run(): Main thread execution method that handles client communication
        disconnect(): Closes client connection and cleanup
        __repr__(): String representation of the client handler
    Args:
        client_socket (socket.socket): Socket object for client connection
        client_address (Tuple[str,int]): Client's address information
        table_callback (Callable): Function to manage client table updates
    """
    
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
    def disconnect(self) -> None:
        self.connected = False
        self.client.close()
    
    def __repr__(self) -> str:
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