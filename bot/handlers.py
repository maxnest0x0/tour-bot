import telegram as tg
import telegram.ext as ext

from .dialog import Dialog
from .text import Text

class Handlers:
    def __init__(self, bot):
        self.bot = bot

    async def start(self, update: tg.Update, context: ext.ContextTypes.DEFAULT_TYPE):
        if update.message is not None:
            await update.message.reply_text(Text.welcome())

    async def message(self, update: tg.Update, context: ext.ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id

        if chat_id in self.bot.dialogs:
            dialog = self.bot.dialogs[chat_id]
            if dialog.is_expired():
                del self.bot.dialogs[chat_id]

        if chat_id not in self.bot.dialogs:
            self.bot.dialogs[chat_id] = Dialog(update.effective_chat)

        dialog = self.bot.dialogs[chat_id]
        dialog.active()

        if dialog.message is None:
            dialog.message = True

            try:
                await dialog.process_text(update.message.text)
            except Exception as error:
                dialog.message = None
                raise error
        else:
            await dialog.send(Text.busy())
