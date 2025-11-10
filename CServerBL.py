import socket  # Import socket for networking
import threading  # Import threading for concurrent connections
import json  # Import json for message serialization
import os  # Import os for file system operations
from tkinter.ttk import Treeview  # Import Treeview for GUI client table
from typing import Callable, List, Tuple, Dict  # Type hints
from protocol import *  # Import protocol definitions
import bcrypt  # Import bcrypt for password hashing
from Database import db # Import db for Database operations
class CServerBL():
    def __init__(self) -> None:
        self._ip: str = "0.0.0.0"  # Server IP address
        self._port: int = 9999  # Server port
        self.server_socket: socket.socket = None  # Main server socket
        self.clients_table: Treeview = None  # GUI table for clients
        self.clientHandlers: List[CClientHandler] = []  # List of client handler threads
        self.event = threading.Event()  # Event flag for server loop
        self.main_thread: threading.Thread = None  # Main server thread
        storage_folder_name = "./StorageFiles"  # Folder for storage
        if not os.path.exists(storage_folder_name):  # Create folder if not exists
            os.mkdir(storage_folder_name)

    # Start the server
    def start_server(self) ->  None:
        """
        Start the TCP server and enter the accept loop.
        Initializes and binds a TCP socket to self._ip and self._port, sets self.event,
        and begins listening for incoming client connections.
        """
        write_to_log(self)  # Log server start
        try:
            self.event.set()  # Set event flag
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create socket
            self.server_socket.bind((self._ip, self._port))  # Bind socket to IP and port
            self.server_socket.listen(5)  # Listen for connections
            write_to_log(f"[SERVER] is running at \nIP: {socket.gethostbyname(socket.gethostname())} \nPORT: {self._port}")
            write_to_log(self)
            while self.event.is_set() and self.server_socket is not None:  # Main accept loop
                client, address = self.server_socket.accept()  # Accept new client
                write_to_log(client)
                user_data: Dict[str,Any] = json.loads(client.recv(1024).decode())  # Receive initial message
                response = {
                    "status": False,
                    "message": "<authentication Response from server>"
                }
                # Handle login command
                write_to_log(type(user_data))
                if user_data["cmd"] == "login" and (_user := db.getUser(user_data)) and _user["tries"] < 4:
                    self.createHandler(client, address, self.table_callback, _user)  # Create handler thread
                    response = {"status": True, "message": f"Welcome back, {user_data['username']}", "user": "_user"}
                    print(response)
                # Handle register command
                elif user_data["cmd"] == "register":
                    user_data["password"] = bcrypt.hashpw(user_data["password"].encode("utf-8"),bcrypt.gensalt())
                    response = db.Insert(user_data)
                    if response["status"] == True:
                        user = db.getUser(user_data)
                        response["user"] = "user"
                        self.createHandler(client,address,self.table_callback,user)
                # Send response to client
                client.send(json.dumps(response).encode())
        except OSError as e:
            pass  # Ignore OS errors
        except Exception as e:
            write_to_log(f"[ServerBL] Exception at start_server(): {e}")  # Log other exceptions

    def createHandler(self, client_socket: socket.socket, client_address, table_callback: Callable[[socket.socket, Tuple[str, int], str], None], user) -> None:
        client_handler: CClientHandler = CClientHandler(client_socket, client_address, table_callback, user)  # Create handler
        self.clientHandlers.append(client_handler)  # Add to handler list
        client_handler.start()  # Start handler thread
    
    def stop_server(self) -> None:
        write_to_log(f"[ServerBL] stop_server() called")  # Log stop
        try:
            self.event.clear()  # Clear event flag
            write_to_log(f"[ServerBL] cleared flag!")
            if len(self.clientHandlers) > 0:  # If handlers exist
                for clientHandler in self.clientHandlers:
                    write_to_log(f"closing {clientHandler}")
                    if clientHandler is not None:
                        clientHandler.disconnect()  # Disconnect client
                        clientHandler.join()  # Wait for thread to finish
                self.clientHandlers = []  # Clear handler list
                self.clients_table.delete(*self.clients_table.get_children())  # Clear GUI table
            
            if self.server_socket is not None:
                self.server_socket.close()  # Close server socket
                self.server_socket = None
            
            self.main_thread = None  # Clear main thread
            write_to_log("[CServerBL] Closed server!")  # Log closed
        except Exception as e:
            write_to_log(f"[ServerBL] Exception at stop_server(): {e}")  # Log exceptions
    
    def table_callback(self, c_socket: socket.socket, addr, action: str) -> None:
        if action == "add":
            self.clients_table.insert("", "end", values=(socket.gethostbyaddr(addr[0])[0], addr[0], "None"))  # Add client to table
    

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
    
    def __init__(self, client_socket: socket.socket, client_address, table_callback: Callable[[socket.socket,Tuple[str, int],str],None],user) -> None:
        super().__init__()
        
        self.client: socket.socket = client_socket
        self.address: Tuple[str,int]  = client_address
        self.connected = False
        self.table_callback: Callable[[socket.socket, Tuple[str, int], str], str]= table_callback
        self.user: Dict[str: Any] = user
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