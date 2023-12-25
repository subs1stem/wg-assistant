from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from modules.keyboards import servers_kb

router = Router()


@router.message(Command('start'))
async def send_start(message: Message):
    await message.answer(f'Привет, {message.chat.username or "%username%"}! 👋')


@router.message(Command('servers'))
async def send_servers(message: Message, servers: dict):
    server_names = list(servers.keys())
    await message.answer('Список серверов:', reply_markup=servers_kb(server_names))
