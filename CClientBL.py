
import socket
from typing import Tuple

class CClientBL():
    def __init__(self) -> None:
        self.ADDR = ("127.0.0.1", 5000)
        self.connected: bool = False
        self.client_socket: socket.socket = None



    def connect(self, username: str, password: str) -> Tuple[str, socket.socket]: # Connecting to server with username and password
        try:
            _client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            _client_socket.connect(self.ADDR)
            print(f"[CLIENT_BL] {_client_socket.getsockname()} connected")
            self.connected = True
            return f"Welcome {username}!", _client_socket
        except Exception as e:
            print("[CLIENT_BL] Exception on connect: {}".format(e))
            return "Could'nt connect to server!",None
    def disconnect(self) -> None:
            pass
