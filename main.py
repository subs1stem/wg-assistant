import asyncio
from os import environ

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

from handlers import commands, callbacks, messages
from modules.middlewares import AuthCheckMiddleware

load_dotenv()


async def main():
    admin_list = [int(admin_id) for admin_id in environ['ADMIN_ID'].split(',')]
    bot = Bot(token=environ['TOKEN'], parse_mode='HTML')
    dp = Dispatcher(storage=MemoryStorage(), admin_list=admin_list)

    dp.update.middleware(AuthCheckMiddleware())
    # dp.update.filter(MagicData(~F.event.from_user.id.in_(admin_list)))

    dp.include_routers(commands.router,
                       callbacks.router,
                       messages.router)

    await bot.set_my_commands([
        BotCommand(command='start', description='начало работы'),
        BotCommand(command='servers', description='список серверов'),
    ])

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
