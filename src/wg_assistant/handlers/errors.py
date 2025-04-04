import logging

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent, CallbackQuery

router = Router()


@router.error(ExceptionTypeFilter(ConnectionError), F.update.callback_query.as_('callback'))
async def handle_connection_error(_, callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer(f'Server connection error ⚠️', show_alert=True)
    logging.info('Error connecting to the server, state cleared')


@router.error(ExceptionTypeFilter(TelegramBadRequest), F.update.callback_query.as_('callback'))
async def handle_message_is_not_modified(event: ErrorEvent, callback: CallbackQuery):
    if 'message is not modified' in str(event.exception):
        logging.debug(f'Ignored error: "{event.exception}"')
    else:
        await handle_error(event, callback)


@router.error(F.update.callback_query.as_('callback'))
async def handle_error(event: ErrorEvent, callback: CallbackQuery):
    await callback.answer(f'Unknown error ⚠️', show_alert=True)
    logging.error(event.exception)
