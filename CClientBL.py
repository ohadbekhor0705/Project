
import socket
from typing import Tuple
import json
from protocol import *
class CClientBL():
    def __init__(self) -> None:
        self.ADDR = ("127.0.0.1", 5000)
        self.connected: bool = False
        self.client_socket: socket.socket = None

    def connect(self, username: str, password: str, cmd: str) -> Tuple[str, socket.socket]:
        """
        Establishes a connection to the server and sends authentication credentials.
        Args:
            username (str): Username for authentication
            password (str): Password for authentication 
            cmd (str): Command to be sent to server
        Returns:
            Tuple[str, socket.socket]: A tuple containing:
                - str: Response message from server
                - socket.socket: Connected socket object if successful, None if connection fails
        Raises:
            Exception: Any network or connection related exceptions that may occur
        Description:
            Creates a TCP socket connection to the server specified in self.ADDR
            Sends JSON encoded credentials and command
            Receives and parses server response
            Logs connection status and responses
            Returns server message and socket if successful
        """
        
        try:
            _client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            _client_socket.connect(self.ADDR)
            _client_socket.send(json.dumps(
                {
                    "username": username,
                    "password": password,
                    "cmd": cmd
                }).encode()
            )
            response = json.loads(_client_socket.recv(1024).decode())
            write_to_log(response)
            if response["status"] == True:
                write_to_log(f"[CLIENT_BL] {_client_socket.getsockname()} connected")
                write_to_log(response["message"])
                return f"{response["message"]}", _client_socket

        except Exception as e:
            write_to_log("[CLIENT_BL] Exception on connect: {}".format(e))
            return "Could'nt connect to server!",None
    
    def disconnect(self) -> None:
        try:
            self.connected = False
            self.client_socket.close()
            self.client_socket = None
        except Exception as e:
            write_to_log(f"[ClientBL] error on disconnect() {e}")
if __name__ == "__main__":
    client = CClientBL()
    write_to_log(client.connect("username","password"))
     