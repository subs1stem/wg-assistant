from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from wg_assistant.handlers.messages import check_new_name, send_unknown_message
from wg_assistant.wireguard.wireguard import WireGuard


@pytest.mark.skip
async def test_check_peer_name():
    pass


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
        set_state=AsyncMock()
    )

    server = MagicMock(
        spec=WireGuard,
        rename_peer=MagicMock(),
        get_peer_enabled=MagicMock(return_value=expected_peer_enabled)
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
