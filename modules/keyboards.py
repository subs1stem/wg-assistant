from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def back_btn(callback_data):
    kb = InlineKeyboardBuilder()
    kb.button(text='⬅ Back', callback_data=callback_data)
    return kb.as_markup()


def cancel_btn(callback_data):
    kb = InlineKeyboardBuilder()
    kb.button(text='Cancel ❌', callback_data=callback_data)
    return kb.as_markup()


def yes_no_kb(callback_data):
    kb = InlineKeyboardBuilder()
    kb.button(text='Yes ✅', callback_data=f'{callback_data}:yes')
    kb.button(text='No ❌', callback_data=f'{callback_data}:no')
    return kb.as_markup()


def servers_kb(servers):
    kb = InlineKeyboardBuilder()

    for name in servers:
        kb.button(text=name, callback_data=f'server:{name}')

    return kb.adjust(1).as_markup()


def wg_options_kb(interface_is_up):
    kb = InlineKeyboardBuilder()
    kb.button(text='Status 📝', callback_data='get_peers')
    kb.button(text='Management 🎛', callback_data='config_peers')
    kb.button(text='Configuration ⚙️', callback_data='get_server_config')
    if interface_is_up:
        kb.button(text='Disable interface ⬇️', callback_data='wg_state:down')
    else:
        kb.button(text='Enable interface ⬆️', callback_data='wg_state:up')
    kb.button(text='Reboot host 🔄', callback_data='reboot_host')
    kb.button(text='⬅ Go to server list', callback_data='servers')
    return kb.adjust(1, 2).as_markup()


def peer_list_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Refresh 🔄', callback_data='get_peers')
    kb.button(text='⬅ Back', callback_data='server:')
    return kb.adjust(1).as_markup()


def peers_kb(peers):
    kb = InlineKeyboardBuilder()
    kb.button(text='Add 🆕', callback_data='add_peer')
    for name, pubkey in peers.items():
        kb.button(text=f'{name}', callback_data=f'peer:{pubkey}')
    kb.adjust(1, 2)
    kb.row(InlineKeyboardButton(text='⬅ Back', callback_data='server:'), width=1)
    return kb.as_markup()


def peer_action_kb(pubkey, peer_is_enabled):
    kb = InlineKeyboardBuilder()
    kb.button(text='Rename ✏️', callback_data=f'selected_peer:name:{pubkey}')
    if peer_is_enabled:
        kb.button(text='Disable 📵', callback_data=f'selected_peer:off:{pubkey}')
    else:
        kb.button(text='Enable ✅', callback_data=f'selected_peer:on:{pubkey}')
    kb.button(text='Delete 🗑', callback_data=f'selected_peer:del:{pubkey}')
    kb.button(text='⬅ Back', callback_data='config_peers')
    return kb.adjust(2, 1).as_markup()


def bot_settings_kb(debug_log_enabled):
    kb = InlineKeyboardBuilder()
    if debug_log_enabled:
        kb.button(text='Disable debug log ⏹', callback_data='debug_log:disable')
    else:
        kb.button(text='Enable debug log 🐞', callback_data='debug_log:enable')
    return kb.as_markup()
