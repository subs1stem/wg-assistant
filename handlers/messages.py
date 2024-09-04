from io import BytesIO

import qrcode
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.input_file import BufferedInputFile

from modules.fsm_states import AddPeer, RenamePeer
from wireguard.wireguard import WireGuard

router = Router()


@router.message(AddPeer.waiting_for_peer_name)
async def check_peer_name(message: Message, state: FSMContext, server: WireGuard):
    await message.bot.send_chat_action(message.chat.id, action='upload_photo')
    client_config = server.add_peer(message.text)

    with BytesIO() as img_buf:
        qr = qrcode.make(client_config)
        qr.save(img_buf)
        img_buf.seek(0)

        await message.answer_photo(
            photo=BufferedInputFile(img_buf.read(), 'qr'),
            caption=client_config,
        )

    await state.clear()


@router.message(RenamePeer.waiting_for_new_name)
async def check_new_name(message: Message, state: FSMContext, server: WireGuard):
    state_data = await state.get_data()
    pubkey = state_data.get('pubkey')
    server.rename_peer(pubkey, message.text)
    await state.clear()


@router.message()
async def send_unknown_message(message: Message):
    await message.answer("I don't understand you.\nUse commands ⬇")
