from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from modules.keyboards import servers_kb, bot_settings_kb

router = Router()


@router.message(CommandStart())
async def send_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f'Hello, {message.chat.username or "%username%"}! 👋')


@router.message(Command('servers'))
async def send_servers(message: Message, servers: dict, state: FSMContext):
    await state.clear()
    server_names = list(servers.keys())
    await message.answer('Server list:', reply_markup=servers_kb(server_names))


@router.message(Command('settings'))
async def send_settings(message: Message):
    await message.answer('Bot settings:', reply_markup=bot_settings_kb(False))
