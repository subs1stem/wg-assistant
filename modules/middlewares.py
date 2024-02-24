import logging
from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from servers.server_factory import ServerFactory


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        event_json = event.model_dump_json(indent=2, exclude_none=True)
        logging.debug(f'Incoming update:\n{event_json}')
        return await handler(event, data)


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
                return await event.callback_query.answer('You have been blocked 🛑', show_alert=True)

            return await event.message.answer("I don't know you ⚠")

        return await handler(event, data)


class ServerCreateMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if event.message is not None and event.message.text.startswith('/'):
            return await handler(event, data)

        state = data['state']

        if event.callback_query:
            callback_data = event.callback_query.data

            if callback_data.startswith('server:') and callback_data != 'server:':
                servers = data.get('servers')
                server_name = callback_data.split(':')[1]
                server_data = servers.get(server_name)

                await state.set_data({
                    'server_name': server_name,
                    'server_data': server_data
                })

        state_data = await state.get_data()

        if state_data:
            server_name = state_data['server_name']
            server_data = state_data['server_data']
            server = ServerFactory.create_server_instance(server_name, server_data)
            data.update(server_name=server_name, server=server)

        return await handler(event, data)
