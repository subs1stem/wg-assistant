import sqlite3
from typing import Dict, Any, Optional, cast

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType


class SQLiteStorage(BaseStorage):
    def __init__(self, database_name: str = 'wg_assistant.db') -> None:
        self.database_name = database_name
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS states (
                chat_id INTEGER PRIMARY KEY,
                state TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS data (
                chat_id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
        self.connection.commit()

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        chat_id = key.chat_id
        if state is None:
            self.cursor.execute('DELETE FROM states WHERE chat_id = ?', (chat_id,))
        else:
            self.cursor.execute(
                'REPLACE INTO states (chat_id, state) VALUES (?, ?)',
                (chat_id, cast(str, state.state if isinstance(state, State) else state))
            )
        self.connection.commit()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        chat_id = key.chat_id
        self.cursor.execute('SELECT state FROM states WHERE chat_id = ?', (chat_id,))
        result = self.cursor.fetchone()
        return cast(Optional[str], result[0]) if result else None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        chat_id = key.chat_id
        if not data:
            self.cursor.execute('DELETE FROM data WHERE chat_id = ?', (chat_id,))
        else:
            self.cursor.execute('REPLACE INTO data (chat_id, data) VALUES (?, ?)', (chat_id, data))
        self.connection.commit()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        chat_id = key.chat_id
        self.cursor.execute('SELECT data FROM data WHERE chat_id = ?', (chat_id,))
        result = self.cursor.fetchone()
        return eval(result[0]) if result else {}

    async def close(self) -> None:
        self.connection.close()
