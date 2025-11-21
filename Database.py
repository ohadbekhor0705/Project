try:
    from protocol import write_to_log
    import sqlite3
    import bcrypt
    from typing import Dict, Tuple, Any, overload
except ModuleNotFoundError:
    print("please run command on the terminal: pip install -r requirements.txt")

class DataBase: 

    """DataBase — lightweight SQLite helper for users and files.

    Methods
    -------
    __init__(path)
        Initialize the database at path and create required tables if they do not exist.
    username_exists(username: str) -> bool
        Return True if the given username already exists in the users table.
    getUser(user_id: int) -> Dict[str,Any] | None
        Retrieve user information by user ID. Returns None if user not found.
    Insert(user: Dict[str,Any]) -> Dict
        Insert a new user. Returns dict with status and response message.
    run_query(q: str,args: Tuple[str,Ant]) -> Dict
        Run an sql query with given arguments. Returns result status and cursor.

    Notes
    -----
    - Each method opens its own sqlite3 connection to self.path
    - Uses parameterized queries to prevent SQL injection
    - Exceptions are logged via write_to_log()
    - Passwords should be hashed before storage (e.g. using bcrypt)
    """
    

    def __init__(self, path: str):
            self.path: str = path
            # create tables if not exist
            with sqlite3.connect(self.path) as conn:
                cur = conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS users(
                        user_id INTEGER PRIMARY KEY,
                        username CHAR(255),
                        password_hash TEXT,
                        max_storage INT DEFAULT 1073741824,
                        curr_storage INT DEFAULT 0,
                        tries INT DEFAULT 0,
                        disabled BOOLEAN DEFAULT 0
                    );
                    CREATE TABLE IF NOT EXISTS files(
                    file_id CHAR(255) PRIMARY KEY,
                    filename CHAR(255),
                    filesize INTEGER,
                    modified INT,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                    );
                    """
                )

    def username_exists(self, username: str) -> bool:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None
    @overload
    def getUser(self, login: int) -> Dict[str,Any] | None: ...

    @overload
    def getUser(self, login: Dict[str,Any]) -> Dict[str,Any] | None: ...

    def getUser(self, login: Dict[str,Any] | int) -> Dict[str,Any] | None:
        """
        Retrieves a user record from the database based on either user ID or login credentials.
        Args:
            login (Dict[str, Any] | int): The login information. Can be either:
                - A dictionary with 'username' and 'password_hash' keys for authentication.
                - An integer representing the user ID.
        Returns:
            Dict[str, Any] | None: A dictionary containing user information if found, otherwise None.
        """
        
        try:
            result: Dict[str,Any] | None = None
            with sqlite3.connect(self.path) as conn:
                cur: sqlite3.Cursor = conn.cursor()
                if isinstance(login, int): # if we got the user id then run a query based on the user id
                    result = cur.execute("SELECT * FROM users WHERE user_id = ? and disabled = 0;",(login,)).fetchone()
                if isinstance(login, Dict):
                    result = cur.execute("SELECT * FROM users WHERE username = :username and disabled = 0",login).fetchone()
            write_to_log(f"[getUser()] {result}")
            if result is None:
                return None
            if isinstance(login,Dict) and not bcrypt.checkpw(login["password"].encode(), result[2].encode()): # check if the hash of their password is the same:
                if result[5] == 3: # if someone tried 3 times to enter the correct password then disable this user:
                    self.run_query("UPDATE users set disabled = 1 WHERE user_id = ?",(result[0],))
                else: # if The username is but the password isn't:
                    self.run_query("UPDATE users SET tries = ? WHERE user_id = ?",(result[5]+1,result[0]))
            else:
                response= {
                        "user_id": result[0],
                        "username": result[1],
                        "password_hash": result[2],
                        "max_storage": result[3],
                        "curr_storage": result[4],
                        "tries": result[5],
                        "disabled": result[6],
                }
                return response
        except Exception as e:
                write_to_log(f"[protocol -> DataBase] Exception in getUser(): {e}")
                return None
    def Insert(self, user: Dict[str,Any]) -> Dict:
        """Insert a new user into the database.
        
        Args:
            user (Dict[str, Any]): A dictionary containing 'username' and 'password' keys.
        
        Returns:
            Dict: A dictionary with 'status' indicating success and 'response' message.
        """
        try:
            user["password"] = user["password"].decode("utf-8")
            if self.username_exists(user["username"]):
                return {"status":False, "message": "This username is already taken"}
            with sqlite3.connect(self.path) as conn:
                write_to_log(f"{user['username']=}")
                write_to_log(f"{user['password']=}")
                cur = conn.execute("INSERT INTO users (username, password_hash) VALUES (:username, :password)", user)
            response= {
                "status": True,
                "message": "Welcome to skyVault!"
            }
            write_to_log(f"{response=}")
            return response
        except Exception as e:
            write_to_log(f"[protocol -> DataBase] Exception in Insert(): {e}")
            return {
                "status": False,
                "message": f"{e}"
            }
    def run_query(self,q: str,args:Tuple[Any] | None = None) -> Tuple[bool, sqlite3.Cursor]:
        """Running custom SQL Query with parameters to prevent SQL Injection

        Args:
            q (str): SQL Query
            args (Tuple[Any] | None, optional): SQL Arguments. Defaults to None.

        Returns:
            Tuple[bool, sqlite3.Cursor]: a tuple contains the result status and cursor to fetch data.
        """
        try:
            with sqlite3.connect(self.path) as conn:
                cur = conn.cursor()
                if args:
                    return True, cur.execute(q,args)
                else:
                    return True, cur.execute(q)

        except Exception as e:
            return False, None

    def retrieve_file(self, file_id: str) -> Tuple[Dict[str, Any],bytes] | None:
        ok, cur = self.run_query("SELECT 1 FROM files WHERE file_id = ?",(file_id,))
        if ok:
            result = cur.fetchone()[0]
            return True, {
                "file_id": result[0],
                "filename": result[1],
                "filesize": result[2],
                "modified": result[3],
                "user_id": result[4]
            }
        return None

db: DataBase = DataBase("./Database.db")
