from copy import deepcopy
from logging import Logger
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from aiogram.types import Message

from wg_assistant.handlers.callbacks import *
from wg_assistant.models.server import ServerModel
from wg_assistant.wireguard.wireguard import WireGuard


@patch('wg_assistant.handlers.callbacks.servers_kb', return_value='mock_kb')
async def test_send_servers(mock_servers_kb):
    callback = MagicMock(
        spec=CallbackQuery,
        message=MagicMock(spec=Message, edit_text=AsyncMock()),
    )

    state = MagicMock(spec=FSMContext, clear=AsyncMock())

    server1 = MagicMock(spec=ServerModel)
    server1.name = 'server1'
    server2 = MagicMock(spec=ServerModel)
    server2.name = 'server2'
    servers = [server1, server2]

    await send_servers(callback, state, servers)

    mock_servers_kb.assert_called_once_with(['server1', 'server2'])
    state.clear.assert_awaited_once()
    callback.message.edit_text.assert_awaited_once_with(text='Server list:', reply_markup='mock_kb')


@pytest.mark.parametrize(
    'server_name,expected_wg_enabled',
    [('server1', True), ('server2', False)],
    ids=['enabled wg', 'disabled wg'],
)
@patch('wg_assistant.handlers.callbacks.wg_options_kb', return_value='mock_kb')
async def test_send_server_menu(mock_wg_options_kb, server_name, expected_wg_enabled):
    callback = MagicMock(
        spec=CallbackQuery,
        message=MagicMock(spec=Message, edit_text=AsyncMock()),
    )

    server = MagicMock(spec=WireGuard, get_wg_enabled=MagicMock(return_value=expected_wg_enabled))

    await send_server_menu(callback, server_name, server)

    mock_wg_options_kb.assert_called_once_with(expected_wg_enabled)
    callback.message.edit_text.assert_awaited_once_with(
        text=f'Server <b>{server_name}</b>',
        reply_markup='mock_kb',
    )


@patch('wg_assistant.handlers.callbacks.yes_no_kb', return_value='mock_kb')
async def test_send_reboot_host_confirmation(mock_yes_no_kb):
    callback = MagicMock(
        spec=CallbackQuery,
        message=MagicMock(spec=Message, edit_text=AsyncMock()),
    )

    await send_reboot_host_confirmation(callback)

    mock_yes_no_kb.assert_called_once_with('confirm_reboot')
    callback.message.edit_text.assert_awaited_once_with(
        text='Are you sure you want to reboot the host?',
        reply_markup='mock_kb',
    )


@pytest.mark.parametrize('callback_data', ['confirm_reboot:y', 'confirm_reboot:n'], ids=['confirmed', 'canceled'])
@patch('wg_assistant.handlers.callbacks.send_servers')
@patch('wg_assistant.handlers.callbacks.send_server_menu')
async def test_reboot_host(mock_send_server_menu, mock_send_servers, callback_data):
    callback = MagicMock(
        spec=CallbackQuery,
        data=callback_data,
        answer=AsyncMock(),
    )

    state = MagicMock(spec=FSMContext)
    server_name = 'server1'
    server = MagicMock(spec=WireGuard, reboot_host=MagicMock())

    server1 = MagicMock(spec=ServerModel)
    server1.name = 'server1'
    server2 = MagicMock(spec=ServerModel)
    server2.name = 'server2'
    servers = [server1, server2]

    await reboot_host(callback, state, servers, server_name, server)

    if callback_data == 'confirm_reboot:y':
        callback.answer.assert_awaited_once_with('Rebooting the host...')
        server.reboot_host.assert_called_once_with()
        mock_send_servers.assert_awaited_once_with(callback, state, servers)
        mock_send_server_menu.assert_not_awaited()
    else:
        mock_send_server_menu.assert_awaited_once_with(callback, server_name, server)
        callback.answer.assert_not_awaited()
        server.reboot_host.assert_not_called()
        mock_send_servers.assert_not_awaited()


