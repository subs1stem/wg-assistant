from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from modules.keyboards import main_menu_kb

router = Router()


@router.message(Command('start'))
async def welcome(message: Message):
    username = message.chat.username
    if not username:
        username = '%username%'
    await message.answer(f'Привет, {username}! 👋')


@router.message(Command('menu'))
async def main_menu(message: Message):
    await message.answer('Главное меню:', reply_markup=main_menu_kb())
