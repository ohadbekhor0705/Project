

from models import User


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
except ModuleNotFoundError:
    raise ModuleNotFoundError("please run command on the terminal: pip install -r requirements.txt")
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
            while self.event.is_set() and self.server_socket is not None:  # Main accept loop
                client, address = self.server_socket.accept()  # Accept new client
                write_to_log(client)
                payload: Dict[str,Any] = json.loads(client.recv(1024).decode())  # Receive initial message
                print(payload)
                response = {
                    "status": False,
                    "message": "<authentication Response from server>"
                }
                # Handle login command
                if payload["cmd"] == "login":
                    if (_user  := getUser(payload)):
                        self.createHandler(client, address,_user)  # Create handler thread
                        response = {"status": True, "message": f"Welcome back, {payload['username']}", "user": "_user"}
                    else:
                        response = {"status": False, "message": "Username or password are Invalid!"}

                # Handle register command
                elif payload["cmd"] == "register":
                    payload["password_hash"] = bcrypt.hashpw(payload["password"].encode("utf-8"),bcrypt.gensalt()).decode()
                    response = InsertUser(payload)
                    if response["status"] == True:
                        user: User | None = getUser(payload)
                        self.createHandler(client,address,user)
                # Send response to client
                client.send(json.dumps(response).encode())
        except OSError as e:
            pass  # Ignore OS errors
        #except Exception as e:
        #    write_to_log(f"[ServerBL] Exception at start_server(): {e}")  # Log other exceptions

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
                #self.clients_table.delete(*self.clients_table.get_children())  # Clear GUI table
            
            if self.server_socket is not None:
                self.server_socket.close()  # Close server socket
                self.server_socket = None
            
            self.main_thread = None  # Clear main thread
            write_to_log("[CServerBL] Closed server!")  # Log closed
        except Exception as e:
            write_to_log(f"[ServerBL] Exception at stop_server(): {e}")  # Log exceptions

    def createHandler(self, client_socket: socket.socket, client_address, user: User) -> None:
        client_handler: CClientHandler = CClientHandler(client_socket, client_address, user)  # Create handler
        self.clientHandlers.append(client_handler)  # Add to handler list
        client_handler.start()  # Start handler thread
    
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
    
    def __init__(self, client_socket: socket.socket, client_address, user: User) -> None:
        super().__init__()
        self.client: socket.socket = client_socket
        self.address: Tuple[str,int]  = client_address
        self.connected = True
        self.user: User = user
        self.daemon = True
    # This code run for every client in a different thread
    def run(self) -> None:
        # Server functionality here
        while self.connected and self.client is not None:
            try:
                if self.client.recv(4, socket.MSG_PEEK) == b"!DIS":
                    break
                message_len: int = struct.unpack("!Q",self.client.recv(8))[0]
                payload: dict[str, Any] = json.loads(self.client.recv(message_len).decode())
                write_to_log(f"[ServerBL] {payload=}")
                response = handle_client_request(payload,self.client,self.user) # Handle client request
                response_bytes = json.dumps(response).encode()
                self.client.send(struct.pack("!Q",len(response_bytes)))
                self.client.send(response_bytes)
            except ConnectionResetError:
                print("client was forced closed!")
                #write_to_log(f"[CServerBL] -> [ClientHandler] Exception at run(): {e}")
            finally:
                self.disconnect()
    def disconnect(self) -> None:
        print(f"[SERVER-BL] {self} disconnected")
        self.connected = False
        if self.client:
            self.client.close()
        self.client = None
        self = None
        
    def __repr__(self) -> str:
        return f"<ClientHandler({self.address=}, \n{self.client=})>"
if __name__ == "__main__":
    try:
        write_to_log("Press Ctrl + C to exit.")
        server = CServerBL()
        server.start_server()
    except KeyboardInterrupt:
        write_to_log("closing program")
        server.stop_server()
        quit()