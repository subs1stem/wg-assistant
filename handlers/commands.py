from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from modules.keyboards import servers_kb

router = Router()


@router.message(CommandStart())
async def send_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f'Привет, {message.chat.username or "%username%"}! 👋')


@router.message(Command('servers'))
async def send_servers(message: Message, state: FSMContext, servers: dict):
    await state.clear()
    server_names = list(servers.keys())
    await message.answer('Список серверов:', reply_markup=servers_kb(server_names))
