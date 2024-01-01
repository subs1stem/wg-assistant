from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery

from servers.server_factory import ServerFactory


class AuthCheckMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user_id = data.get('event_from_user').id
        admins = data.get('admins')

        if user_id not in admins:
            if event.message is None:
                return await event.callback_query.answer('Вы были заблокированы 🛑', show_alert=True)

            return await event.message.answer('Я Вас не знаю ⚠')

        return await handler(event, data)


class ServerCreateMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.data = {}
        self.data_updated = False
        self.selected_server_name = None

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any],
    ) -> Any:
        if not self.data_updated:
            self.data = data
            self.data_updated = True

        if event.data.startswith('server:'):
            servers = self.data.get('servers')
            server_name = event.data.split(':')[1] or self.selected_server_name
            server_data = servers.get(server_name)

            self.selected_server_name = server_name
            server = ServerFactory.create_server_instance(server_name, server_data)

            self.data.update(server_name=server_name, server=server)

        return await handler(event, self.data)
