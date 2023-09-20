from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery

from data.servers import ServersFile
from wireguard.ssh import SSH


class AuthCheckMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user_id = data.get('event_from_user').id
        admin_list = data.get('admin_list')

        if user_id not in admin_list:
            if event.message is None:
                return event.callback_query.answer('Вы были заблокированы 🛑', show_alert=True)
            return await event.message.answer('Я Вас не знаю ⚠')
        return await handler(event, data)


class ServerConnectionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if event.data.startswith('server:') and not await data['state'].get_data():
            server_name = event.data.split(':')[1]
            server_data = ServersFile().get_server_by_name(server_name)

            try:
                server = SSH(**server_data)
                await data['state'].set_data({'server_name': server_name, 'server': server})
            except ConnectionError:
                return await event.answer(f'Не удалось подключиться к серверу "{server_name}" ⚠️', show_alert=True)

        data.update(await data['state'].get_data())
        return await handler(event, data)
