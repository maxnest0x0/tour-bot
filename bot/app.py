import telegram.ext as ext

from .handlers import Handlers

class Bot:
    TOKEN = "6409765724:AAFx8V-167YJtdzDtfa4bmdJfVuI4Pbs2F4"

    def __init__(self):
        builder = ext.ApplicationBuilder()
        builder.concurrent_updates(True)
        builder.token(self.TOKEN)

        self.app = builder.build()
        self.set_handlers()
        self.run()

    def set_handlers(self):
        self.app.add_handler(ext.CommandHandler("start", Handlers.start))

    def run(self):
        self.app.run_polling()
