import os
import telegram.ext as ext

from .handlers import Handlers

class Bot:
    def __init__(self):
        self.handlers = Handlers(self)
        self.dialogs = {}

        builder = ext.ApplicationBuilder()
        builder.concurrent_updates(True)
        builder.token(os.environ["TOKEN"])

        self.app = builder.build()
        self.set_handlers()
        self.run()

    def set_handlers(self):
        self.app.add_handler(ext.CommandHandler("start", self.handlers.start))
        self.app.add_handler(ext.MessageHandler(ext.filters.TEXT & ~ext.filters.COMMAND, self.handlers.message))

    def run(self):
        self.app.run_polling()
