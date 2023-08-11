from io import BytesIO
from os import environ

from aiogram import types
from aiogram.dispatcher import FSMContext

from modules.fsm_states import AddPeer
from modules.keyboards import main_menu_keyboard
from wireguard.ssh import SSH


async def set_message_handlers(dp):
    @dp.message_handler(lambda message: str(message.chat.id) not in environ['ADMIN_ID'].split(','))
    async def send_auth_error(message: types.Message):
        await message.answer('Я тебя не знаю ⚠')

    @dp.message_handler(commands=['start'])
    async def send_welcome(message: types.Message):
        username = message.chat.username
        if not username:
            username = '%username%'
        await message.answer(f'Привет, {username}! 👋')

    @dp.message_handler(commands=['menu'])
    async def send_main_menu(message: types.Message):
        await message.answer('Главное меню:', reply_markup=main_menu_keyboard())

    @dp.message_handler(state=AddPeer.waiting_for_peer_name)
    async def check_peer_name(message: types.Message, state: FSMContext):
        await message.answer_chat_action(action='upload_photo')
        data = SSH().add_peer(message.text)
        img_buf = BytesIO()
        data[0].save(img_buf)
        img_buf.seek(0)
        await message.answer_photo(photo=img_buf.read(),
                                   caption=data[1])
        img_buf.close()
        await state.finish()

    @dp.message_handler(content_types=types.ContentTypes.ANY)
    async def send_unknown_message(message: types.Message):
        await message.answer('Я тебя не понимаю\nИспользуй команды ⬇')
