from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from wireguard.ssh import SSH


def back_btn(callback_data):
    kb = InlineKeyboardBuilder()
    kb.button(text='⬅️ Назад', callback_data=callback_data)
    return kb.as_markup()


def cancel_btn(callback_data):
    kb = InlineKeyboardBuilder()
    kb.button(text='Отменить ❌', callback_data=callback_data)
    return kb.as_markup()


def servers_kb(servers):
    kb = InlineKeyboardBuilder()

    for name in servers:
        kb.button(text=name, callback_data=f'server:{name}')

    return kb.adjust(1).as_markup()


def wg_options_kb(interface_is_up):
    kb = InlineKeyboardBuilder()
    kb.button(text='Состояние пиров 📝', callback_data='get_peers')
    kb.button(text='Управление 🎛', callback_data='config_peers')
    kb.button(text='Конфигурация ⚙️', callback_data='get_server_config')
    if interface_is_up:
        kb.button(text='Отключить ⬇️', callback_data='wg_state:down')
    else:
        kb.button(text='Включить ⬆️', callback_data='wg_state:up')
    kb.button(text='Перезагрузить 🔄', callback_data='reboot_server')
    kb.button(text='⬅ К списку серверов', callback_data='servers')
    return kb.adjust(1, 2).as_markup()


def peer_list_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Обновить 🔄', callback_data='get_peers')
    kb.button(text='⬅ Назад', callback_data='server:')
    return kb.adjust(1).as_markup()


def config_peers_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Отключить 😶', callback_data='off_peer')
    kb.button(text='Удалить 🗑️', callback_data='del_peer')
    return kb.as_markup()


def peers_kb(peer_names):
    kb = InlineKeyboardBuilder()
    kb.row_width = 2
    kb.button(text='Добавить клиента 🆕', callback_data='add_peer')
    for key in peer_names:
        kb.button(text=f'{peer_names[key]}', callback_data=f'peer:{key}')
    kb.adjust(1, 2)
    kb.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='server:'), width=1)
    return kb.as_markup()


def peer_action_kb(pubkey):
    kb = InlineKeyboardBuilder()
    kb.row_width = 1
    if SSH().get_peer_enabled(pubkey):
        kb.button(text='Отключить 📵', callback_data=f'off_peer:{pubkey}')
    else:
        kb.button(text='Включить ✅', callback_data=f'on_peer:{pubkey}')
    kb.button(text='Удалить 🗑', callback_data=f'del_peer:{pubkey}')
    kb.button(text='⬅️ Назад', callback_data='config_peers')
    return kb.as_markup()
