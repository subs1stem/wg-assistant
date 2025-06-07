import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import TelegramObject, User, Message, CallbackQuery, Update

from wg_assistant.models.servers import ServerModel
from wg_assistant.modules.middlewares import LoggingMiddleware, AuthCheckMiddleware, ServerCreateMiddleware
from wg_assistant.servers.server_factory import ServerFactory


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


@pytest.mark.parametrize(
    'text,callback_data,expect_server_setup',
    [
        ('/start', None, False),
        (None, 'server:my-server', True),
        (None, 'server:', False),
        (None, None, False),
    ],
    ids=['command', 'valid callback', 'empty server callback', 'no msg or callback']
)
async def test_server_create_middleware(text, callback_data, expect_server_setup):
    middleware = ServerCreateMiddleware()
    handler = AsyncMock(return_value='OK')

    event = MagicMock(spec=Update)
    event.message = AsyncMock(spec=Message) if text else None
    if event.message:
        event.message.text = text

    event.callback_query = AsyncMock(spec=CallbackQuery) if callback_data else None
    if event.callback_query:
        event.callback_query.data = callback_data

    server_model = ServerModel(name='my-server')
    servers = [server_model]

    state = AsyncMock()
    state_data = {'server_model': server_model.model_dump_json()} if expect_server_setup else {}
    state.get_data.return_value = state_data

    data = {
        'state': state,
        'servers': servers
    }

    result = await middleware(handler, event, data)

    assert result == 'OK'

    if text and text.startswith('/'):
        state.set_data.assert_not_called()
        state.get_data.assert_not_called()

    elif callback_data and callback_data.startswith('server:') and callback_data != 'server:':
        state.set_data.assert_awaited_once()
        state.get_data.assert_awaited_once()
        assert 'server_name' in data
        assert 'server' in data
        assert data['server_name'] == 'my-server'
        assert isinstance(data['server'], ServerFactory.create_server_instance(server_model).__class__)

    else:
        state.set_data.assert_not_called()
        state.get_data.assert_awaited_once()
        assert 'server_name' not in data
        assert 'server' not in data

    handler.assert_awaited_once_with(event, data)
