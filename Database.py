from protocol import write_to_log
import sqlite3
import bcrypt
from typing import Dict, Tuple, Any, overload
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
    run_query(q: str, args: Dict[str,Any] = None) -> list[Any] | None
        Execute an SQL query with optional parameters and return results.

    Notes
    -----
    - Each method opens its own sqlite3 connection to self.path
    - Uses parameterized queries to prevent SQL injection
    - Exceptions are logged via write_to_log()
    - Passwords should be hashed before storage (e.g. using bcrypt)
    """
    

    def __init__(self, path: str):
            self.path: str = path
            with sqlite3.connect(path) as conn:
            # create tables if not exist
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

    #         return False
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
            with sqlite3.connect(self.path) as conn:
                cur = conn.cursor()
                result: Dict[str,Any] | None = None
                if isinstance(login, int): # if we got the user id then run a query based on the user id
                    result = cur.execute("SELECT * FROM users WHERE user_id = ?;",(login,)).fetchone()
                    print(len(result))
                if isinstance(login, Dict):
                    result = cur.execute("SELECT * FROM users WHERE username = :username ",login).fetchone()
                write_to_log(f"[getUser()] {result}")
                if result is None:
                    print("?")
                    return None
                if isinstance(login,Dict) and not bcrypt.checkpw(login["password"].encode(), result[2].encode()):
                    return None
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

    def run_query(self, q: str, args:Dict[str,Any] = None) -> list[Any] | None:
        """
        Execute a SQL query against the SQLite database referenced by self.path.
        Args:
            q (str): SQL statement to execute. Can be a SELECT (returns rows) or a modification statement (INSERT/UPDATE/DELETE).
            args (Dict[str, Any], optional): Parameters to bind to the query. For named placeholders use a dict (e.g. {"id": value}); for positional placeholders use a sequence. Defaults to None.
        Returns:
            list[tuple] | None: For queries that return rows (e.g., SELECT) returns a list of rows (each row typically a tuple). For non-query statements that modify the database, returns None after committing the transaction.
        Raises:
            sqlite3.Error: If a database error occurs during execution.
        """
        with sqlite3.connect(self.path) as conn:
            if args:
                curs = conn.execute(q,args)
            else:
                conn.execute(q)
            curs.execute()
            conn.commit()
        """Return files for the user."""
        try:
            with sqlite3.connect(self.path) as conn:
                cur = conn.cursor()
                files = cur.execute("SELECT * FROM FILES WHERE user_id =:id",{"id":args}).fetchall()

                return files
        except Exception as e:
            # Log the exception that occurred in retrieveFiles() including the exception message
            write_to_log(f"[protocol -> DataBase] Exception on retrieveFiles(): {e}")  # write to log and print the error

db: DataBase = DataBase("./Database.db")
