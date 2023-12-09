import telegram as tg
import telegram.ext as ext

from secret import token

async def start(update: tg.Update, context: ext.ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is not None:
        await update.message.reply_text("Hello World")

if __name__ == "__main__":
    app = ext.ApplicationBuilder().concurrent_updates(True).token(token).build()

    app.add_handler(ext.CommandHandler("start", start))

    app.run_polling()
