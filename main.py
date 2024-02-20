import asyncio
import logging
import sys
from os import environ

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv

from db.database import Database
from handlers import callbacks, commands, errors, messages
from modules.middlewares import LoggingMiddleware, AuthCheckMiddleware, ServerCreateMiddleware
from modules.storages import SQLiteStorage
from servers.servers_file_loader import load_servers_from_file

load_dotenv()


async def main():
    admins = [int(admin_id) for admin_id in environ['ADMIN_ID'].split(',')]
    servers = load_servers_from_file()

    bot = Bot(token=environ['TOKEN'], parse_mode='HTML')

    dp = Dispatcher(
        storage=SQLiteStorage(),
        admins=admins,
        servers=servers,
    )

    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(AuthCheckMiddleware())
    dp.update.middleware(ServerCreateMiddleware())

    dp.include_routers(
        commands.router,
        callbacks.router,
        messages.router,
        errors.router,
    )

    await bot.set_my_commands([
        BotCommand(command='start', description='start'),
        BotCommand(command='servers', description='server list'),
        BotCommand(command='settings', description='bot settings'),
    ])

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    database = Database()
    database.init_db()

    log_level_str = database.get_log_level()
    log_level = logging.getLevelName(log_level_str)

    logging.basicConfig(
        level=log_level,
        stream=sys.stdout,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    # Set the logging level of "aiogram.event" to "WARNING"
    # because there is too much spam coming in with the INFO level
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)

    asyncio.run(main())
