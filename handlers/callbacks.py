from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from modules.fsm_states import AddPeer
from modules.keyboards import *
from modules.messages import peers_message
from wireguard.ssh import SSH

router = Router()


@router.callback_query(lambda callback: str(callback.from_user.id) not in environ['ADMIN_ID'].split(','))
async def access_warning(callback: types.CallbackQuery):
    await callback.message.answer(chat_id=callback.from_user.id,
                                  text='Доступ запрещён 🛑')


@router.callback_query(lambda callback: callback.data == 'main_menu')
async def main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Главное меню:',
                                         reply_markup=main_menu_keyboard())


@router.callback_query(lambda callback: callback.data == 'wg_options')
async def wg_options(callback: types.CallbackQuery):
    await callback.answer('Загрузка...')
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Параметры WireGuard:',
                                         reply_markup=wg_options_keyboard())


@router.callback_query(lambda callback: callback.data == 'reboot_server')
async def reboot_server(callback: types.CallbackQuery):
    await callback.answer('Перезагружаю сервер...')
    SSH().reboot()


@router.callback_query(lambda callback: callback.data == 'get_peers')
async def peers(callback: types.CallbackQuery):
    await callback.answer('Запрашиваю список пиров...')
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text=f'{peers_message()}',
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=peer_list_keyboard())


@router.callback_query(lambda callback: callback.data == 'get_server_config')
async def raw_config(callback: types.CallbackQuery):
    await callback.answer('Запрашиваю конфиг...')
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text=f'<code>{SSH().get_raw_config()}</code>',
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=back_button('wg_options'))


@router.callback_query(lambda callback: callback.data.startswith('wg_state'))
async def change_wg_state(callback: types.CallbackQuery):
    await callback.answer('Выполняю...')
    state = callback.data.split('_')[-1]
    SSH().wg_change_state(state)
    await callback.bot.edit_message_reply_markup(chat_id=callback.from_user.id,
                                                 message_id=callback.message.message_id,
                                                 reply_markup=wg_options_keyboard())


@router.callback_query(lambda callback: callback.data == 'add_peer')
async def add_peer(callback: types.CallbackQuery):
    await callback.answer()
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Пришли мне имя клиента',
                                         reply_markup=cancel_button('main_menu'))
    await AddPeer.waiting_for_peer_name.set()


@router.callback_query(lambda callback: callback.data == 'config_peers')
async def config_peers(callback: types.CallbackQuery):
    await callback.answer('Запрашиваю список пиров...')
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Выбери клиента:',
                                         reply_markup=peers_keyboard())


@router.callback_query(lambda callback: callback.data.startswith('peer'))
async def show_peer(callback: types.CallbackQuery):
    await callback.answer()
    _, pubkey = callback.data.split(':')
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text=f'Выбери действие:',
                                         reply_markup=peer_action(pubkey),
                                         parse_mode=ParseMode.HTML)


@router.callback_query(lambda callback: callback.data.startswith('off_peer'))
async def off_peer(callback: types.CallbackQuery):
    await callback.answer('Отключаю...')
    pubkey = callback.data.split(':')[1]
    SSH().disable_peer(pubkey)
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Выбери клиента:',
                                         reply_markup=peers_keyboard())


@router.callback_query(lambda callback: callback.data.startswith('on_peer'))
async def on_peer(callback: types.CallbackQuery):
    await callback.answer('Включаю...')
    pubkey = callback.data.split(':')[1]
    SSH().enable_peer(pubkey)
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Выбери клиента:',
                                         reply_markup=peers_keyboard())


@router.callback_query(lambda callback: callback.data.startswith('del_peer'))
async def del_peer(callback: types.CallbackQuery):
    await callback.answer('Удаляю...')
    pubkey = callback.data.split(':')[1]
    SSH().delete_peer(pubkey)
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Выбери клиента:',
                                         reply_markup=peers_keyboard())
