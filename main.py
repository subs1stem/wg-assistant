import asyncio
from os import environ

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv
from redis.asyncio import Redis

from handlers import commands, callbacks, messages
from modules.middlewares import AuthCheckMiddleware

load_dotenv()

redis = Redis(
    host=environ['REDIS_HOST'],
    port=int(environ['REDIS_PORT']),
)


async def main():
    admin_list = [int(admin_id) for admin_id in environ['ADMIN_ID'].split(',')]
    bot = Bot(token=environ['TOKEN'], parse_mode='HTML')
    dp = Dispatcher(storage=RedisStorage(redis), admin_list=admin_list)

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
