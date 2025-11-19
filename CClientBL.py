
import socket
from typing import Tuple,BinaryIO
import json
from protocol import *
import struct
import os
class CClientBL():
    def __init__(self) -> None:
        self.ADDR = ("127.0.0.1", 9999)
        self.connected: bool = False
        self.client: socket.socket = None
        self.user = {}
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
            Receives and parses server response,
            Logs connection status and responses
            Returns server message and socket if successful
        """
        
        try:
            _client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            _client_socket.connect(self.ADDR) 
            self.user = {
                    "username": username,
                    "password": password,
                    "cmd": cmd
            }
            _client_socket.send(json.dumps(self.user).encode())
            response = json.loads(_client_socket.recv(1024).decode())
            write_to_log(response is None)
            if response["status"] == True:
                write_to_log("connected!")
                write_to_log(f"[CLIENT_BL] {_client_socket.getsockname()} connected")
                write_to_log(response["message"])
                print(f"{response["message"]=}")
                return f"{response["message"]}", _client_socket
            else:
                self.user = {}
                return response["message"], None
        except Exception as e:
            write_to_log("[CLIENT_BL] Exception on connect: {}".format(e))
            return "Could'nt connect to server!",None
    
    def sendfile(self,file: BinaryIO, command: str) -> bool:        
        payload: str = json.dumps({
            "cmd": command,
            "filename":  file.name.split("/"),
            "filesize": os.path.getsize(file.name)
        })
        self.client.send(struct.pack("!Q",len(payload)))
        self.client.send(payload.encode("utf-8"))
        while chunk:= file.read(4096):
            self.client.sendall(chunk)
        return True

    def disconnect(self) -> None:
        try:
            self.connected = False
            self.client.close()
            self.client = None
        except Exception as e:
            write_to_log(f"[ClientBL] error on disconnect() {e}")
if __name__ == "__main__":
    client = CClientBL()
    write_to_log(client.connect("test123","fhfhjfgh","login"))
     