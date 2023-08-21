from io import BytesIO

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.input_file import BufferedInputFile

from modules.fsm_states import AddPeer
from wireguard.ssh import SSH

router = Router()


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
