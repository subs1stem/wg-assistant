from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from modules.keyboards import servers_kb

router = Router()


@router.message(Command('start'))
async def send_welcome(message: Message):
    username = message.chat.username
    if not username:
        username = '%username%'
    await message.answer(f'Привет, {username}! 👋')


@router.message(Command('servers'))
async def send_servers(message: Message, state: FSMContext, servers: dict):
    await state.clear()
    server_names = list(servers.keys())
    await message.answer('Список серверов:', reply_markup=servers_kb(server_names))
