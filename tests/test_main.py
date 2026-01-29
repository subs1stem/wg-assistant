from unittest.mock import patch, AsyncMock, Mock

import pytest
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from pydantic import ValidationError

from wg_assistant.handlers import commands, callbacks, messages, errors
from wg_assistant.main import main
from wg_assistant.modules.middlewares import LoggingMiddleware, ServerCreateMiddleware, AuthCheckMiddleware


@patch('wg_assistant.main.SQLiteStorage')
@patch('wg_assistant.main.get_bot_token', return_value='token')
@patch('wg_assistant.main.get_bot_admins', return_value=[1, 2])
@patch('wg_assistant.main.get_servers', return_value={'server': 1})
@patch('wg_assistant.main.Bot', return_value=AsyncMock())
@patch('wg_assistant.main.Dispatcher')
async def test_main_success(
        mock_dispatcher,
        mock_bot,
        mock_get_servers,
        mock_get_bot_admins,
        mock_get_bot_token,
        mock_storage,
):
    dp = Mock()
    dp.update = Mock()
    dp.update.middleware = Mock()
    dp.include_routers = Mock()
    dp.start_polling = AsyncMock()
    mock_dispatcher.return_value = dp

    bot = mock_bot.return_value

    await main()

    mock_get_bot_token.assert_called_once_with()
    mock_get_bot_admins.assert_called_once_with()
    mock_get_servers.assert_called_once_with()

    mock_bot.assert_called_once_with('token', default=DefaultBotProperties(parse_mode='HTML'))
    mock_dispatcher.assert_called_once_with(storage=mock_storage.return_value, admins=[1, 2], servers={'server': 1})

    calls = [call.args[0] for call in dp.update.middleware.mock_calls]
    assert any(isinstance(m, LoggingMiddleware) for m in calls)
    assert any(isinstance(m, AuthCheckMiddleware) for m in calls)
    assert any(isinstance(m, ServerCreateMiddleware) for m in calls)

    dp.include_routers.assert_called_once_with(
        commands.router,
        callbacks.router,
        messages.router,
        errors.router,
    )

    bot.set_my_commands.assert_awaited_once_with([
        BotCommand(command='start', description='start'),
        BotCommand(command='servers', description='server list'),
        BotCommand(command='settings', description='bot settings'),
    ])

    bot.delete_webhook.assert_awaited_once_with(drop_pending_updates=True)
    dp.start_polling.assert_awaited_once_with(bot)


@patch('wg_assistant.main.logging')
@patch('wg_assistant.main.sys.exit', side_effect=SystemExit)
async def test_main_runtime_error(mock_exit, mock_logging):
    with patch('wg_assistant.main.get_bot_token', side_effect=RuntimeError('no token')):
        with pytest.raises(SystemExit):
            await main()

    mock_logging.critical.assert_called_once_with('Error loading environment variables: no token')
    mock_exit.assert_called_once_with(1)


@patch('wg_assistant.main.logging')
@patch('wg_assistant.main.sys.exit', side_effect=SystemExit)
async def test_main_validation_error(mock_exit, mock_logging):
    validation_error = ValidationError('', [])

    with patch('wg_assistant.main.get_servers', side_effect=validation_error):
        with pytest.raises(SystemExit):
            await main()

    mock_logging.critical.assert_called_once_with('Validation error while loading servers: []')
    mock_exit.assert_called_once_with(1)
