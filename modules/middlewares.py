from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from data.servers import ServersFile


class ServerConnectionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if data['raw_state'] == 'CurrentServer:waiting_for_server':
            server_name = event.data.split(':')[1]
            server_data = ServersFile().get_server_by_name(server_name)
            await data['state'].set_data({'server_name': server_name} | server_data)

        return await handler(event, data)
