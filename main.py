import asyncio
from os import environ

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

from handlers import auth, commands, callbacks, messages

load_dotenv()


async def main():
    bot = Bot(token=environ['TOKEN'])
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(auth.router,
                       commands.router,
                       callbacks.router,
                       messages.router)

    await bot.set_my_commands([
        BotCommand(command='start', description='начало работы'),
        BotCommand(command='menu', description='главное меню'),
    ])

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
