from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup



reply_markup = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Начать", callback_data='start'))