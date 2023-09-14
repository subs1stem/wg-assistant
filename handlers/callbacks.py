from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from data.servers import ServersFile
from modules.fsm_states import AddPeer
from modules.fsm_states import CurrentServer
from modules.keyboards import *
from modules.messages import peers_message
from modules.middlewares import ServerConnectionMiddleware
from wireguard.ssh import SSH

router = Router()
router.callback_query.middleware(CallbackAnswerMiddleware())
router.callback_query.middleware(ServerConnectionMiddleware())


@router.callback_query(F.data == 'servers')
async def send_server_list(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    server_names = ServersFile().get_server_names()
    await callback.message.edit_text(text='Список серверов:', reply_markup=servers_kb(server_names))


@router.callback_query(F.data.startswith('server:'))
async def send_server_menu(callback: CallbackQuery, state: FSMContext):
    server_name = (await state.get_data())['server_name']
    interface_is_up = (await state.get_data())['server'].get_wg_status()
    await state.set_state(CurrentServer.working_with_server)
    await callback.message.edit_text(text=f'Сервер <b>{server_name}</b>', reply_markup=wg_options_kb(interface_is_up))


@router.callback_query(F.data == 'reboot_server')
async def reboot_server(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Перезагружаю сервер...')
    (await state.get_data())['server'].reboot()


@router.callback_query(CurrentServer.working_with_server, F.data == 'get_peers')
async def send_peer_list(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Запрашиваю состояние пиров...')
    peer_list = (await state.get_data())['server'].get_peers()
    await callback.message.edit_text(text=f'{peers_message(peer_list)}', reply_markup=peer_list_kb())


@router.callback_query(CurrentServer.working_with_server, F.data == 'get_server_config')
async def send_raw_config(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Запрашиваю конфиг...')
    raw_config = (await state.get_data())['server'].get_raw_config()
    await callback.message.edit_text(text=f'<code>{raw_config}</code>', reply_markup=back_btn('wg_options'))


@router.callback_query(F.data.startswith('wg_state'))
async def change_wg_state(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Выполняю...')
    wg_state = callback.data.split(':')[-1]
    (await state.get_data())['server'].wg_change_state(wg_state)
    interface_is_up = wg_state == 'up'
    await callback.message.edit_reply_markup(reply_markup=wg_options_kb(interface_is_up))


@router.callback_query(F.data == 'add_peer')
async def add_peer(callback: CallbackQuery):
    await callback.message.edit_text(text='Пришли мне имя клиента', reply_markup=cancel_btn('servers'))
    await AddPeer.waiting_for_peer_name.set()


@router.callback_query(F.data == 'config_peers')
async def config_peers(callback: CallbackQuery):
    await callback.answer('Запрашиваю список пиров...')
    await callback.message.edit_text(text='Выбери клиента:', reply_markup=peers_kb())


@router.callback_query(F.data.startswith('peer'))
async def show_peer(callback: CallbackQuery):
    _, pubkey = callback.data.split(':')
    await callback.message.edit_text(text=f'Выбери действие:', reply_markup=peer_action_kb(pubkey))


@router.callback_query(F.data.startswith('off_peer'))
async def off_peer(callback: CallbackQuery):
    await callback.answer('Отключаю...')
    pubkey = callback.data.split(':')[1]
    SSH().disable_peer(pubkey)
    await callback.message.edit_text(text='Выбери клиента:', reply_markup=peers_kb())


@router.callback_query(F.data.startswith('on_peer'))
async def on_peer(callback: CallbackQuery):
    await callback.answer('Включаю...')
    pubkey = callback.data.split(':')[1]
    SSH().enable_peer(pubkey)
    await callback.message.edit_text(text='Выбери клиента:', reply_markup=peers_kb())


@router.callback_query(F.data.startswith('del_peer'))
async def del_peer(callback: CallbackQuery):
    await callback.answer('Удаляю...')
    pubkey = callback.data.split(':')[1]
    SSH().delete_peer(pubkey)
    await callback.message.edit_text(text='Выбери клиента:', reply_markup=peers_kb())
