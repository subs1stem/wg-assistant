from os import environ

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.utils import executor
from dotenv import load_dotenv

from handlers.callbacks import set_callback_handlers
from handlers.messages import set_message_handlers

load_dotenv()

bot = Bot(token=environ['TOKEN'])
dispatcher = Dispatcher(bot, storage=MemoryStorage())


async def set_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand('start', 'начало работы'),
        BotCommand('menu', 'главное меню'),
    ])


async def on_startup(dp):
    await set_commands(dp)
    await set_message_handlers(dp)
    await set_callback_handlers(dp)


if __name__ == '__main__':
    executor.start_polling(dispatcher,
                           skip_updates=True,
                           on_startup=on_startup)
