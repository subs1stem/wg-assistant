from aiogram.dispatcher.filters.state import State, StatesGroup


class AddPeer(StatesGroup):
    waiting_for_peer_name = State()
