from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Chat

from wg_assistant.handlers.commands import send_start, send_servers, send_settings
from wg_assistant.models.server import ServerModel


@pytest.mark.parametrize(
    'username,expected_text',
    [('test_user', 'Hello, test_user! 👋'), (None, 'Hello, %username%! 👋')],
    ids=['with username', 'without username'],
)
async def test_send_start(username, expected_text):
    message = MagicMock(
        spec=Message,
        answer=AsyncMock(),
        chat=MagicMock(spec=Chat, username=username),
    )

    state = MagicMock(spec=FSMContext, clear=AsyncMock())

    await send_start(message, state)

    state.clear.assert_awaited_once()
    message.answer.assert_awaited_once_with(expected_text)


@patch('wg_assistant.handlers.commands.servers_kb', return_value='mock_kb')
async def test_send_servers(mock_servers_kb):
    message = MagicMock(spec=Message, answer=AsyncMock())
    state = MagicMock(spec=FSMContext, clear=AsyncMock())

    server1 = MagicMock(spec=ServerModel)
    server1.name = 'server1'
    server2 = MagicMock(spec=ServerModel)
    server2.name = 'server2'
    servers = [server1, server2]

    await send_servers(message, servers, state)

    mock_servers_kb.assert_called_once_with(['server1', 'server2'])
    state.clear.assert_awaited_once()
    message.answer.assert_awaited_once_with('Server list:', reply_markup='mock_kb')


@pytest.mark.parametrize(
    'log_level,expected_debug_log_enabled',
    [('DEBUG', True), ('ANY_OTHER', False)],
    ids=['debug log level', 'any other log level'],
)
@patch('wg_assistant.handlers.commands.bot_settings_kb', return_value='mock_kb')
@patch('wg_assistant.handlers.commands.get_log_level')
async def test_send_settings(mock_get_log_level, mock_bot_settings_kb, log_level, expected_debug_log_enabled):
    message = MagicMock(spec=Message, answer=AsyncMock())
    mock_get_log_level.return_value = log_level

    await send_settings(message)

    mock_get_log_level.assert_called_once_with()
    mock_bot_settings_kb.assert_called_once_with(expected_debug_log_enabled)
    message.answer.assert_awaited_once_with('Bot settings:', reply_markup='mock_kb')
