import sqlite3
from pathlib import Path

from wg_assistant.db import database


def test_init_db_creates_tables(tmp_path: Path, monkeypatch):
    test_db = tmp_path / 'test.sqlite'
    monkeypatch.setattr(database, 'DB_FILE', str(test_db))

    database.init_db()

    con = sqlite3.connect(test_db)
    cur = con.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert 'states' in tables
    assert 'data' in tables
    assert 'settings' in tables

    cur.execute("SELECT value FROM settings WHERE key = 'log_level'")
    value = cur.fetchone()
    assert value[0] == 'INFO'
    con.close()


def test_get_and_set_log_level(tmp_path: Path, monkeypatch):
    test_db = tmp_path / 'test.sqlite'
    monkeypatch.setattr(database, 'DB_FILE', str(test_db))

    database.init_db()
    assert database.get_log_level() == 'INFO'

    database.set_log_level('DEBUG')
    assert database.get_log_level() == 'DEBUG'


def test_execute_query_insert_and_select(tmp_path: Path, monkeypatch):
    test_db = tmp_path / 'test.sqlite'
    monkeypatch.setattr(database, 'DB_FILE', str(test_db))

    database.init_db()
    insert_query = 'INSERT OR REPLACE INTO states (chat_id, state) VALUES (?, ?)'
    select_query = 'SELECT state FROM states WHERE chat_id = ?'

    database.execute_query(insert_query, (12345, 'new_state'))
    result = database.execute_query(select_query, (12345,))
    assert result[0][0] == 'new_state'
