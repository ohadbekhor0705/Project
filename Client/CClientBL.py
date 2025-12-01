
import socket
from typing import Tuple,BinaryIO
import json
import struct
import os
from typing import Any
from customtkinter import CTkProgressBar, CTkLabel
from datetime import datetime
from tkinter.ttk import Treeview
class CClientBL():
    def __init__(self) -> None:
        self.ADDR = ("127.0.0.1", 9999)
        self.connected: bool = False
        self.client: socket.socket | None = None
        self.user = {}
        self.files: list[dict[str,Any]] = []
    def connect(self, username: str, password: str, cmd: str) -> Tuple[dict[str,Any], socket.socket | None]:
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
            auth: dict[str, str] = {
                    "username": username,
                    "password": password,
                    "cmd": cmd
            }
            auth_bytes: bytes = json.dumps(auth).encode()
            _client_socket.send(struct.pack("!Q",len(auth_bytes)) +  auth_bytes)

            response_length: bytes = _client_socket.recv(8)
            response = json.loads(_client_socket.recv(struct.unpack("!Q",response_length)[0]))
            print(response)
            if response["status"] == True:
                self.user = response["user"]
                self.connected = True
                print("connected!")
                print(f"[CLIENT_BL] {_client_socket.getsockname()} connected")
                print(f"{response=}")
                self.files = response["files"]
                return response, _client_socket
            else:
                return response, None
        except ConnectionRefusedError:
            return {"message": "The server isn't running. Please Try Again Later."},None
        except Exception as e:
            print("[CLIENT_BL] Exception on connect: {}".format(e))
            return {"message": "Could'nt connect to server!"},None
    
    def sendfile(self,file: BinaryIO, command: str,progress_bar: CTkProgressBar, files_table: Treeview, title: CTkLabel, enable) -> None:
        try:    
            file_size: int = os.path.getsize(file.name)
            #if file_size + self.user["current_storage"]  > self.user["max_storage"]:
            #    title.configure(text= "You're out of storage!")
            #    return
            
            payload: dict[str, Any] = {
                "cmd": command,
                "filename":  file.name.split("/")[-1],
                "filesize": file_size
            }
            encoded_json: bytes = json.dumps(payload).encode()
            self.client.send(struct.pack("!Q",len(encoded_json)) + encoded_json) # type: ignore # send payload with 8-byte representation of size at the beginning
            sent: int = 0
            
            while chunk:= file.read(65536): # read file in chunks of 64 KB.
                
                self.client.sendall(chunk) # type: ignore # send chunk
                sent += len(chunk)
                ratio: float = sent/file_size
                progress_bar.set(ratio)

            response: dict[str, Any] = self.get_message()
            print(f"[CClientBl] received from server: {response}")
            if response["status"]:
                print(response)
                progress_bar.set(0)
                dateTime: str = datetime.now().strftime("%Y-%m-%D %H:%M")
                files_table.insert("","end", values= (file.name.split("/")[-1], round(file_size/1048576,2),dateTime))
                print(f"[CClientBL] {response=}")
                title.configure(text=f"{response["message"]}")
            enable() # type: ignore

        except Exception as e:
            print(e)

    def disconnect(self) -> None:
        self.connected = False
        if self.client:
            self.client.close()
        self.client = None
    

    def get_message(self) -> dict[str, Any]:
        message_len_bytes: bytes = self.client.recv(8) # type: ignore
        message_len: int = struct.unpack("!Q",message_len_bytes)[0]
        payload: dict[str, Any] = json.loads(self.client.recv(message_len).decode()) # 

        return payload
if __name__ == "__main__":
    client: CClientBL | None = CClientBL()
    msg, client.client = client.connect("username1234","password1234","login")
    print(msg)
    if not client.client:
        exit()
    print("sending file.....")
    with open("./user.json","rb") as f:
         client.sendfile(f,"upload") # type: ignore
    