@patch('wg_assistant.handlers.callbacks.peers_message', return_value='peers_message')
@patch('wg_assistant.handlers.callbacks.peer_list_kb', return_value='mock_kb')
async def test_send_peer_list(mock_peer_list_kb, mock_peers_message, name_pubkey_peer_list):
    callback = MagicMock(
        spec=CallbackQuery,
        answer=AsyncMock(),
        message=MagicMock(spec=Message, edit_text=AsyncMock()),
    )

    server = MagicMock(
        spec=WireGuard,
        get_peers=MagicMock(return_value=name_pubkey_peer_list),
    )

    await send_peer_list(callback, server)

    callback.answer.assert_awaited_once_with('Requesting status...')
    server.get_peers.assert_called_once_with()
    mock_peers_message.assert_called_once_with(name_pubkey_peer_list)
    mock_peer_list_kb.assert_called_once_with()
    callback.message.edit_text.assert_awaited_once_with(text='peers_message', reply_markup='mock_kb')


@patch('wg_assistant.handlers.callbacks.back_btn', return_value='mock_kb')
async def test_send_raw_config(mock_back_btn):
    callback = MagicMock(
        spec=CallbackQuery,
        answer=AsyncMock(),
        message=MagicMock(spec=Message, edit_text=AsyncMock()),
    )

    server = MagicMock(
        spec=WireGuard,
        get_config=MagicMock(return_value='raw_server_config'),
    )

    server_name = 'test_server'

    await send_raw_config(callback, server, server_name)

    callback.answer.assert_awaited_once_with('Requesting configuration...')
    server.get_config.assert_called_once_with()
    mock_back_btn.assert_called_once_with(f'server:{server_name}')
    callback.message.edit_text.assert_awaited_once_with(
        text='<code>raw_server_config</code>',
        reply_markup='mock_kb',
    )


@pytest.mark.parametrize(
    'callback_data,expected_enabled',
    (['wg_state:up', True], ['wg_state:down', False]),
    ids=['up', 'down'],
)
@patch('wg_assistant.handlers.callbacks.wg_options_kb', return_value='mock_kb')
async def test_change_wg_state(mock_wg_options_kb, callback_data, expected_enabled):
    callback = MagicMock(
        spec=CallbackQuery,
        answer=AsyncMock(),
        data=callback_data,
        message=MagicMock(spec=Message, edit_reply_markup=AsyncMock()),
    )

    server = MagicMock(
        spec=WireGuard,
        set_wg_enabled=MagicMock(),
    )

    await change_wg_state(callback, server)

    callback.answer.assert_awaited_once_with('Processing...')
    server.set_wg_enabled.assert_called_once_with(expected_enabled)
    mock_wg_options_kb.assert_called_once_with(expected_enabled)
    callback.message.edit_reply_markup.assert_awaited_once_with(reply_markup='mock_kb')


@patch('wg_assistant.handlers.callbacks.AddPeer.waiting_for_peer_name')
@patch('wg_assistant.handlers.callbacks.cancel_btn', return_value='mock_kb')
async def test_add_peer(mock_cancel_btn, mock_waiting_for_peer_name):
    callback = MagicMock(
        spec=CallbackQuery,
        message=MagicMock(spec=Message, edit_text=AsyncMock()),
    )

    state = MagicMock(spec=FSMContext, set_state=AsyncMock())

    await add_peer(callback, state)

    mock_cancel_btn.assert_called_once_with('config_peers')
    callback.message.edit_text.assert_awaited_once_with(text="Send me the client's name", reply_markup='mock_kb')
    state.set_state.assert_awaited_once_with(mock_waiting_for_peer_name)


@pytest.mark.parametrize('has_photo', [True, False], ids=['photo', 'no photo'])
@patch('wg_assistant.handlers.callbacks.peers_kb', return_value='mock_kb')
async def test_config_peers(mock_peers_kb, has_photo, server_config_as_dict, name_pubkey_peer_list):
    callback = MagicMock(
        spec=CallbackQuery,
        answer=AsyncMock(),
        message=MagicMock(
            spec=Message,
            photo=has_photo,
            delete=AsyncMock(),
            answer=AsyncMock(),
            edit_text=AsyncMock(),
        ),
    )

    server = MagicMock(
        spec=WireGuard,
        get_config=MagicMock(return_value=deepcopy(server_config_as_dict)),
    )

    state = MagicMock(spec=FSMContext, set_state=AsyncMock())
    text = 'Choose a client:'
    reply_markup = 'mock_kb'

    await config_peers(callback, server, state)

    state.set_state.assert_awaited_once_with()
    callback.answer.assert_awaited_once_with('Requesting a list of peers...')
    server.get_config.assert_called_once_with(as_dict=True)
    mock_peers_kb.assert_called_once_with(name_pubkey_peer_list)

    if has_photo:
        callback.message.delete.assert_awaited_once_with()
        callback.message.answer.assert_awaited_once_with(text=text, reply_markup=reply_markup)
    else:
        callback.message.edit_text.assert_awaited_once_with(text=text, reply_markup=reply_markup)


