import json
import sqlite3
from typing import Dict, Any, Optional, cast

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType


class SQLiteStorage(BaseStorage):
    def __init__(self, database_name: str = 'wg_assistant.db') -> None:
        self.con = sqlite3.connect(database_name)
        self.cur = self.con.cursor()

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        chat_id = key.chat_id
        if state is None:
            self.cur.execute('DELETE FROM states WHERE chat_id = ?', (chat_id,))
        else:
            self.cur.execute(
                'REPLACE INTO states (chat_id, state) VALUES (?, ?)',
                (chat_id, cast(str, state.state if isinstance(state, State) else state))
            )
        self.con.commit()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        chat_id = key.chat_id
        self.cur.execute('SELECT state FROM states WHERE chat_id = ?', (chat_id,))
        result = self.cur.fetchone()
        return cast(Optional[str], result[0]) if result else None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        chat_id = key.chat_id
        if not data:
            self.cur.execute('DELETE FROM data WHERE chat_id = ?', (chat_id,))
        else:
            self.cur.execute('REPLACE INTO data (chat_id, data) VALUES (?, ?)', (chat_id, json.dumps(data)))
        self.con.commit()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        chat_id = key.chat_id
        self.cur.execute('SELECT data FROM data WHERE chat_id = ?', (chat_id,))
        result = self.cur.fetchone()
        return json.loads(result[0]) if result else {}

    async def close(self) -> None:
        self.con.close()
