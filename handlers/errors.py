from aiogram import Router, F
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent, CallbackQuery

router = Router()


@router.error(ExceptionTypeFilter(ConnectionError), F.update.callback_query.as_('callback'))
async def handle_connection_error(_, callback: CallbackQuery):
    await callback.answer(f'Ошибка подключения к серверу ⚠️', show_alert=True)


@router.error(F.update.callback_query.as_('callback'))
async def handle_error(event: ErrorEvent, callback: CallbackQuery):
    print(event.exception)
    await callback.answer(f'Неизвестная ошибка ⚠️', show_alert=True)
