import telegram as tg
import telegram.ext as ext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def start(update: tg.Update, context: ext.ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is not None:
        keyboard = [[InlineKeyboardButton("Начать", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Привет, нажми на кнопку, чтобы начать!", reply_markup=reply_markup)

async def button(update: tg.Update, context: ext.CallbackContext) -> None:
    query = update.callback_query
    if query.data == 'start':
        await query.message.reply_text("Добро пожаловать в мир путешествий! Я – Тур Бот, ваш гид в мире открытий. Готовы начать приключение?")
        await context.bot.delete_message(chat_id = query.message.chat_id, message_id = query.message.message_id)