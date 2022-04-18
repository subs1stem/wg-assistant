from aiogram import types

from settings import ADMIN_IDs


async def set_message_handlers(dp):
    @dp.message_handler(lambda message: message.chat.id not in ADMIN_IDs)
    async def send_auth_error(message: types.Message):
        await message.answer('Я тебя не знаю ⚠')

    @dp.message_handler(commands=['start'])
    async def send_welcome(message: types.Message):
        username = message.chat.username
        if not username:
            username = '%username%'
        await message.answer(f'Привет, {username}! 👋')

    @dp.message_handler(commands=['menu'])
    async def send_main_menu(message: types.Message):
        await message.answer('Здесь будет главное меню')

    @dp.message_handler(content_types=types.ContentTypes.ANY)
    async def send_unknown_message(message: types.Message):
        await message.answer('Я тебя не понимаю\nИспользуй команды ⬇')
