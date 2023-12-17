from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery

from servers.server_factory import ServerFactory
from wireguard.wireguard import WireGuard


class AuthCheckMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user_id = data.get('event_from_user').id
        admins = data.get('admins')

        if user_id not in admins:
            if event.message is None:
                return await event.callback_query.answer('Вы были заблокированы 🛑', show_alert=True)

            return await event.message.answer('Я Вас не знаю ⚠')

        return await handler(event, data)


class ServerCreateMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        servers = data.get('servers')
        state_data = await data.get('state').get_data()
        server_name = state_data.get('server_name') or event.data.split(':')[1]
        server_data = servers.get(server_name)

        try:
            server: WireGuard = ServerFactory.create_server_instance(server_name, server_data)
        except ConnectionError:
            return await event.answer(
                f'Не удалось подключиться к серверу "{server_name}" ⚠️',
                show_alert=True
            )

        await data['state'].set_data({'server_name': server_name, 'server': server})
        data.update(server_name=server_name, server=server)

        return await handler(event, data)
