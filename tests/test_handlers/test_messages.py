from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Chat

from wg_assistant.handlers.messages import check_peer_name, check_new_name, send_unknown_message
from wg_assistant.wireguard.wireguard import WireGuard


@patch('wg_assistant.handlers.messages.back_btn', return_value='mock_kb')
@patch('wg_assistant.handlers.messages.qrcode.make')
@patch('wg_assistant.handlers.messages.BufferedInputFile')
async def test_check_peer_name(mock_buffered_input_file, mock_qrcode_make, mock_back_btn):
    mock_image = MagicMock()
    mock_image.save.side_effect = lambda buf: buf.write(b'qr_code_bytes')
    mock_qrcode_make.return_value = mock_image

    message = MagicMock(
        spec=Message,
        text='test_peer',
        chat=MagicMock(spec=Chat, id=123),
        bot=MagicMock(spec=Bot, send_chat_action=AsyncMock()),
        answer_photo=AsyncMock(),
    )

    state = MagicMock(spec=FSMContext, set_state=AsyncMock())
    server = MagicMock(spec=WireGuard, add_peer=MagicMock(return_value='peer_config'))

    await check_peer_name(message, state, server)

    message.bot.send_chat_action.assert_awaited_once_with(123, action='upload_photo')
    server.add_peer.assert_called_once_with('test_peer')

    mock_qrcode_make.assert_called_once_with(
        'peer_config',
        image_factory=mock_qrcode_make.call_args.kwargs['image_factory'],
    )

    mock_buffered_input_file.assert_called_once_with(b'qr_code_bytes', 'qr')
    mock_back_btn.assert_called_once_with('config_peers')

    message.answer_photo.assert_awaited_once_with(
        photo=mock_buffered_input_file.return_value,
        caption='peer_config',
        reply_markup='mock_kb',
    )

    state.set_state.assert_awaited_once()


@pytest.mark.parametrize('peer_pubkey,expected_peer_enabled', [
    ('IHgQ6Xdym0Z8+apaEJTgi6WclMREVvY4RKrck/2Nalw=', True),
    ('2FOgBVysbAX/2WQQpcQbVb2VyA2wdOZXTDbh/F6RxUQ=', False),
])
@patch('wg_assistant.handlers.messages.peer_action_kb', return_value='mock_kb')
async def test_check_new_name(mock_peer_action_kb, peer_pubkey, expected_peer_enabled):
    message = MagicMock(spec=Message, text='new_name', answer=AsyncMock())

    state = MagicMock(
        spec=FSMContext,
        get_data=AsyncMock(return_value={'pubkey': peer_pubkey}),
        set_state=AsyncMock(),
    )

    server = MagicMock(
        spec=WireGuard,
        rename_peer=MagicMock(),
        get_peer_enabled=MagicMock(return_value=expected_peer_enabled),
    )

    await check_new_name(message, state, server)

    state.get_data.assert_awaited_once()
    server.rename_peer.assert_called_once_with(peer_pubkey, 'new_name')
    server.get_peer_enabled.assert_called_once_with(peer_pubkey)
    mock_peer_action_kb.assert_called_once_with(peer_pubkey, expected_peer_enabled)
    message.answer.assert_awaited_once_with(text='Choose an action:', reply_markup='mock_kb')
    state.set_state.assert_awaited_once()


async def test_send_unknown_message():
    message = MagicMock(spec=Message, answer=AsyncMock())
    await send_unknown_message(message)
    message.answer.assert_awaited_once_with("I don't understand you.\nUse commands ⬇")
