import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import TelegramObject, User, Message, CallbackQuery, Update

from wg_assistant.modules.middlewares import LoggingMiddleware, AuthCheckMiddleware


async def test_logging_middleware(caplog):
    middleware = LoggingMiddleware()
    handler = AsyncMock(return_value='OK')

    event = MagicMock(spec=TelegramObject)
    event.model_dump.return_value = {'update_id': 123}

    data = {}

    with caplog.at_level(logging.DEBUG):
        result = await middleware(handler, event, data)

    assert "Incoming update: {'update_id': 123}" in caplog.text
    assert result == 'OK'
    event.model_dump.assert_called_once_with(exclude_none=True)
    handler.assert_awaited_once_with(event, data)


@pytest.mark.parametrize(
    'user_id,admins,message_exists,callback_exists,expected_action',
    [
        (123, [123, 456], True, True, 'allow'),
        (999, [123, 456], True, False, 'message_answer'),
        (999, [123, 456], False, True, 'callback_answer'),
    ],
    ids=['allow', 'deny with message answer', 'deny with callback answer']
)
async def test_auth_check_middleware(user_id, admins, message_exists, callback_exists, expected_action):
    middleware = AuthCheckMiddleware()
    handler = AsyncMock(return_value='OK')
    event = MagicMock(spec=Update)

    mock_user = User(id=user_id, is_bot=False, first_name='Test')
    data = {'event_from_user': mock_user, 'admins': admins}

    event.message = None
    event.callback_query = None

    if message_exists:
        event.message = AsyncMock(spec=Message)
        event.message.answer = AsyncMock()
    if callback_exists:
        event.callback_query = AsyncMock(spec=CallbackQuery)
        event.callback_query.answer = AsyncMock()

    result = await middleware(handler, event, data)

    if expected_action == 'allow':
        handler.assert_awaited_once_with(event, data)
        assert result == 'OK'

        if message_exists:
            event.message.answer.assert_not_called()
        if callback_exists:
            event.callback_query.answer.assert_not_called()

    elif expected_action == 'message_answer':
        event.message.answer.assert_awaited_once_with("I don't know you ⚠")
        handler.assert_not_awaited()

        if callback_exists:
            event.callback_query.answer.assert_not_called()

    elif expected_action == 'callback_answer':
        event.callback_query.answer.assert_awaited_once_with('You have been blocked 🛑', show_alert=True)
        handler.assert_not_awaited()

        if message_exists:
            event.message.answer.assert_not_called()
