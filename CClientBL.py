
import socket
from typing import Tuple,BinaryIO
import json
import struct
import os
from customtkinter import CTkProgressBar
from tkinter.ttk import Treeview
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
            self.user: dict[str, str] = {
                    "username": username,
                    "password": password,
                    "cmd": cmd
            }
            print(self.user)
            _client_socket.send(json.dumps(self.user).encode())
            response = json.loads(_client_socket.recv(1024).decode())
            print(response)
            if response["status"] == True:
                self.connected = True
                print("connected!")
                print(f"[CLIENT_BL] {_client_socket.getsockname()} connected")
                print(response["message"])
                print(f"{response["message"]=}")
                return f"{response["message"]}", _client_socket
            else:
                self.user = {}
                return response["message"], None
        except Exception as e:
            print("[CLIENT_BL] Exception on connect: {}".format(e))
            return "Could'nt connect to server!",None
    
    def sendfile(self,file: BinaryIO, command: str, prog_barRef:CTkProgressBar = None,files_table: Treeview = None) -> None:
        try:    
            file_size = os.path.getsize(file.name)    
            payload: str = json.dumps({
                "cmd": command,
                "filename":  file.name.split("/")[-1],
                "filesize": file_size
            })
            # print(payload)
            # print(f"{struct.pack('!Q',len(payload))}")
            sent: int = 0
            #prog_barRef.set(0)
            self.client.send(struct.pack("!Q",len(payload))) # send payload length
            self.client.send(payload.encode("utf-8")) # send payload
            ran = False
            while chunk:= file.read(4096): # read file in chunks
                #print(chunk is None)
                #print("sending:",chunk)
                if chunk:
                    self.client.sendall(chunk) # send chunks
                #sent += len(chunk)
                #prog_barRef.set(sent * 100 / file_size) # update progress bar
            files_table.insert("","end",(file.name.split("/")[-1] ,int(os.path.getsize(payload["filename"])/ (1024 * 1024)),""))
        except Exception as e:
            return

    def disconnect(self) -> None:
        self.connected = False
        if self.client:
            self.client.close()
        self.client = None
if __name__ == "__main__":
    client: CClientBL | None = CClientBL()
    msg, client.client = client.connect("Ogadichka4","Ogadich","login")
    print(msg)
    with open("./Thomas_Calculus.pdf","rb") as f:
        client.sendfile(f,"upload")
    response_length: int = struct.unpack("!Q",client.client.recv(8))[0]
    response = json.loads(client.client.recv(response_length).decode())
    print(response)
    