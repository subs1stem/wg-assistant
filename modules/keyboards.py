from aiogram.utils.keyboard import InlineKeyboardBuilder

from wireguard.ssh import SSH


def back_button(callback_data):
    kb = InlineKeyboardBuilder()
    kb.button(text='⬅ Назад', callback_data=callback_data)
    return kb.as_markup()


def cancel_button(callback_data):
    kb = InlineKeyboardBuilder()
    kb.button(text='Отменить ❌', callback_data=callback_data)
    return kb.as_markup()


def servers_kb(servers):
    kb = InlineKeyboardBuilder()

    for serverName, serverParams in servers.items():
        kb.button(text=serverName, callback_data=f'server:{serverName}')

    return kb.as_markup()


def server_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row_width = 1
    kb.button(text='Добавить клиента 🆕', callback_data='add_peer')
    kb.button(text='Параметры WireGuard 🌐', callback_data='wg_options')
    kb.button(text='Перезагрузить сервер 🔄', callback_data='reboot_server')
    return kb.as_markup()


def wg_options_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row_width = 1
    kb.button(text='Список пиров 🤝', callback_data='get_peers')
    kb.button(text='Управление пирами 📝', callback_data='config_peers')
    kb.button(text='Конфиг сервера ⚙', callback_data='get_server_config')
    if SSH().get_wg_status():
        kb.button(text='Опустить интерфейс ⬇', callback_data='wg_state_down')
    else:
        kb.button(text='Поднять интерфейс ⬆', callback_data='wg_state_up')
    kb.button(text='⬅ Назад', callback_data='servers')
    return kb.as_markup()


def peer_list_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row_width = 1
    kb.button(text='Обновить 🔄', callback_data='get_peers')
    kb.button(text='⬅ Назад', callback_data='wg_options')
    return kb.as_markup()


def config_peers_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text='Отключить 😶', callback_data='off_peer')
    kb.button(text='Удалить 🗑️', callback_data='del_peer')
    return kb.as_markup()


def peers_keyboard():
    peers = SSH().get_peer_names()
    kb = InlineKeyboardBuilder()
    kb.row_width = 2
    for key in peers:
        kb.button(f'{peers[key]}', callback_data=f'peer:{key}')
    kb.button(text='⬅ Назад', callback_data='wg_options')
    return kb.as_markup()


def peer_action(pubkey):
    kb = InlineKeyboardBuilder()
    kb.row_width = 1
    if SSH().get_peer_enabled(pubkey):
        kb.button(text='Отключить 📵', callback_data=f'off_peer:{pubkey}')
    else:
        kb.button(text='Включить ✅', callback_data=f'on_peer:{pubkey}')
    kb.button(text='Удалить ❌', callback_data=f'del_peer:{pubkey}')
    kb.button(text='⬅ Назад', callback_data='config_peers')
    return kb.as_markup()
