
import socket
from typing import Tuple
import json
from protocol import *
class CClientBL():
    def __init__(self) -> None:
        self.ADDR = ("127.0.0.1", 5000)
        self.connected: bool = False
        self.client_socket: socket.socket = None

    def connect(self, username: str, password: str, cmd: str) -> Tuple[str, socket.socket]: # Connecting to server with username and password
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
    