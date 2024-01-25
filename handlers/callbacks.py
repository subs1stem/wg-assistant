from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from modules.fsm_states import AddPeer
from modules.keyboards import *
from modules.messages import peers_message
from wireguard.wireguard import WireGuard

router = Router()


@router.callback_query(F.data == 'servers')
async def send_servers(callback: CallbackQuery, state: FSMContext, servers: dict):
    await state.clear()
    server_names = list(servers.keys())
    await callback.message.edit_text(text='Server list:', reply_markup=servers_kb(server_names))


@router.callback_query(F.data.startswith('server:'))
async def send_server_menu(callback: CallbackQuery, server_name: str, server: WireGuard):
    await callback.message.edit_text(
        text=f'Server <b>{server_name}</b>',
        reply_markup=wg_options_kb(server.get_wg_enabled())
    )


@router.callback_query(F.data == 'reboot_server')
async def reboot_server(callback: CallbackQuery, server: WireGuard):
    await callback.answer('Rebooting the server...')
    server.reboot_host()


@router.callback_query(F.data == 'get_peers')
async def send_peer_list(callback: CallbackQuery, server: WireGuard):
    await callback.answer('Requesting status...')
    peer_list = server.get_peers()
    await callback.message.edit_text(text=f'{peers_message(peer_list)}', reply_markup=peer_list_kb())


@router.callback_query(F.data == 'get_server_config')
async def send_raw_config(callback: CallbackQuery, server: WireGuard, server_name: str):
    await callback.answer('Requesting configuration...')
    await callback.message.edit_text(
        text=f'<code>{server.get_config()}</code>',
        reply_markup=back_btn(f'server:{server_name}')
    )


@router.callback_query(F.data.startswith('wg_state'))
async def change_wg_state(callback: CallbackQuery, server: WireGuard):
    await callback.answer('Processing...')
    wg_state = callback.data.split(':')[-1]
    is_up = wg_state == 'up'
    server.set_wg_enabled(is_up)
    await callback.message.edit_reply_markup(reply_markup=wg_options_kb(is_up))


@router.callback_query(F.data == 'add_peer')
async def add_peer(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Send me the client's name", reply_markup=cancel_btn('config_peers'))
    await state.set_state(AddPeer.waiting_for_peer_name)


@router.callback_query(F.data == 'config_peers')
async def config_peers(callback: CallbackQuery, server: WireGuard):
    await callback.answer('Requesting a list of peers...')
    config = server.get_config(as_dict=True)
    config.pop('Interface')
    peers = {name: data['PublicKey'] for name, data in config.items()}
    await callback.message.edit_text(text='Choose a client:', reply_markup=peers_kb(peers))


@router.callback_query(F.data.startswith('peer'))
async def show_peer(callback: CallbackQuery, server: WireGuard):
    pubkey = callback.data.split(':')[-1]
    peer_is_enabled = server.get_peer_enabled(pubkey)
    await callback.message.edit_text(text=f'Choose an action:', reply_markup=peer_action_kb(pubkey, peer_is_enabled))


@router.callback_query(F.data.startswith('selected_peer'))
async def process_peer_action(callback: CallbackQuery, server: WireGuard):
    _, action, pubkey = callback.data.split(':')

    match action:
        case 'off':
            await callback.answer('Disabling...')
            server.disable_peer(pubkey)
        case 'on':
            await callback.answer('Enabling...')
            server.enable_peer(pubkey)
        case 'del':
            await callback.answer('Deleting...')
            server.delete_peer(pubkey)
            return await config_peers(callback, server)
        case _:
            await callback.answer('Unknown action!', show_alert=True)

    await show_peer(callback, server)
