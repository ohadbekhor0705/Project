



try:
    from socket import socket
    from typing import Any
    from sqlalchemy.orm.session import Session
    from sqlalchemy import and_
    import cryptography
    import logging
    from typing import Dict, Any, overload
    import bcrypt
    import socket
    from models import User, File, SessionLocal
    from datetime import datetime
    from uuid6 import uuid7
    import os
except ModuleNotFoundError:
    raise ModuleNotFoundError("please run command on the terminal: pip install -r requirements.txt")


@overload
def getUser(login: int) -> User | None: ...

@overload
def getUser(login: Dict[str,Any]) -> User | None: ...

def username_exists(username: str, db: Session | None = None) -> bool: 
    if db is None:
        db = SessionLocal()
    result: bool = db.query(User).filter(User.username == username).first() is not None
    return result
     

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
        return [ {"filename": f.filename, "filesize": f.filesize, "modified": f.modified} for f in files]

def UploadFile(payload: dict[str, Any],client: socket.socket ,user: User) -> dict[str,Any] | None:
    """Uploading a file

    Args:
        payload (dict[str, Any]): Containing 
        client (socket.socket): client socket object
        user (User): client user information

    Returns:
        dict[str,Any]: status response from server to client
    """    


    file_size: int = payload["filesize"]
    if user.curr_storage + file_size > user.max_storage:
        return {"status": False, "message": "You dont have enough storage!"}
    received: int = 0
    file_id: str = str(uuid7())
    #file_path = f"./StorageFiles/{file_id}.bin"
    file_path = f"./StorageFiles/{payload["filename"]}"
    try:
        with open(file_path,"ab") as f:
            while received < file_size:
                chunk: bytes = client.recv(65536)
                if not chunk:
                    os.remove(file_path)
                    break
                f.write(chunk)
                received += len(chunk)
    except BrokenPipeError:
        os.remove(file_path)
        return None
    except ConnectionResetError:
        os.remove(file_path)
        return None
        
    with SessionLocal() as db:
        # attach user to the session
        user_in_session = db.merge(user)

        new_file = File(
            file_id=file_id,
            filename=payload["filename"],
            filesize=payload["filesize"],
            modified=int(datetime.now().timestamp()),
            user_id=user.user_id
        )

        user_in_session.curr_storage += new_file.filesize
        user_in_session.files.append(new_file)
        db.commit()
    return {"status": True, "message": payload["filename"]+" Uploaded!"}


def handle_client_request(payload: dict[str, Any], client: socket.socket, user: User) -> dict[str, Any] | None:
    response: dict[str, Any]  | None= {}
    params: tuple[dict[str, Any], socket.socket, User] = (payload, client, user)
    match payload["cmd"]:
        case "upload":
            response = UploadFile(*params)
        case _:
            response = {"status": False, "message": "Invalid command"}
    return response
