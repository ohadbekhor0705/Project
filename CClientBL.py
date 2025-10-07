

import socket


class CClientBL():
    def __init__(self) -> None:
        self.ADDR = ("127.0.0.1", 5000)
        self.connected = False
        self.client_socket = None

    def connect(self, username: str, password: str) -> socket.socket:
        try:
            _client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            _client_socket.connect(self.ADDR)
            print(f"[CLIENT_BL] {_client_socket.getsockname()} connected")
            self.connected = True
            return _client_socket
        except Exception as e:
            print("[CLIENT_BL] Exception on connect: {}".format(e))
            return None
    
    def disconnect(self):
        pass
