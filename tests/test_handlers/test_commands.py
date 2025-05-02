from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from wg_assistant.handlers.commands import send_start, send_servers


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
async def test_send_servers():
    message = MagicMock(answer=AsyncMock())
    state = MagicMock(clear=AsyncMock())

    server1 = MagicMock()
    server1.name = 'server1'
    server2 = MagicMock()
    server2.name = 'server2'
    servers = [server1, server2]

    with patch('wg_assistant.handlers.commands.servers_kb', return_value='MOCK_KB') as kb_mock:
        await send_servers(message, servers, state)

        kb_mock.assert_called_once_with(['server1', 'server2'])
        state.clear.assert_awaited_once()
        message.answer.assert_awaited_once_with('Server list:', reply_markup='MOCK_KB')


@pytest.mark.asyncio
async def test_send_settings():
    pass
