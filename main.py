import asyncio
from os import environ

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

from handlers.callbacks import set_callback_handlers
from handlers.messages import set_message_handlers

load_dotenv()


async def set_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand('start', 'начало работы'),
        BotCommand('menu', 'главное меню'),
    ])


async def on_startup(dp):
    await set_commands(dp)
    await set_message_handlers(dp)
    await set_callback_handlers(dp)


async def main():
    bot = Bot(token=environ['TOKEN'])
    dispatcher = Dispatcher(storage=MemoryStorage())
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
