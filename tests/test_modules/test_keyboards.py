import pytest

from wg_assistant.modules.keyboards import *


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
    pass


def test_peers_kb():
    pass


def test_peer_action_kb():
    pass


def test_bot_settings_kb():
    pass
