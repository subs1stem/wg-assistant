from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def back_button(callback_data):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('⬅ Назад', callback_data=callback_data))
    return markup


def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('Параметры WireGuard 🌐', callback_data='wg_options'),
               InlineKeyboardButton('Перезагрузить сервер 🔄', callback_data='reboot_server'))
    return markup


def wg_options_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('Список пиров 🤝', callback_data='get_peers'),
               InlineKeyboardButton('Конфиг сервера ⚙', callback_data='get_server_config'),
               InlineKeyboardButton('⬅ Назад', callback_data='main_menu'))
    return markup