@pytest.mark.parametrize(
    'callback_data,peer_pubkey,expected_peer_enabled',
    [
        ('peer:IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=', 'IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=', True),
        ('peer:2FOgBVysbAX/2WQQpcQbVb2VyA2wdOZXTDbh/F6RxUQ=', '2FOgBVysbAX/2WQQpcQbVb2VyA2wdOZXTDbh/F6RxUQ=', False),
    ],
    ids=['enabled peer', 'disabled peer'],
)
@patch('wg_assistant.handlers.callbacks.peer_action_kb', return_value='mock_kb')
async def test_show_peer(mock_peer_action_kb, callback_data, peer_pubkey, expected_peer_enabled):
    callback = MagicMock(
        spec=CallbackQuery,
        data=callback_data,
        message=MagicMock(spec=Message, edit_text=AsyncMock()),
    )

    server = MagicMock(spec=WireGuard, get_peer_enabled=MagicMock(return_value=expected_peer_enabled))
    state = MagicMock(spec=FSMContext, set_state=AsyncMock())

    await show_peer(callback, server, state)

    state.set_state.assert_awaited_once_with()
    server.get_peer_enabled.assert_called_once_with(peer_pubkey)
    mock_peer_action_kb.assert_called_once_with(peer_pubkey, expected_peer_enabled)
    callback.message.edit_text.assert_awaited_once_with(text=f'Choose an action:', reply_markup='mock_kb')


@pytest.mark.parametrize(
    'callback_data,action,pubkey',
    [
        (
                'selected_peer:name:IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=',
                'name',
                'IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=',
        ),
        (
                'selected_peer:off:IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=',
                'off',
                'IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=',
        ),
        (
                'selected_peer:on:IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=',
                'on',
                'IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=',
        ),
        (
                'selected_peer:del:IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=',
                'del',
                'IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=',
        ),
        (
                'selected_peer:unknown_action:IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=',
                'unknown_action',
                'IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=',
        ),
    ],
    ids=['change name', 'disable', 'enable', 'delete', 'unknown action'],
)
@patch('wg_assistant.handlers.callbacks.show_peer')
@patch('wg_assistant.handlers.callbacks.RenamePeer.waiting_for_new_name')
@patch('wg_assistant.handlers.callbacks.yes_no_kb', return_value='mock_yes_no_keyboard')
@patch('wg_assistant.handlers.callbacks.cancel_btn', return_value='mock_cancel_button')
async def test_process_peer_action(
        mock_cancel_button,
        mock_yes_no_keyboard,
        mock_waiting_for_new_name_state,
        mock_show_peer,
        callback_data,
        action,
        pubkey,
):
    callback = MagicMock(
        spec=CallbackQuery,
        data=callback_data,
        answer=AsyncMock(),
        message=MagicMock(spec=Message, edit_text=AsyncMock()),
    )

    state = MagicMock(
        spec=FSMContext,
        update_data=AsyncMock(),
        set_state=AsyncMock(),
    )

    server = MagicMock(spec=WireGuard, set_peer_enabled=MagicMock())

    await process_peer_action(callback, state, server)

    match action:
        case 'name':
            callback.answer.assert_awaited_once_with()
            mock_cancel_button.assert_called_once_with(f'peer:{pubkey}')

            callback.message.edit_text.assert_awaited_once_with(
                text='Send me the new client name',
                reply_markup='mock_cancel_button',
            )

            state.update_data.assert_awaited_once_with({'pubkey': pubkey})
            state.set_state.assert_awaited_once_with(mock_waiting_for_new_name_state)

            server.set_peer_enabled.assert_not_called()
            mock_show_peer.assert_not_awaited()
        case 'off':
            callback.answer.assert_awaited_once_with('Disabling...')
            server.set_peer_enabled.assert_called_once_with(pubkey, False)
            mock_show_peer.assert_awaited_once_with(callback, server, state)

            callback.message.edit_text.assert_not_awaited()
            state.update_data.assert_not_awaited()
            state.set_state.assert_not_awaited()
        case 'on':
            callback.answer.assert_awaited_once_with('Enabling...')
            server.set_peer_enabled.assert_called_once_with(pubkey, True)
            mock_show_peer.assert_awaited_once_with(callback, server, state)

            callback.message.edit_text.assert_not_awaited()
            state.update_data.assert_not_awaited()
            state.set_state.assert_not_awaited()
        case 'del':
            mock_yes_no_keyboard.assert_called_once_with('confirm_peer_del', pubkey)

            callback.message.edit_text.assert_awaited_once_with(
                text='Are you sure you want to delete the peer? This action cannot be reversed!',
                reply_markup='mock_yes_no_keyboard',
            )

            callback.answer.assert_not_awaited()
            state.update_data.assert_not_awaited()
            state.set_state.assert_not_awaited()
            server.set_peer_enabled.assert_not_called()
            mock_show_peer.assert_not_awaited()
        case 'unknown_action':
            callback.answer.assert_awaited_once_with('Unknown action!', show_alert=True)
            mock_show_peer.assert_awaited_once_with(callback, server, state)

            callback.message.edit_text.assert_not_awaited()
            state.update_data.assert_not_awaited()
            state.set_state.assert_not_awaited()
            server.set_peer_enabled.assert_not_called()


