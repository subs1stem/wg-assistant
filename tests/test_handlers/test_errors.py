from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from wg_assistant.handlers.errors import handle_connection_error


@patch('wg_assistant.handlers.errors.logging')
async def test_handle_connection_error(mock_logging):
    callback = MagicMock(spec=CallbackQuery, answer=AsyncMock())
    state = MagicMock(spec=FSMContext, clear=AsyncMock())

    await handle_connection_error(None, callback, state)

    state.clear.assert_awaited_once_with()
    callback.answer.assert_awaited_once_with('Server connection error ⚠️', show_alert=True)
    mock_logging.info.assert_called_once_with('Error connecting to the server, state cleared')


@pytest.mark.skip
async def test_handle_message_is_not_modified():
    pass


@pytest.mark.skip
async def test_handle_error():
    pass
