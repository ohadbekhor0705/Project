try:
    from socket import socket
    from typing import Any
    from sqlalchemy.orm.session import Session
    from sqlalchemy import and_, func, select
    import cryptography
    import logging
    from typing import Dict, Any, overload
    import bcrypt
    import socket
    from models import User, File, SessionLocal
    from datetime import datetime
    from uuid6 import uuid7
    from models import File, User
    import os
    from cryptography.fernet import Fernet
except ModuleNotFoundError:
    raise ModuleNotFoundError("please run command on the terminal: pip install -r requirements.txt")


CHUNK_SIZE = 1024 *256 # 256 KB

def username_exists(username: str, db: Session | None = None) -> bool: 
    if db is None:
        db = SessionLocal()
    result: bool = db.query(User).filter(User.username == username).first() is not None
    return result
@overload
def getUser(login: int) -> User | None: ...
@overload
def getUser(login: Dict[str,Any]) -> User | None: ...

def getUser(login: dict | int) -> 'User | None':
    """
    Retrieves a user record based on user ID or login credentials.
    Updates failed login attempts and disables the user after 3 failed tries.

    Args:
        login (dict | int): Either:
            - dict with 'username' and 'password' for login
            - int representing user_id

    Returns:
        User | None: SQLAlchemy User object if found, otherwise None.
    """
    user: 'User | None' = None

    with SessionLocal() as db:
        # Fetch user
        if isinstance(login, int):
            user = db.query(User).filter(User.user_id == login).first()
        elif isinstance(login, dict):
            user = db.query(User).filter(
                and_(User.username == login["username"], User.disabled == False)
            ).first()
        if not user:
            return  None
        # Handle login password
        if isinstance(login, dict):
            password_correct: bool = bcrypt.checkpw(
                login["password"].encode(), user.password_hash.encode()
            )
            if not password_correct:
                user.tries = (user.tries or 0) + 1
                if user.tries >= 3:
                    user.disabled = True
                db.commit()  # commit changes while session is active
        # create a new User object that is NOT bound to the session
        detached_user = User(
            user_id=user.user_id,
            username=user.username,
            password_hash=user.password_hash,
            tries=user.tries,
            disabled=user.disabled,
            max_storage=user.max_storage,
            curr_storage=user.curr_storage
        )
        return detached_user  # safe to use anywhere           


    pass

def InsertUser(user: Dict[str,Any]) -> Dict:
    """Insert a new user into the database.

    Args:
        user (Dict[str, Any]): A dictionary containing 'username' and 'password' keys.

    Returns:
        Dict: A dictionary with 'status' indicating success and 'response' message.
    """
    db: Session = SessionLocal()
    try:
        if username_exists(user["username"],db):
          return {"status":False, "message": "This username is already taken"}

        db.add(User(username=user["username"],password_hash=user["password_hash"]))
        db.commit()
        return {
          "status": True,
          "message": f"Welcome to skyVault, {user["username"]}!"
        }

    except Exception as e:
        return {
          "status": False,
          "message": f"{e}"
        }
    finally:
        db.close()

def files_by_id(uid: int) -> list[dict[str,Any]]:
    with SessionLocal() as db:
        files  = db.query(File).filter(File.user_id == uid).all()
        if not files:
            return []
        return [ {"file_id": f.file_id ,"filename": f.filename, "filesize": f.filesize, "modified": f.modified} for f in files]

def UploadFile(payload: dict[str, Any],client: socket.socket ,user: User) -> dict[str,Any] | None:
    """Uploading a file

    Args:
        payload (dict[str, Any]): Containing 
        client (socket.socket): client socket object
        user (User): client user information

    Returns:
        dict[str,Any]: status response from server to client
    """    
    file_id = str(uuid7())
    received: int = 0
    try:
        file_size: int = payload["filesize"]
        chunk_size = 256 * 1024
        with open(f"./StorageFiles/{file_id}.bin","wb") as f:
            while received < file_size:
                chunk: bytes = client.recv(chunk_size)
                if not chunk:
                    raise ConnectionResetError()
                f.write(chunk)
                received += len(chunk)
    except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError) as e:
        print(e)
        os.remove(f"./StorageFiles/{file_id}.bin")
        return None
    db = SessionLocal()
    user_in_session = db.merge(user)
    user_in_session.curr_storage += payload["filesize"]
    uploaded_file =  File(
            file_id=file_id,
            filename=payload["filename"],
            filesize=file_size,
            modified=int(datetime.now().timestamp()),
            user_id=user.user_id
        )
    db.add(uploaded_file)
    db.commit()
    db.close()
    return {"status": True, "message": payload["filename"]+" Uploaded!","file_id":file_id}

def DeleteFile(file_ids: list[str], user: User)-> dict[str, Any]:
    try:
        with SessionLocal() as db:
            # get the total size of all deleted files:
            # generates SELECT SUM(filesize) FROM Files WHERE file_id IN {file_ids}
            total_size: int = db.query(func.sum(File.filesize))\
                                .filter(File.file_id.in_(file_ids))\
                                .scalar() or 0
            # delete all the files from the db
            db.query(File)\
            .filter(File.file_id.in_(file_ids))\
            .delete(synchronize_session=False)
            # attach user to the session
            user_in_session = db.merge(user)
            user_in_session.curr_storage -= total_size
            db.commit()
        for file_id in file_ids:
            os.remove(f"./StorageFiles/{file_id}.bin")
        return {"status": True, "message": "File(s) deleted!"}
    except Exception as e:
        print(e)
        return {"status": False, "message": "Couldn't delete this file."}

def SendFile(client: socket.socket, file_id: str) -> None:
    """_summary_

    Args:
        client (socket.socket): _description_
        filename (str): _description_

    Returns:
        dict[str, Any]: _description_
    """
    global CHUNK_SIZE
    try:
        with open(f"./StorageFiles/{file_id}.bin","rb") as f:
            while chunk  := f.read(CHUNK_SIZE):
                client.sendall(chunk)
    except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
        pass
    return None

def createLink(file_id: str)-> dict[str, Any]:
    try:
        with SessionLocal() as db:
            file: File = db.query(File).filter(File.file_id == file_id).one()
        return {"status": True,"message": "Share link created!", "link": ""}
    except:
        return {"status": False,"message": "Couldn't Create share link."}

def handle_client_request(payload: dict[str, Any], client: socket.socket, user: User) -> dict[str, Any] | None:
    """Handling clients requests

    Args:
        payload (dict[str, Any]): client's requests with parameters.
        client (socket.socket): client socket object.
        user (User): client's user data.

    Returns:
        dict[str, Any] | None: Server Response.
    """    
    response: dict[str, Any] = {}
    match payload["cmd"]:
        case "upload":
            response = UploadFile(payload, client, user)
        case "delete":
            response = DeleteFile(payload["ids"], user)
        case "save":
            response = SendFile(client,payload["file_id"])
        case "createLink":
            response = createLink(payload["file_id"])
        case _:
            response = {"status": False, "message": "Invalid command"}
    return response
