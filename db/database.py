import sqlite3


def init_db(database_name: str = 'wg_assistant.db') -> None:
    sql_queries = '''
        CREATE TABLE IF NOT EXISTS states (chat_id INTEGER PRIMARY KEY, state TEXT);
        CREATE TABLE IF NOT EXISTS data (chat_id INTEGER PRIMARY KEY, data TEXT);
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
        INSERT OR IGNORE INTO settings (key, value) VALUES ('log_level', 'INFO');
    '''

    with sqlite3.connect(database_name) as con:
        cur = con.cursor()
        cur.executescript(sql_queries)


def get_log_level(database_name: str = 'wg_assistant.db') -> str:
    with sqlite3.connect(database_name) as con:
        cur = con.cursor()
        cur.execute('SELECT value FROM settings WHERE key = "log_level"')
        return cur.fetchone()[0]
