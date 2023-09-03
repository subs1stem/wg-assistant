from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from data.servers import ServersFile
from modules.fsm_states import AddPeer
from modules.fsm_states import CurrentServer
from modules.keyboards import *
from modules.messages import peers_message
from modules.middlewares import ServerConnectionMiddleware
from wireguard.ssh import SSH

router = Router()
router.callback_query.middleware(ServerConnectionMiddleware())


@router.callback_query(lambda callback: callback.data == 'servers')
async def server_list(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    server_names = ServersFile().get_server_names()
    await state.set_state(CurrentServer.waiting_for_server)
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Список серверов:',
                                         reply_markup=servers_kb(server_names))


@router.callback_query(CurrentServer.waiting_for_server)
async def server_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    server_name = callback.data.split(':')[1]
    await state.set_data(ServersFile().get_server_by_name(server_name))
    await state.set_state(CurrentServer.working_with_server)
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text=f'Сервер <b>{server_name}</b>',
                                         reply_markup=server_options_kb())


@router.callback_query(lambda callback: callback.data == 'wg_options')
async def wg_options(callback: CallbackQuery):
    await callback.answer('Загрузка...')
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Параметры WireGuard:',
                                         reply_markup=wg_options_kb())


@router.callback_query(lambda callback: callback.data == 'reboot_server')
async def reboot_server(callback: CallbackQuery):
    await callback.answer('Перезагружаю сервер...')
    SSH().reboot()


@router.callback_query(CurrentServer.working_with_server, lambda callback: callback.data == 'get_peers')
async def peers(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Запрашиваю список пиров...')
    server_data = state.get_data()
    print(server_data)
    peer_list = SSH().get_peers()
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text=f'{peers_message(peer_list)}',
                                         reply_markup=peer_list_kb())


@router.callback_query(lambda callback: callback.data == 'get_server_config')
async def raw_config(callback: CallbackQuery):
    await callback.answer('Запрашиваю конфиг...')
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text=f'<code>{SSH().get_raw_config()}</code>',
                                         reply_markup=back_btn('wg_options'))


@router.callback_query(lambda callback: callback.data.startswith('wg_state'))
async def change_wg_state(callback: CallbackQuery):
    await callback.answer('Выполняю...')
    state = callback.data.split('_')[-1]
    SSH().wg_change_state(state)
    await callback.bot.edit_message_reply_markup(chat_id=callback.from_user.id,
                                                 message_id=callback.message.message_id,
                                                 reply_markup=wg_options_kb())


@router.callback_query(lambda callback: callback.data == 'add_peer')
async def add_peer(callback: CallbackQuery):
    await callback.answer()
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Пришли мне имя клиента',
                                         reply_markup=cancel_btn('servers'))
    await AddPeer.waiting_for_peer_name.set()


@router.callback_query(lambda callback: callback.data == 'config_peers')
async def config_peers(callback: CallbackQuery):
    await callback.answer('Запрашиваю список пиров...')
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Выбери клиента:',
                                         reply_markup=peers_kb())


@router.callback_query(lambda callback: callback.data.startswith('peer'))
async def show_peer(callback: CallbackQuery):
    await callback.answer()
    _, pubkey = callback.data.split(':')
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text=f'Выбери действие:',
                                         reply_markup=peer_action_kb(pubkey))


@router.callback_query(lambda callback: callback.data.startswith('off_peer'))
async def off_peer(callback: CallbackQuery):
    await callback.answer('Отключаю...')
    pubkey = callback.data.split(':')[1]
    SSH().disable_peer(pubkey)
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Выбери клиента:',
                                         reply_markup=peers_kb())


@router.callback_query(lambda callback: callback.data.startswith('on_peer'))
async def on_peer(callback: CallbackQuery):
    await callback.answer('Включаю...')
    pubkey = callback.data.split(':')[1]
    SSH().enable_peer(pubkey)
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Выбери клиента:',
                                         reply_markup=peers_kb())


@router.callback_query(lambda callback: callback.data.startswith('del_peer'))
async def del_peer(callback: CallbackQuery):
    await callback.answer('Удаляю...')
    pubkey = callback.data.split(':')[1]
    SSH().delete_peer(pubkey)
    await callback.bot.edit_message_text(chat_id=callback.from_user.id,
                                         message_id=callback.message.message_id,
                                         text='Выбери клиента:',
                                         reply_markup=peers_kb())
