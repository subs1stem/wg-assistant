from io import BytesIO
from os import environ

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.input_file import BufferedInputFile

from modules.fsm_states import AddPeer
from modules.keyboards import main_menu_keyboard
from wireguard.ssh import SSH

router = Router()


@router.message(lambda message: str(message.chat.id) not in environ['ADMIN_ID'].split(','))
async def auth_error(message: Message):
    await message.answer('Я тебя не знаю ⚠')


@router.message(Command('start'))
async def welcome(message: Message):
    username = message.chat.username
    if not username:
        username = '%username%'
    await message.answer(f'Привет, {username}! 👋')


@router.message(Command('menu'))
async def main_menu(message: Message):
    await message.answer('Главное меню:', reply_markup=main_menu_keyboard())


@router.message(AddPeer.waiting_for_peer_name)
async def check_peer_name(message: Message, state: FSMContext):
    await message.answer_chat_action(action='upload_photo')
    data = SSH().add_peer(message.text)
    img_buf = BytesIO()
    data[0].save(img_buf)
    img_buf.seek(0)
    await message.answer_photo(photo=BufferedInputFile(img_buf.read(), 'qr'),
                               caption=data[1])
    img_buf.close()
    await state.clear()


@router.message()
async def send_unknown_message(message: Message):
    await message.answer('Я тебя не понимаю\nИспользуй команды ⬇')
