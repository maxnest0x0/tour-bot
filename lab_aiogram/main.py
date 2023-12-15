from aiogram.utils import executor
from aiogram.types import Message, CallbackQuery
from bot import dp
from markups import *

@dp.message_handler(commands="start")
async def start_handler(message: Message):
    await message.answer("Привет, нажми на кнопку, чтобы начать!", reply_markup=reply_markup)

@dp.callback_query_handler()
async def button(call: CallbackQuery):
    if call.data == 'start':
        await call.message.edit_text("Добро пожаловать в мир путешествий! Я – Тур Бот, ваш гид в мире открытий. Готовы начать приключение?")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)