from aiogram import types

from modules.keyboards import *
from settings import ADMIN_IDs
from wireguard.ssh import SSH


async def set_callback_handlers(dp):
    @dp.callback_query_handler(lambda query: query.from_user.id not in ADMIN_IDs)
    async def send_access_warning(query: types.CallbackQuery):
        await query.answer()
        await dp.bot.send_message(chat_id=query.from_user.id,
                                  text='Доступ запрещён 🛑')

    @dp.callback_query_handler(lambda query: query.data == 'main_menu')
    async def send_main_menu(query: types.CallbackQuery):
        await query.answer()
        await dp.bot.edit_message_text(chat_id=query.from_user.id,
                                       message_id=query.message.message_id,
                                       text='Главное меню:',
                                       reply_markup=main_menu_keyboard())

    @dp.callback_query_handler(lambda query: query.data == 'get_raw_config')
    async def send_raw_config(query: types.CallbackQuery):
        await query.answer('Запрашиваю конфиг...')
        await dp.bot.edit_message_text(chat_id=query.from_user.id,
                                       message_id=query.message.message_id,
                                       text=f'`{SSH().get_raw_config()}`',
                                       parse_mode=types.ParseMode.MARKDOWN_V2,
                                       reply_markup=back_button('main_menu'))
