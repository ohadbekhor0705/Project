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
            if response["status"] == True:
                self.user = response["user"]
                self.connected = True
                self.files = response["files"]
                self.user = response["user"]
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
            self.send_message(payload)
            sent: int = 0
            chunk_size = 256 * 1024
            while chunk:= file.read(chunk_size): # read file in chunks of 256 KB.
                
                self.client.sendall(chunk) # type: ignore # send chunk
                sent += len(chunk)
                ratio: float = sent/file_size
                progress_bar.set(ratio)

            response: dict[str, Any] = self.get_message()
            print(f"[CClientBl] received from server: {response}")
            if response["status"]:
                self.files.append({"file_id": response["file_id"] ,"filename": payload["filename"], "filesize": file_size})
                self.user["curr_storage"] += file_size
                progress_bar.set(0)
                dateTime: datetime = datetime.now().strftime("%Y-%m-%d")
                files_table.insert("","end", values= (response["file_id"],file.name.split("/")[-1], str(round(file_size/1048576,2))+" MB",dateTime))
                title.configure(text=f"{response["message"]}")
            enable() # type: ignore

        except Exception as e:
            print(e)
    
    def delete_files(self,file_ids: list[str], files_table: Treeview, selected_rows: tuple[str,...], title: CTkLabel) -> None:
        payload = {
            "cmd": "delete",
            "ids": file_ids
        }
        self.send_message(payload)
        response = self.get_message()
        title.configure(text=response["message"])
        if response["status"]:
            files_table.delete(*selected_rows)
    def send_message(self, payload: dict[str,Any]) -> None:
        encoded_json: bytes = json.dumps(payload).encode()
        self.client.send(struct.pack("!Q",len(encoded_json)) + encoded_json)  # send payload with 8-byte representation of size at the beginning

    def get_message(self) -> dict[str, Any]:
        """Receiving response frm server

        Returns:
            dict[str, Any]: _description_
        """        
        message_len_bytes: bytes = self.client.recv(8)
        message_len: int = struct.unpack("!Q",message_len_bytes)[0]
        payload: dict[str, Any] = json.loads(self.client.recv(message_len).decode())

        return payload