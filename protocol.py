import cryptography
import logging
import sqlite3
from typing import Dict, Any
import bcrypt
# prepare Log file
LOG_FILE = 'LOG.log'
logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

def write_to_log(msg) -> None:
    logging.info(msg)
    print(msg)

class DataBase: 

    """DataBase — lightweight SQLite helper for users and files.

    Methods
    -------
    __init__(path_url)
        Initialize the database at path_url and create required tables if they do not exist.
    is_exists(user: Dict[str, Any]) -> bool
        Check whether a record exists matching provided 'username' and 'password' (expects a dict with keys
        used in the parameterized query).
    username_exists(username: str) -> bool
        Return True if the given username already exists in the users table.
    Insert(user: Dict[str, Any]) -> Union[dict, tuple, bool]
        Insert a new user. On success the implementation returns a dict like
        {'status': True, 'response': 'Welcome...'}; on failure it may return (False, "message") or False.
    run_query(q: str, args: Dict[str, Any] = None)
        Execute an arbitrary SQL statement with optional parameters and commit the transaction.
        Intended to be used for non-SELECT statements; callers should adapt return handling as needed.
    retrieveFiles(id: int) -> List[Tuple]
        Return files belonging to the specified user id (rows from the files table).

    Notes
    -----
    - Each method opens its own sqlite3 connection to self.url (connections are not shared).
    - Always use parameterized queries (placeholders) to avoid SQL injection.
    - Exceptions are logged via write_to_log() for diagnostics.
    - Password handling: store and verify salted hashes (e.g. bcrypt); this class assumes callers
      perform proper hashing/verification rather than storing plain text.
    """
    

    def __init__(self, path_url):
            self.url = path_url
            with sqlite3.connect(path_url) as conn:
            # create tables if not exist
                cur = conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS users(
                        user_id INTEGER PRIMARY KEY,
                        username CHAR(255),
                        password_hash BLOB,
                        max_storage INT DEFAULT 100000000,
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

    def is_exists(self, user: Dict[str, Any] ) -> bool:
        try:
            with sqlite3.connect(self.url) as conn:
                cursor = conn.cursor()
                return cursor.execute(
                     "SELECT * FROM users"
                     "WHERE username = :username" 
                     " AND password = :password ",user
                    ).fetchone() is not None
        except Exception as e:
            write_to_log(f"[protocol -> DataBase] Exception in is_exist(): {e}")
    
            return False
    def username_exists(self, username: str) -> bool:
        with sqlite3.connect(self.url) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None
    
    def Insert(self, user: Dict[str,Any]) -> Dict:
        """Insert a new user into the database.
        
        Args:
            user (Dict[str, Any]): A dictionary containing 'username' and 'password' keys.
        
        Returns:
            Dict: A dictionary with 'status' indicating success and 'response' message.
        """
        try:
            if self.username_exists(user):
                return False, "This username is already taken"
            with sqlite3.connect(self.url) as conn:
                cur = conn.execute("INSERT INTO users (username, password) VALUES (:username, :password)", user)
                cur.execute()
                conn.commit()
            return {
                "status": True,
                "response": "Welcome to skyVault!"
            }
        except Exception as e:
            write_to_log(f"[protocol -> DataBase] Exception in Insert(): {e}")
            return False

    def run_query(self, q: str, args:Dict[str,Any] = None):
        """
        Execute a SQL query against the SQLite database referenced by self.url.
        Args:
            q (str): SQL statement to execute. Can be a SELECT (returns rows) or a modification statement (INSERT/UPDATE/DELETE).
            args (Dict[str, Any], optional): Parameters to bind to the query. For named placeholders use a dict (e.g. {"id": value}); for positional placeholders use a sequence. Defaults to None.
        Returns:
            list[tuple] | None: For queries that return rows (e.g., SELECT) returns a list of rows (each row typically a tuple). For non-query statements that modify the database, returns None after committing the transaction.
        Raises:
            sqlite3.Error: If a database error occurs during execution.
        """
        with sqlite3.connect(self.url) as conn:
            if args:
                curs = conn.execute(q,args)
            else:
                conn.execute(q)
            curs.execute()
            conn.commit()
        """Return files for the user."""
        try:
            with sqlite3.connect(self.url) as conn:
                cur = conn.cursor()
                files = cur.execute("SELECT * FROM FILES WHERE uid =:id",{"id":id}).fetchall()

                return files
        except Exception as e:
            # Log the exception that occurred in retrieveFiles() including the exception message
            write_to_log(f"[protocol -> DataBase] Exception on retrieveFiles(): {e}")  # write to log and print the error

db: DataBase = DataBase("./Database.db")
