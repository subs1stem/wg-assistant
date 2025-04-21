import pytest

from wg_assistant.modules.keyboards import *

PUBLIC_KEY = 'ANVS03UUByb787r25trQKZ0CXYYAcYdBEJskGZd5i1o='


def test_back_btn():
    kb = back_btn('back').inline_keyboard
    row = kb[0]
    assert len(row) == 1
    assert row[0].text == '⬅ Back'
    assert row[0].callback_data == 'back'


def test_cancel_btn():
    kb = cancel_btn('cancel').inline_keyboard
    row = kb[0]
    assert len(row) == 1
    assert row[0].text == 'Cancel ❌'
    assert row[0].callback_data == 'cancel'


def test_yes_no_kb():
    kb = yes_no_kb('yes_no', 'extra').inline_keyboard
    row = kb[0]
    assert len(row) == 2
    assert row[0].text == 'Yes ✅'
    assert row[0].callback_data == 'yes_no:y:extra'
    assert row[1].text == 'No ❌'
    assert row[1].callback_data == 'yes_no:n:extra'


def test_servers_kb():
    kb = servers_kb(['spam', 'eggs']).inline_keyboard

    row1 = kb[0]
    row2 = kb[1]

    assert len(row1) == 1
    assert len(row2) == 1

    assert row1[0].text == 'spam'
    assert row1[0].callback_data == 'server:spam'
    assert row2[0].text == 'eggs'
    assert row2[0].callback_data == 'server:eggs'


@pytest.mark.parametrize('interface_is_up,expected_button_text,expected_callback', [
    (True, 'Disable interface ⬇️', 'wg_state:down'),
    (False, 'Enable interface ⬆️', 'wg_state:up'),
])
def test_wg_options_kb(interface_is_up, expected_button_text, expected_callback):
    kb = wg_options_kb(interface_is_up).inline_keyboard

    row1 = kb[0]
    row2 = kb[1]
    row3 = kb[2]
    row4 = kb[3]

    assert len(row1) == 1
    assert len(row2) == 2
    assert len(row3) == 2
    assert len(row4) == 1

    assert row1[0].text == 'Status 📝'
    assert row1[0].callback_data == 'get_peers'
    assert row2[0].text == 'Management 🎛'
    assert row2[0].callback_data == 'config_peers'
    assert row2[1].text == 'Configuration ⚙️'
    assert row2[1].callback_data == 'get_server_config'
    assert row3[0].text == expected_button_text
    assert row3[0].callback_data == expected_callback
    assert row3[1].text == 'Reboot host 🔄'
    assert row3[1].callback_data == 'reboot_host'
    assert row4[0].text == '⬅ Go to server list'
    assert row4[0].callback_data == 'servers'


def test_peer_list_kb():
    kb = peer_list_kb().inline_keyboard

    row1 = kb[0]
    row2 = kb[1]

    assert len(row1) == 1
    assert len(row2) == 1

    assert row1[0].text == 'Refresh 🔄'
    assert row1[0].callback_data == 'get_peers'
    assert row2[0].text == '⬅ Back'
    assert row2[0].callback_data == 'server:'


def test_peers_kb(name_pubkey_peer_list):
    kb = peers_kb(name_pubkey_peer_list).inline_keyboard

    row1 = kb[0]
    row2 = kb[1]
    row3 = kb[2]
    row4 = kb[3]
    row5 = kb[4]

    assert len(row1) == 1
    assert len(row2) == 2
    assert len(row3) == 2
    assert len(row4) == 1
    assert len(row5) == 1

    assert row1[0].text == 'Add 🆕'
    assert row1[0].callback_data == 'add_peer'
    assert row2[0].text == 'Rick'
    assert row2[0].callback_data == 'peer:uML8vYZpJ4kgq0luCPNC3Rpis8SYuj2+bXhR2nb78Fo='
    assert row2[1].text == 'Daryl'
    assert row2[1].callback_data == 'peer:SFJZvvuVJscdDoVUSwHJ0vNKDakAnVmhgjASMqCVtGs='
    assert row3[0].text == 'Shane'
    assert row3[0].callback_data == 'peer:CDKhm4wqrj5OAJuA7yn8SmYsRCsMlC23AmkJXBAGGH4='
    assert row3[1].text == 'Carl'
    assert row3[1].callback_data == 'peer:GClFQddt6d9PUauk1RVKQ7pMsJOJ94OiLR0no1ao/ns='
    assert row4[0].text == 'Glenn'
    assert row4[0].callback_data == 'peer:iCR9kDRwKbE/9fMoNFDyboBaH1m6pPoq4Bz+i0wCKmg='
    assert row5[0].text == '⬅ Back'
    assert row5[0].callback_data == 'server:'


@pytest.mark.parametrize('peer_is_enabled,expected_button_text,expected_callback', [
    (True, 'Disable 📵', f'selected_peer:off:{PUBLIC_KEY}'),
    (False, 'Enable ✅', f'selected_peer:on:{PUBLIC_KEY}'),
])
def test_peer_action_kb(peer_is_enabled, expected_button_text, expected_callback):
    kb = peer_action_kb(PUBLIC_KEY, peer_is_enabled).inline_keyboard

    row1 = kb[0]
    row2 = kb[1]
    row3 = kb[2]

    assert len(row1) == 2
    assert len(row2) == 1
    assert len(row3) == 1

    assert row1[0].text == 'Rename ✏️'
    assert row1[0].callback_data == f'selected_peer:name:{PUBLIC_KEY}'
    assert row1[1].text == expected_button_text
    assert row1[1].callback_data == expected_callback
    assert row2[0].text == 'Delete 🗑'
    assert row2[0].callback_data == f'selected_peer:del:{PUBLIC_KEY}'
    assert row3[0].text == '⬅ Back'
    assert row3[0].callback_data == 'config_peers'


@pytest.mark.parametrize('debug_log_enabled,expected_button_text,expected_callback', [
    (True, 'Disable debug log ⏹', 'debug_log:disable'),
    (False, 'Enable debug log 🐞', 'debug_log:enable'),
])
def test_bot_settings_kb(debug_log_enabled, expected_button_text, expected_callback):
    kb = bot_settings_kb(debug_log_enabled).inline_keyboard
    row1 = kb[0]
    assert len(row1) == 1
    assert row1[0].text == expected_button_text
    assert row1[0].callback_data == expected_callback
