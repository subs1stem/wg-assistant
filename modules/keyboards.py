from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


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


def peers_kb(peers):
    kb = InlineKeyboardBuilder()
    kb.button(text='Добавить клиента 🆕', callback_data='add_peer')
    for name, pubkey in peers.items():
        kb.button(text=f'{name}', callback_data=f'peer:{pubkey}')
    kb.adjust(1, 2)
    kb.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='server:'), width=1)
    return kb.as_markup()


def peer_action_kb(pubkey, peer_is_enabled):
    kb = InlineKeyboardBuilder()
    if peer_is_enabled:
        kb.button(text='Отключить 📵', callback_data=f'selected_peer:off:{pubkey}')
    else:
        kb.button(text='Включить ✅', callback_data=f'selected_peer:on:{pubkey}')
    kb.button(text='Удалить 🗑', callback_data=f'selected_peer:del:{pubkey}')
    kb.button(text='⬅️ Назад', callback_data='config_peers')
    return kb.adjust(2, 1).as_markup()