@pytest.mark.parametrize(
    'callback_data,deletion_confirmed,pubkey',
    [
        (
                'confirm_peer_del:y:IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=',
                True,
                'IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=',
        ),
        (
                'confirm_peer_del:n:2FOgBVysbAX/2WQQpcQbVb2VyA2wdOZXTDbh/F6RxUQ=',
                False,
                '2FOgBVysbAX/2WQQpcQbVb2VyA2wdOZXTDbh/F6RxUQ=',
        ),
    ],
    ids=['confirmed', 'canceled'],
)
@patch('wg_assistant.handlers.callbacks.show_peer')
@patch('wg_assistant.handlers.callbacks.config_peers')
async def test_delete_peer(mock_config_peers, mock_show_peer, callback_data, deletion_confirmed, pubkey):
    callback = MagicMock(
        spec=CallbackQuery,
        data=callback_data,
        answer=AsyncMock(),
    )

    state = MagicMock(spec=FSMContext)
    server = MagicMock(spec=WireGuard, delete_peer=MagicMock())

    await delete_peer(callback, state, server)

    if deletion_confirmed:
        callback.answer.assert_awaited_once_with('Deleting...')
        server.delete_peer.assert_called_once_with(pubkey)
        mock_config_peers.assert_awaited_once_with(callback, server, state)
        mock_show_peer.assert_not_awaited()
    else:
        mock_show_peer.assert_awaited_once_with(callback, server, state)
        callback.answer.assert_not_awaited()
        server.delete_peer.assert_not_called()
        mock_config_peers.assert_not_awaited()


@pytest.mark.parametrize(
    'callback_data,state,log_level',
    [('debug_log:enable', True, 'DEBUG'), ('debug_log:disable', False, 'INFO')],
    ids=['enable', 'disable'],
)
@patch('wg_assistant.handlers.callbacks.logging.getLogger')
@patch('wg_assistant.handlers.callbacks.set_log_level')
@patch('wg_assistant.handlers.callbacks.bot_settings_kb', return_value='mock_kb')
async def test_set_debug_log_state(
        mock_bot_settings_kb,
        mock_set_log_level,
        mock_get_logger,
        callback_data,
        state,
        log_level,
):
    callback = MagicMock(
        spec=CallbackQuery,
        data=callback_data,
        message=MagicMock(spec=Message, edit_reply_markup=AsyncMock()),
    )

    mock_logger = MagicMock(spec=Logger)
    mock_get_logger.return_value = mock_logger

    await set_debug_log_state(callback)

    mock_set_log_level.assert_called_once_with(log_level)
    mock_logger.setLevel.assert_called_once_with(log_level)
    mock_bot_settings_kb.assert_called_once_with(state)
    callback.message.edit_reply_markup.assert_awaited_once_with(reply_markup='mock_kb')
