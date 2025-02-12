from io import BytesIO

import qrcode
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.input_file import BufferedInputFile
from qrcode.image.pure import PyPNGImage

from modules.fsm_states import AddPeer, RenamePeer
from modules.keyboards import peer_action_kb, back_btn
from wireguard.wireguard import WireGuard

router = Router()


@router.message(AddPeer.waiting_for_peer_name)
async def check_peer_name(message: Message, state: FSMContext, server: WireGuard):
    await message.bot.send_chat_action(message.chat.id, action='upload_photo')
    client_config = server.add_peer(message.text)

    img_buf = BytesIO()
    qrcode.make(client_config, image_factory=PyPNGImage).save(img_buf)

    await message.answer_photo(
        photo=BufferedInputFile(img_buf.getvalue(), 'qr'),
        caption=client_config,
        reply_markup=back_btn('config_peers'),
    )

    await state.set_state()


@router.message(RenamePeer.waiting_for_new_name)
async def check_new_name(message: Message, state: FSMContext, server: WireGuard):
    state_data = await state.get_data()
    pubkey = state_data.get('pubkey')
    server.rename_peer(pubkey, message.text)

    peer_is_enabled = server.get_peer_enabled(pubkey)
    await message.answer(text=f'Choose an action:', reply_markup=peer_action_kb(pubkey, peer_is_enabled))

    await state.set_state()


@router.message()
async def send_unknown_message(message: Message):
    await message.answer("I don't understand you.\nUse commands ⬇")
