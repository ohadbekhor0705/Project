


try:
    from sqlalchemy.orm.session import Session
    from sqlalchemy import and_
    import cryptography
    import logging
    from typing import Dict, Any, overload
    import bcrypt
    import socket
    from models import User, File, SessionLocal
except ModuleNotFoundError:
    raise ModuleNotFoundError("please run command on the terminal: pip install -r requirements.txt")
# prepare Log file
LOG_FILE = 'LOG.log'
logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

def write_to_log(msg) -> None:
    #logging.info(msg)
    print(msg)


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
        print(user)

        # Handle login password
        if user is not None and isinstance(login, dict):
            password_correct = bcrypt.checkpw(
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
        
    
def Insert(user: Dict[str,Any]) -> Dict:
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
        write_to_log(f"[protocol -> DataBase] Exception in Insert(): {e}")
        return {
          "status": False,
          "message": f"{e}"
          }
    finally:
        db.close()      