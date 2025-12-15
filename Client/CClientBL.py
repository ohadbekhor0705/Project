import io
import socket
from typing import Tuple,BinaryIO
import json
import struct
import os
from typing import Any
from customtkinter import CTkProgressBar, CTkLabel
from datetime import datetime
from tkinter.ttk import Treeview
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography import fernet
import base64
class CClientBL():
    def __init__(self) -> None:
        self.ADDR = ("127.0.0.1", 9999)
        self.connected: bool = False
        self.client: socket.socket | None = None
        self.user = {}
        
        self.public_key: bytes
        self.session_key: bytes
        self.fernet: fernet.Fernet

        self.current_storage: int = 0
        self.max_storage: int = 0
        self.files: list[dict[str,Any]] = []
        self.username: str = ""

        
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
            # Receiving public key from server
            key_len_recv = _client_socket.recv(8)
            len_pem_public: int = struct.unpack("!Q",key_len_recv)[0]

            pem_public = _client_socket.recv(len_pem_public)
            self.public_key = server_public_key = serialization.load_pem_public_key(pem_public) # Loading public key
            #Generate session key and send it encrypted
            raw_session_key = os.urandom(32)
            self.session_key = base64.urlsafe_b64encode(raw_session_key)
            encrypted_session_key = server_public_key.encrypt(self.session_key,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
            _client_socket.send(struct.pack("!Q",len(encrypted_session_key)) + encrypted_session_key) #sending session key

            self.fernet = fernet.Fernet(self.session_key)


            auth = {
                    "username": username,
                    "password": password,
                    "cmd": cmd
            }
            encrypted_auth = self.fernet.encrypt(json.dumps(auth).encode())
            _client_socket.send(struct.pack("!Q",len(encrypted_auth)) +  encrypted_auth)
            # getting authentication response:
            response_length: bytes = _client_socket.recv(8)
            response_bytes_encrypted: bytes = _client_socket.recv(struct.unpack("!Q",response_length)[0])
            response: dict[str, Any] = json.loads(self.fernet.decrypt(response_bytes_encrypted).decode())
            print(response)
            if response["status"] == True:
                self.user = response["user"]
                self.connected = True
                self.files = response["files"]
                self.username = auth["username"]
                self.current_storage = response["user"]["curr_storage"]
                self.max_storage = response["user"]["max_storage"]
                return response, _client_socket
            else:
                return response, None
        except ConnectionRefusedError:
            return {"message": "The server isn't running. Please Try Again Later."},None
    
    def sendfile(self,file: BinaryIO, command: str,progress_bar: CTkProgressBar, files_table: Treeview, title: CTkLabel) -> None:
        file_size: int = os.path.getsize(file.name)
        if file_size + self.current_storage  > self.max_storage:
            title.configure(text= "You're out of storage!")
            return
        payload: dict[str, Any] = {
            "cmd": command,
            "filename":  file.name.split("/")[-1],
            "filesize": file_size,
        } 
        self.send_message(payload)
        sent: int = 0
        chunk_size = 256 * 1024
        while chunk := file.read(chunk_size):
            self.client.sendall(chunk)
            sent += chunk_size
            progress_bar.set(sent/file_size)
        response: dict[str, Any] = self.get_message()
        print(f"[CClientBl] received from server: {response}")
        if response["status"]:
            self.files.append({"file_id": response["file_id"] ,"filename": payload["filename"], "filesize": file_size})
            self.current_storage += file_size
            progress_bar.set(0)
            dateTime: datetime = datetime.now().strftime("%Y-%m-%d")
            files_table.insert("","end", values= (response["file_id"],file.name.split("/")[-1], str(round(file_size/1048576,2))+" MB",dateTime))
            title.configure(text=f"{response["message"]}")
            print(response["message"])
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
        

    def ReceiveFile(self,progress_bar: CTkProgressBar, file_id:str, filename:str, file_size: int):

        received = 0
        print(file_size)
        self.send_message({"cmd": "save","file_id": file_id,"filename":filename})
        
        chunk_size = 1024 *256
        written: int = 0
        if not os.path.exists("./saved_files"):
            os.mkdir("saved_files")
        with open(f"saved_files/{filename}","wb") as saved_file:
            while received < file_size:
                chunk = self.client.recv(256 * 1024)
                received += len(chunk)
                saved_file.write(chunk)
                progress_bar.set(received/file_size)
            
    def send_message(self, payload: dict[str,Any]) -> None:
        """sending Encrypted message to server

        Args:
            payload (dict[str,Any]): payload to send.
        """        
        encoded_json: bytes = json.dumps(payload).encode()
        encrypted = self.fernet.encrypt(encoded_json)
        self.client.send(struct.pack("!Q",len(encrypted))+ encrypted)

    def get_message(self) -> dict[str, Any]:
        """Receiving response frm server

        Returns:
            dict[str, Any]: message from server.
        """ 
        len_bytes: bytes = self.client.recv(8)
        encrypted_payload = self.client.recv(struct.unpack("!Q",len_bytes)[0])
        
        return json.loads(self.fernet.decrypt(encrypted_payload).decode())
    
