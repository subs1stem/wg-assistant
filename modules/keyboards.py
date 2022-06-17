from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from wireguard.ssh import SSH


def back_button(callback_data):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('⬅ Назад', callback_data=callback_data))
    return markup


def cancel_button(callback_data):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Отменить ❌', callback_data=callback_data))
    return markup


def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('Добавить клиента 🆕', callback_data='add_peer'),
               InlineKeyboardButton('Параметры WireGuard 🌐', callback_data='wg_options'),
               InlineKeyboardButton('Перезагрузить сервер 🔄', callback_data='reboot_server'))
    return markup


def wg_options_keyboard():
    if SSH().get_wg_status():
        wg_updown_btn = InlineKeyboardButton('Опустить интерфейс ⬇', callback_data='wg_state_down')
    else:
        wg_updown_btn = InlineKeyboardButton('Поднять интерфейс ⬆', callback_data='wg_state_up')
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('Список пиров 🤝', callback_data='get_peers'),
               InlineKeyboardButton('Конфиг сервера ⚙', callback_data='get_server_config'),
               wg_updown_btn,
               InlineKeyboardButton('⬅ Назад', callback_data='main_menu'))
    return markup


def peer_list_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('Обновить 🔄', callback_data='get_peers'),
               InlineKeyboardButton('⬅ Назад', callback_data='wg_options'))
    return markup
