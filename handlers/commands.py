from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from modules.keyboards import servers_kb

router = Router()


@router.message(Command('start'))
async def welcome(message: Message):
    username = message.chat.username
    if not username:
        username = '%username%'
    await message.answer(f'Привет, {username}! 👋')


@router.message(Command('servers'))
async def servers(message: Message):
    await message.answer('Список серверов:', reply_markup=servers_kb())
