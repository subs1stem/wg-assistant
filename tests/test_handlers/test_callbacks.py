from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from aiogram.types import Message

from conftest import name_pubkey_peer_list
from wg_assistant.handlers.callbacks import *
from wg_assistant.models.servers import ServerModel
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


@pytest.mark.parametrize('server_name,expected_wg_enabled', [
    ('server1', True),
    ('server2', False),
])
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


@pytest.mark.skip
async def test_send_raw_config():
    pass


@pytest.mark.skip
async def test_change_wg_state():
    pass


@pytest.mark.skip
async def test_add_peer():
    pass


@pytest.mark.skip
async def test_config_peers():
    pass


@pytest.mark.skip
async def test_show_peer():
    pass


@pytest.mark.skip
async def test_process_peer_action():
    pass


@pytest.mark.skip
async def test_delete_peer():
    pass


@pytest.mark.skip
async def test_set_debug_log_state():
    pass
