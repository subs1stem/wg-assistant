from aiogram import types

from modules.keyboards import *
from modules.messages import peers_message
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

    @dp.callback_query_handler(lambda query: query.data == 'wg_options')
    async def send_wg_options(query: types.CallbackQuery):
        await query.answer()
        await dp.bot.edit_message_text(chat_id=query.from_user.id,
                                       message_id=query.message.message_id,
                                       text='Параметры WireGuard:',
                                       reply_markup=wg_options_keyboard())

    @dp.callback_query_handler(lambda query: query.data == 'reboot_server')
    async def reboot_server(query: types.CallbackQuery):
        await query.answer('Перезагружаю сервер...')
        SSH().reboot()

    @dp.callback_query_handler(lambda query: query.data == 'get_peers')
    async def send_peers(query: types.CallbackQuery):
        await query.answer('Запрашиваю список пиров...')
        await dp.bot.edit_message_text(chat_id=query.from_user.id,
                                       message_id=query.message.message_id,
                                       text=f'{peers_message()}',
                                       parse_mode=types.ParseMode.HTML,
                                       reply_markup=back_button('wg_options'))

    @dp.callback_query_handler(lambda query: query.data == 'get_server_config')
    async def send_raw_config(query: types.CallbackQuery):
        await query.answer('Запрашиваю конфиг...')
        await dp.bot.edit_message_text(chat_id=query.from_user.id,
                                       message_id=query.message.message_id,
                                       text=f'<code>{SSH().get_raw_config()}</code>',
                                       parse_mode=types.ParseMode.HTML,
                                       reply_markup=back_button('wg_options'))
