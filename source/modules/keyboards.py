from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def back_button(callback_data):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('⬅ Назад', callback_data=callback_data))
    return markup


def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Посмотреть конфиг ⚙', callback_data='get_raw_config'))
    return markup
