import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.types import BotCommand

from handlers.callbacks import set_callback_handlers
from handlers.messages import set_message_handlers
from settings import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot)


async def set_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand('start', 'начало работы, авторизация'),
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
