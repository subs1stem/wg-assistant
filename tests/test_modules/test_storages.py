import pytest
from aiogram.fsm.storage.base import StorageKey

from wg_assistant.modules.storages import SQLiteStorage


@pytest.fixture
def storage(tmp_path, monkeypatch) -> SQLiteStorage:
    test_db = tmp_path / 'test_fsm.sqlite'
    monkeypatch.setattr('wg_assistant.modules.storages.DB_FILE', str(test_db))

    storage = SQLiteStorage()
    con = storage.con
    cur = storage.cur

    cur.executescript(
        '''
        CREATE TABLE states
        (
            chat_id INTEGER PRIMARY KEY,
            state   TEXT
        );
        CREATE TABLE data
        (
            chat_id INTEGER PRIMARY KEY,
            data    TEXT
        );
        '''
    )

    con.commit()
    return storage


def make_key() -> StorageKey:
    return StorageKey(bot_id=123, chat_id=456, user_id=789)


async def test_set_and_get_state(storage: SQLiteStorage):
    key = make_key()
    await storage.set_state(key, 'test_state')
    state = await storage.get_state(key)
    assert state == 'test_state'


async def test_delete_state(storage: SQLiteStorage):
    key = make_key()
    await storage.set_state(key, 'test_state')
    await storage.set_state(key, None)
    assert await storage.get_state(key) is None


async def test_set_and_get_data(storage: SQLiteStorage):
    key = make_key()
    sample_data = {'data1': 1, 'data2': 'abc'}
    await storage.set_data(key, sample_data)
    data = await storage.get_data(key)
    assert data == sample_data


async def test_delete_data(storage: SQLiteStorage):
    key = make_key()
    await storage.set_data(key, {'data1': 1})
    await storage.set_data(key, {})
    data = await storage.get_data(key)
    assert data == {}


async def test_close_does_not_raise(storage: SQLiteStorage):
    await storage.close()
