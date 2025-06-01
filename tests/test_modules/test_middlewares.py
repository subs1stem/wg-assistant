import logging
from unittest.mock import AsyncMock, MagicMock

from aiogram.types import TelegramObject

from wg_assistant.modules.middlewares import LoggingMiddleware


async def test_logging_middleware_logs_event(caplog):
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
