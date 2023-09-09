from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from data.servers import ServersFile
from wireguard.ssh import SSH


class ServerConnectionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if event.data.startswith('server:'):
            server_name = event.data.split(':')[1]
            server_data = ServersFile().get_server_by_name(server_name)

            try:
                server = SSH(**server_data)
                await data['state'].set_data({'server_name': server_name, 'server': server})
                return await handler(event, data)
            except ConnectionError:
                await event.answer(f'Не удалось подключиться к серверу "{server_name}" ⚠️', show_alert=True)
        else:
            return await handler(event, data)
