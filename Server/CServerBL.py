try:
    from typing import Any, Dict
    import socket  # Import socket for networking
    import threading  # Import threading for concurrent connections
    import json  # Import json for message serialization
    import os  # Import os for file system operations
    from tkinter.ttk import Treeview  # Import Treeview for GUI client table
    from typing import Callable, List, Tuple, Dict  # Type hints
    from protocol import *  # Import protocol definitions
    import bcrypt  # Import bcrypt for password hashing
    from models import User,File,SessionLocal # Import db for Database operations
    import struct
    from customtkinter import CTkTextbox
    from run import run
    import multiprocessing
    import hashlib
except ModuleNotFoundError:
    raise ModuleNotFoundError("please run command on the terminal: pip install -r requirements.txt")
class CServerBL():
    def __init__(self) -> None:
        self._ip: str = "0.0.0.0"  # Server IP address
        self._port: int = 9999  # Server port
        self.server_socket: socket.socket | None = None  # Main server socket
        self.clients_table: Treeview | None = None  # GUI table for clients
        self.clientHandlers: List[CClientHandler] = []  # List of client handler threads
        self.event = threading.Event()  # Event flag for server loop
        self.main_thread: threading.Thread | None = None  # Main server thread
        self.web_server: multiprocessing.Process | None
        storage_folder_name = "./StorageFiles"  # Folder for storage
        if not os.path.exists(storage_folder_name):  # Create folder if not exists
            os.mkdir(storage_folder_name)
        
        self.logger_box: None | CTkTextbox = None
    # Start the server
    def start_server(self) ->  None:
        """
        Start the TCP server and enter the accept loop.
        Initializes and binds a TCP socket to self._ip and self._port, sets self.event,
        and begins listening for incoming client connections.
        """
        self.web_server = multiprocessing.Process(target=run)
        self.write_to_log(self)  # Log server start
        self.web_server.start()
        try:
            self.event.set()  # Set event flag
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create socket
            self.server_socket.bind((self._ip, self._port))  # Bind socket to IP and port
            self.server_socket.listen(5)  # Listen for connections
            self.write_to_log(f"[SERVER] is running at \nIP: {socket.gethostbyname(socket.gethostname())} \nPORT: {self._port}")
            while self.event.is_set() and self.server_socket is not None:  # Main accept loop
                client, address = self.server_socket.accept()  # Accept new client
                self.write_to_log(client)
                # getting payload from client
                payload_length_bytes: bytes = client.recv(8) 
                payload_bytes: bytes = client.recv(struct.unpack("!Q",payload_length_bytes)[0])
                payload: dict = json.loads(payload_bytes.decode())
                self.write_to_log(f"[CClientBL] Authentication payload received: {payload}")
            
                response = {
                    "status": False,
                    "message": "<authentication Response from server>"
                }
                # Handle login command
                if payload["cmd"] == "login":
                    if (_user  := getUser(payload)):
                        self.createHandler(client, address,_user)  # Create handler thread
                        response = {"status": True, "message": f"Welcome back, {payload['username']}", "user": _user.toDict()}
                        uid: int = _user.user_id
                        files: list[dict[str, Any]] = files_by_id(uid)
                        print(f"{files=}")
                        response["files"] = files
                    else:
                        response = {"status": False, "message": "Username or password are Invalid!"}

                # Handle register command
                elif payload["cmd"] == "register":
                    payload["password_hash"] = bcrypt.hashpw(payload["password"].encode("utf-8"),bcrypt.gensalt()).decode()
                    response = InsertUser(payload)
                    if response["status"] == True:
                        user: User | None = getUser(payload)
                        response["user"] = user.toDict()
                        response["files"] = []
                        self.createHandler(client,address,user)
                
                # Send response to client 
                client.send(struct.pack("!Q",len(json.dumps(response).encode())) + json.dumps(response).encode())
        except OSError as e:
            pass  # Ignore OS errors
        #except Exception as e:
        #    self.write_to_log(f"[ServerBL] Exception at start_server(): {e}")  # Log other exceptions

    def stop_server(self) -> None:
        self.write_to_log(f"[ServerBL] stop_server() called")  # Log stop
        try:
            self.web_server.kill()
            self.web_server = None
            self.event.clear()  # Clear event flag
            self.write_to_log(f"[ServerBL] cleared flag!")
            for clientHandler in self.clientHandlers:
                if clientHandler.client: clientHandler.client.send(b"!DIS")
                self.write_to_log(f"closing {clientHandler}")
                if clientHandler:
                    clientHandler.client.send(b"!DIS") # sending connection
                    clientHandler.disconnect()  # Disconnect client
                    clientHandler.join()  # Wait for thread to finish
            self.clientHandlers = []  # Clear handler list
            
            if self.server_socket:
                self.server_socket.close()  # Close server socket
                self.server_socket = None
            
            self.main_thread = None  # Clear main thread
            self.write_to_log("[CServerBL] Closed server!")  # Log closed
        except Exception as e:
            self.write_to_log(f"[ServerBL] Exception at stop_server(): {e}")  # Log exceptions

    def createHandler(self, client_socket: socket.socket, client_address, user: User) -> None:
        client_handler: CClientHandler = CClientHandler(client_socket, client_address, user, self.write_to_log)  # Create handler
        self.clientHandlers.append(client_handler)  # Add to handler list
        client_handler.start()  # Start handler thread
    
    def __repr__ (self) -> str:
        return f"<Server(ip={self._ip}, port={self._port}, flag={self.event.is_set()}, {self.server_socket})>"

    def write_to_log(self, msg: Any) -> None:
        print(msg)
        if self.logger_box:
            self.logger_box.insert("end",f"{msg}\n")
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
    
    def __init__(self, client_socket: socket.socket, client_address, user: User, write_to_log) -> None:
        super().__init__()
        self.client: socket.socket | None= client_socket
        self.address: Tuple[str,int]  = client_address
        self.connected = True
        self.user: User = user
        self.daemon = True
        self.write_to_log = write_to_log

        if not os.path.exists("./StorageFiles"):
            os.mkdir("./StorageFiles")
    # This code run for every client in a different thread
    def run(self) -> None:
        # Server functionality here
        self.write_to_log(f"[CClientBl] {threading.active_count() - 1} Are currently connected!")
        while self.connected and self.client is not None:
            try:
                if  self.client.recv(4, socket.MSG_PEEK) == b"!DIS":
                    break
                message_len_bytes: bytes = self.client.recv(8)
                if message_len_bytes == b"":
                    break
                message_len: int = struct.unpack("!Q",message_len_bytes)[0]
                
                payload: dict[str, Any] = json.loads(self.client.recv(message_len).decode())
                response: dict[str, Any] = handle_client_request(payload,self.client,self.user) # Handle client request
                self.write_to_log(f"{response =}")
                if response:
                    response_bytes: bytes = json.dumps(response).encode()
                    self.client.send(struct.pack("!Q",len(response_bytes)) + response_bytes)
            except ConnectionResetError:
                self.write_to_log("client was forced closed!")
                #self.write_to_log(f"[CServerBL] -> [ClientHandler] Exception at run(): {e}")
                break
            except ConnectionAbortedError:
                self.write_to_log("client connection Aborted!")
                break
        self.disconnect()
        
    def disconnect(self) -> None:
        self.write_to_log(f"[SERVER-BL] {self} disconnected")
        self.connected = False
        if self.client:
            self.client.close()
        self.client = None
        del self
        
    def __repr__(self) -> str:
        return f"<ClientHandler({self.address=}, \n{self.client=})>"
if __name__ == "__main__":
    try:
        print("Press Ctrl + C to exit.")
        server = CServerBL()
        server.start_server()
    except KeyboardInterrupt:
        print("closing program")
        server.stop_server()
        quit()