from io import BytesIO

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.input_file import BufferedInputFile

from modules.fsm_states import AddPeer
from modules.keyboards import back_btn
from wireguard.linux import Linux

router = Router()


@router.message(AddPeer.waiting_for_peer_name)
async def check_peer_name(message: Message, state: FSMContext, server: Linux):
    await message.bot.send_chat_action(message.chat.id, action='upload_photo')
    data = server.add_peer(message.text)

    with BytesIO() as img_buf:
        data[0].save(img_buf)
        img_buf.seek(0)

        await message.answer_photo(
            photo=BufferedInputFile(img_buf.read(), 'qr'),
            caption=data[1],
            reply_markup=back_btn('config_peers'),
        )

    await state.clear()


@router.message()
async def send_unknown_message(message: Message):
    await message.answer('Я тебя не понимаю\nИспользуй команды ⬇')
