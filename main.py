import asyncio
from os import environ

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

from handlers import callbacks, commands, errors, messages
from modules.middlewares import AuthCheckMiddleware, ServerCreateMiddleware
from modules.storages import SQLiteStorage
from servers.servers_file_loader import load_servers_from_file

load_dotenv()


async def main():
    admins = [int(admin_id) for admin_id in environ['ADMIN_ID'].split(',')]
    servers = load_servers_from_file()

    bot = Bot(token=environ['TOKEN'], parse_mode='HTML')

    dp = Dispatcher(
        # storage=SQLiteStorage(),
        storage=MemoryStorage(),
        admins=admins,
        servers=servers,
    )

    dp.update.middleware(AuthCheckMiddleware())
    dp.update.middleware(ServerCreateMiddleware())

    dp.include_routers(
        commands.router,
        callbacks.router,
        messages.router,
        errors.router,
    )

    await bot.set_my_commands([
        BotCommand(command='start', description='начало работы'),
        BotCommand(command='servers', description='список серверов'),
    ])

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
