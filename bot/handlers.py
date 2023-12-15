import telegram as tg
import telegram.ext as ext

class Handlers:
    @staticmethod
    async def start(update: tg.Update, context: ext.ContextTypes.DEFAULT_TYPE):
        if update.message is not None:
            await update.message.reply_text("Hello World")
