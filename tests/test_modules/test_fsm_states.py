from aiogram.fsm.state import State, StatesGroup

from wg_assistant.modules.fsm_states import AddPeer, RenamePeer


def test_add_peer_state():
    assert isinstance(AddPeer.waiting_for_peer_name, State)
    assert AddPeer.waiting_for_peer_name.state == 'AddPeer:waiting_for_peer_name'


def test_rename_peer_state():
    assert isinstance(RenamePeer.waiting_for_new_name, State)
    assert RenamePeer.waiting_for_new_name.state == 'RenamePeer:waiting_for_new_name'


def test_add_peer_class_is_states_group():
    assert isinstance(AddPeer, type)
    assert issubclass(AddPeer, StatesGroup)


def test_rename_peer_class_is_states_group():
    assert isinstance(RenamePeer, type)
    assert issubclass(RenamePeer, StatesGroup)
