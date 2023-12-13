from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class AuthCheckMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user_id = data.get('event_from_user').id
        admins = data.get('admins')

        data.update(await data['state'].get_data())  # TODO: I dont like it

        if user_id not in admins:
            if event.message is None:
                return event.callback_query.answer('Вы были заблокированы 🛑', show_alert=True)
            return await event.message.answer('Я Вас не знаю ⚠')
        return await handler(event, data)
