import asyncio
from os import environ

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

from handlers import messages

load_dotenv()


async def set_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand('start', 'начало работы'),
        BotCommand('menu', 'главное меню'),
    ])


async def on_startup(dp):
    await set_commands(dp)


async def main():
    bot = Bot(token=environ['TOKEN'])
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(messages.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
