from os import environ

from aiogram import Router
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message(lambda message: str(message.chat.id) not in environ['ADMIN_ID'].split(','))
async def auth_error(message: Message):
    await message.answer('Я Вас не знаю ⚠')


@router.callback_query(lambda callback: str(callback.from_user.id) not in environ['ADMIN_ID'].split(','))
async def access_denied(callback: CallbackQuery):
    await callback.answer(text='Вы были заблокированы 🛑', show_alert=True)
