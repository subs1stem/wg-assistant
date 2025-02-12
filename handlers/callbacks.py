import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from db.database import Database
from modules.fsm_states import AddPeer, RenamePeer
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


@router.callback_query(F.data == 'reboot_host')
async def send_reboot_host_confirmation(callback: CallbackQuery):
    await callback.message.edit_text(
        text='Are you sure you want to reboot the host?',
        reply_markup=yes_no_kb('confirm_reboot')
    )


@router.callback_query(F.data.startswith('confirm_reboot'))
async def reboot_host(callback: CallbackQuery, state: FSMContext, servers: dict, server_name: str, server: WireGuard):
    reboot_confirmed = callback.data.split(':')[-1] == 'y'

    if reboot_confirmed:
        await callback.answer('Rebooting the host...')
        server.reboot_host()
        await send_servers(callback, state, servers)
    else:
        await send_server_menu(callback, server_name, server)


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
async def config_peers(callback: CallbackQuery, server: WireGuard, state: FSMContext):
    await state.set_state()
    await callback.answer('Requesting a list of peers...')

    config = server.get_config(as_dict=True)
    config.pop('Interface')
    peers = {name: data['PublicKey'] for name, data in config.items()}

    text = 'Choose a client:'
    markup = peers_kb(peers)

    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text=text, reply_markup=markup)
    else:
        await callback.message.edit_text(text=text, reply_markup=markup)


@router.callback_query(F.data.startswith('peer'))
async def show_peer(callback: CallbackQuery, server: WireGuard, state: FSMContext):
    await state.set_state()
    pubkey = callback.data.split(':')[-1]
    peer_is_enabled = server.get_peer_enabled(pubkey)
    await callback.message.edit_text(text=f'Choose an action:', reply_markup=peer_action_kb(pubkey, peer_is_enabled))


@router.callback_query(F.data.startswith('selected_peer'))
async def process_peer_action(callback: CallbackQuery, state: FSMContext, server: WireGuard):
    _, action, pubkey = callback.data.split(':')

    match action:
        case 'name':
            await callback.answer()
            await callback.message.edit_text(
                text="Send me the new client name",
                reply_markup=cancel_btn(f'peer:{pubkey}')
            )
            await state.update_data({'pubkey': pubkey})
            return await state.set_state(RenamePeer.waiting_for_new_name)
        case 'off':
            await callback.answer('Disabling...')
            server.set_peer_enabled(pubkey, False)
        case 'on':
            await callback.answer('Enabling...')
            server.set_peer_enabled(pubkey, True)
        case 'del':
            return await callback.message.edit_text(
                text='Are you sure you want to delete the peer? This action cannot be reversed!',
                reply_markup=yes_no_kb(f'confirm_peer_del', pubkey)
            )
        case _:
            await callback.answer('Unknown action!', show_alert=True)

    await show_peer(callback, server, state)


@router.callback_query(F.data.startswith('confirm_peer_del'))
async def delete_peer(callback: CallbackQuery, state: FSMContext, server: WireGuard):
    _, deletion_yes_no, pubkey = callback.data.split(':')
    deletion_confirmed = deletion_yes_no == 'y'

    if deletion_confirmed:
        await callback.answer('Deleting...')
        server.delete_peer(pubkey)
        return await config_peers(callback, server, state)
    else:
        await show_peer(callback, server, state)


@router.callback_query(F.data.startswith('debug_log'))
async def set_debug_log_state(callback: CallbackQuery):
    state = callback.data.split(':')[-1] == 'enable'
    log_level = 'DEBUG' if state else 'INFO'
    Database().set_log_level(log_level)
    logging.getLogger().setLevel(log_level)
    await callback.message.edit_reply_markup(reply_markup=bot_settings_kb(state))
