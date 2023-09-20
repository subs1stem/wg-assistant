from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from data.servers import ServersFile
from modules.fsm_states import AddPeer, CurrentServer
from modules.keyboards import *
from modules.messages import peers_message
from modules.middlewares import ServerConnectionMiddleware

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
    await callback.answer('Запрашиваю конфигурацию...')
    raw_config = (await state.get_data())['server'].get_raw_config()
    await callback.message.edit_text(text=f'<code>{raw_config}</code>', reply_markup=back_btn('server:'))


@router.callback_query(F.data.startswith('wg_state'))
async def change_wg_state(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Выполняю...')
    wg_state = callback.data.split(':')[-1]
    (await state.get_data())['server'].wg_change_state(wg_state)
    interface_is_up = wg_state == 'up'
    await callback.message.edit_reply_markup(reply_markup=wg_options_kb(interface_is_up))


@router.callback_query(F.data == 'add_peer')
async def add_peer(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Пришли мне имя клиента', reply_markup=cancel_btn('config_peers'))
    await state.set_state(AddPeer.waiting_for_peer_name)


@router.callback_query(F.data == 'config_peers')
async def config_peers(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Запрашиваю список пиров...')
    peer_names = (await state.get_data())['server'].get_peer_names()
    await callback.message.edit_text(text='Выбери клиента:', reply_markup=peers_kb(peer_names))


@router.callback_query(F.data.startswith('peer'))
async def show_peer(callback: CallbackQuery, state: FSMContext):
    _, pubkey = callback.data.split(':')
    peer_is_enabled = (await state.get_data())['server'].get_peer_enabled(pubkey)
    await callback.message.edit_text(text=f'Выбери действие:', reply_markup=peer_action_kb(pubkey, peer_is_enabled))


@router.callback_query(F.data.startswith('selected_peer'))
async def process_peer_action(callback: CallbackQuery, state: FSMContext):
    _, action, pubkey = callback.data.split(':')

    match action:
        case 'off':
            await callback.answer('Отключаю...')
            (await state.get_data())['server'].disable_peer(pubkey)
        case 'on':
            await callback.answer('Включаю...')
            (await state.get_data())['server'].enable_peer(pubkey)
        case 'del':
            await callback.answer('Удаляю...')
            (await state.get_data())['server'].delete_peer(pubkey)
        case _:
            await callback.answer('Неизвестное действие!', show_alert=True)

    await config_peers(callback, state)
