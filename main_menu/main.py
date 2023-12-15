import telegram.ext as ext
from markups import start, button
from secret import token
    

if __name__ == "__main__":
    app = ext.ApplicationBuilder().concurrent_updates(True).token(token).build()
    app.add_handler(ext.CommandHandler("start", start))
    app.add_handler(ext.CallbackQueryHandler(button))
    app.run_polling()