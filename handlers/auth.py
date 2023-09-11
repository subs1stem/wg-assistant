from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message(~F.chat.id.in_([]))
async def send_auth_error(message: Message):
    await message.answer('Я Вас не знаю ⚠')


@router.callback_query(~F.from_user.in_([]))
async def send_access_denied(callback: CallbackQuery):
    await callback.answer(text='Вы были заблокированы 🛑', show_alert=True)
