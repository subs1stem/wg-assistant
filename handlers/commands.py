from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from data.servers import get_server_list
from modules.fsm_states import CurrentServer
from modules.keyboards import servers_kb

router = Router()


@router.message(Command('start'))
async def welcome(message: Message):
    username = message.chat.username
    if not username:
        username = '%username%'
    await message.answer(f'Привет, {username}! 👋')


@router.message(Command('servers'))
async def servers(message: Message, state: FSMContext):
    server_list = await get_server_list()
    await message.answer('Список серверов:', reply_markup=servers_kb(server_list))
    await state.set_state(CurrentServer.waiting_for_server)
