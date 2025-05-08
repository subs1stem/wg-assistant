from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from aiogram.types import Message

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


@pytest.mark.skip
async def test_reboot_host():
    pass


@pytest.mark.skip
async def test_send_peer_list():
    pass


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
