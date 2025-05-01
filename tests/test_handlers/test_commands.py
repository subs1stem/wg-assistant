from unittest.mock import AsyncMock, MagicMock

import pytest

from wg_assistant.handlers.commands import send_start


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'username, expected_text',
    [
        ('test_user', 'Hello, test_user! 👋'),
        (None, 'Hello, %username%! 👋'),
    ],
)
async def test_send_start(username, expected_text):
    message = MagicMock()
    message.chat.username = username
    message.answer = AsyncMock()

    state = MagicMock()
    state.clear = AsyncMock()

    await send_start(message, state)

    state.clear.assert_awaited_once()
    message.answer.assert_awaited_once_with(expected_text)


@pytest.mark.asyncio
async def test_send_servers():
    pass


@pytest.mark.asyncio
async def test_send_settings():
    pass
