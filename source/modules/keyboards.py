from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def back_button(callback_data):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('⬅ Назад', callback_data=callback_data))
    return markup


def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('Список пиров 🤝', callback_data='get_peers'),
               InlineKeyboardButton('Посмотреть конфиг ⚙', callback_data='get_raw_config'),
               InlineKeyboardButton('Перезагрузить сервер 🔄', callback_data='reboot_server'))
    return markup
