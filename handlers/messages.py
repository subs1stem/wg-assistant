from io import BytesIO

from aiogram import Router, flags
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.input_file import BufferedInputFile
from aiogram.utils.chat_action import ChatActionMiddleware

from modules.fsm_states import AddPeer
from wireguard.ssh import SSH

router = Router()

router.message.middleware(ChatActionMiddleware())


@router.message(AddPeer.waiting_for_peer_name)
@flags.chat_action(action='upload_photo')  # TODO: something's wrong with this
async def check_peer_name(message: Message, state: FSMContext, server: SSH):
    data = server.add_peer(message.text)

    with BytesIO() as img_buf:
        data[0].save(img_buf)
        img_buf.seek(0)

        await message.answer_photo(
            photo=BufferedInputFile(img_buf.read(), 'qr'),
            caption=data[1]
        )

    await state.clear()


@router.message()
async def send_unknown_message(message: Message):
    await message.answer('Я тебя не понимаю\nИспользуй команды ⬇')
