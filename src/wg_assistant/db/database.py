import sqlite3
from typing import List, Tuple, Optional


class Database:
    """A class to manage SQLite database operations."""

    def __init__(self, database_name: str = 'wg_assistant.db') -> None:
        """Initializes the Database instance.

        Args:
            database_name (str): The name of the SQLite database file. Defaults to 'wg_assistant.db'.

        Returns:
            None
        """
        self.database_name: str = database_name

    def execute_query(self, query: str, parameters: Tuple = ()) -> List[Tuple]:
        """Executes an SQL query on the database.

        Args:
            query (str): The SQL query to execute.
            parameters (Tuple): Optional parameters for the query. Defaults to an empty tuple.

        Returns:
            List[Tuple]: A list of tuples containing the query results.
        """
        with sqlite3.connect(self.database_name) as con:
            cur = con.cursor()
            cur.execute(query, parameters)
            return cur.fetchall()

    def init_db(self) -> None:
        """Initializes the database schema if it doesn't exist.

        Returns:
            None
        """
        sql_queries: str = '''
            CREATE TABLE IF NOT EXISTS states (chat_id INTEGER PRIMARY KEY, state TEXT);
            CREATE TABLE IF NOT EXISTS data (chat_id INTEGER PRIMARY KEY, data TEXT);
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
            INSERT OR IGNORE INTO settings (key, value) VALUES ('log_level', 'INFO');
        '''

        with sqlite3.connect(self.database_name) as con:
            cur = con.cursor()
            cur.executescript(sql_queries)

    def get_log_level(self) -> Optional[str]:
        """Retrieves the current log level from the settings table.

        Returns:
            Optional[str]: The current log level if found, else None.
        """
        query: str = "SELECT value FROM settings WHERE key = 'log_level'"
        result: List[Tuple] = self.execute_query(query)
        return result[0][0] if result else None

    def set_log_level(self, log_level: str) -> None:
        """Updates the log level in the settings table.

        Args:
            log_level (str): The new log level.
        """
        query: str = "UPDATE settings SET value = ? WHERE key = 'log_level'"
        self.execute_query(query, (log_level,))
