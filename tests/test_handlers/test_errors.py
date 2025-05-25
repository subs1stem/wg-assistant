from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ErrorEvent

from wg_assistant.handlers.errors import handle_connection_error, handle_message_is_not_modified, handle_error


@patch('wg_assistant.handlers.errors.logging')
async def test_handle_connection_error(mock_logging):
    callback = MagicMock(spec=CallbackQuery, answer=AsyncMock())
    state = MagicMock(spec=FSMContext, clear=AsyncMock())

    await handle_connection_error(None, callback, state)

    state.clear.assert_awaited_once_with()
    callback.answer.assert_awaited_once_with('Server connection error ⚠️', show_alert=True)
    mock_logging.info.assert_called_once_with('Error connecting to the server, state cleared')


@pytest.mark.parametrize(
    'exception_text,is_not_modified',
    [
        (
                'Telegram server says - Bad Request: message is not modified: specified new message content '
                'and reply markup are exactly the same as a current content and reply markup of the message',
                True,
        ),
        ('any another exception', False),
    ],
    ids=['is not modified', 'any other'],
)
@patch('wg_assistant.handlers.errors.handle_error')
@patch('wg_assistant.handlers.errors.logging')
async def test_handle_message_is_not_modified(mock_logging, mock_handle_error, exception_text, is_not_modified):
    event = MagicMock(spec=ErrorEvent, exception=exception_text)
    callback = MagicMock(spec=CallbackQuery)

    await handle_message_is_not_modified(event, callback)

    if is_not_modified:
        mock_logging.debug.assert_called_once_with(f'Ignored error: "{exception_text}"')
        mock_handle_error.assert_not_awaited()
    else:
        mock_handle_error.assert_awaited_once_with(event, callback)
        mock_logging.debug.assert_not_called()


@patch('wg_assistant.handlers.errors.logging')
async def test_handle_error(mock_logging):
    event = MagicMock(spec=ErrorEvent, exception='mock_exception')
    callback = MagicMock(spec=CallbackQuery, answer=AsyncMock())

    await handle_error(event, callback)

    callback.answer.assert_awaited_once_with('Unknown error ⚠️', show_alert=True)
    mock_logging.error.assert_called_once_with('mock_exception')
