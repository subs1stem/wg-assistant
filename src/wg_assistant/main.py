import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from dotenv import load_dotenv
from pydantic import ValidationError

from wg_assistant.config.env import get_bot_admins, get_bot_token
from wg_assistant.config.servers import get_servers
from wg_assistant.db.database import init_db, get_log_level
from wg_assistant.handlers import callbacks, commands, errors, messages
from wg_assistant.logging_config import setup_logging
from wg_assistant.modules.middlewares import LoggingMiddleware, AuthCheckMiddleware, ServerCreateMiddleware
from wg_assistant.modules.storages import SQLiteStorage

load_dotenv()


async def main():
    try:
        token = get_bot_token()
        admins = get_bot_admins()
    except RuntimeError as e:
        logging.critical(f'Error loading environment variables: {e}')
        sys.exit(1)

    try:
        servers = get_servers()
    except ValidationError as e:
        logging.critical(f'Validation error while loading servers: {e.errors()}')
        sys.exit(1)
    except ValueError as e:
        logging.critical(f'Servers file contains invalid data: {e}')
        sys.exit(1)

    bot = Bot(token, default=DefaultBotProperties(parse_mode='HTML'))

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
    init_db()
    setup_logging(get_log_level())
    asyncio.run(main())
