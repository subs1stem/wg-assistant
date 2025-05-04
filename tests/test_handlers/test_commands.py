from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from wg_assistant.handlers.commands import send_start, send_servers, send_settings


@pytest.mark.asyncio
@pytest.mark.parametrize('username,expected_text', [
    ('test_user', 'Hello, test_user! 👋'),
    (None, 'Hello, %username%! 👋'),
])
async def test_send_start(username, expected_text):
    message = MagicMock(answer=AsyncMock(), chat=MagicMock(username=username))
    state = MagicMock(clear=AsyncMock())

    await send_start(message, state)

    state.clear.assert_awaited_once()
    message.answer.assert_awaited_once_with(expected_text)


@pytest.mark.asyncio
@patch('wg_assistant.handlers.commands.servers_kb', return_value='mock_kb')
async def test_send_servers(mock_servers_kb):
    message = MagicMock(answer=AsyncMock())
    state = MagicMock(clear=AsyncMock())

    server1 = MagicMock()
    server1.name = 'server1'
    server2 = MagicMock()
    server2.name = 'server2'
    servers = [server1, server2]

    await send_servers(message, servers, state)

    mock_servers_kb.assert_called_once_with(['server1', 'server2'])
    state.clear.assert_awaited_once()
    message.answer.assert_awaited_once_with('Server list:', reply_markup='mock_kb')


@pytest.mark.asyncio
@pytest.mark.parametrize('log_level,expected_debug_log_enabled', [
    ('DEBUG', True),
    ('ANY_OTHER', False),
])
@patch('wg_assistant.handlers.commands.bot_settings_kb', return_value='mock_kb')
@patch('wg_assistant.handlers.commands.get_log_level')
async def test_send_settings(mock_get_log_level, mock_bot_settings_kb, log_level, expected_debug_log_enabled):
    message = MagicMock(answer=AsyncMock())
    mock_get_log_level.return_value = log_level

    await send_settings(message)

    mock_get_log_level.assert_called_once_with()
    mock_bot_settings_kb.assert_called_once_with(expected_debug_log_enabled)
    message.answer.assert_awaited_once_with('Bot settings:', reply_markup='mock_kb')
