import os
import telegram.ext as ext

from .handlers import Handlers
from .dialog import Dialog

class BotError(Exception):
    pass

class Bot:
    def __init__(self) -> None:
        self._handlers = Handlers(self)
        self.dialogs: dict[int, Dialog] = {}

        token = os.environ.get("TOKEN")
        if token is None:
            raise BotError("TOKEN env variable not found")

        builder = ext.ApplicationBuilder()
        builder.concurrent_updates(True)
        builder.token(token)

        self.app = builder.build()
        self._set_handlers()

    def _set_handlers(self) -> None:
        self.app.add_handler(ext.CommandHandler("start", self._handlers.start))
        self.app.add_handler(ext.MessageHandler(ext.filters.TEXT & ~ext.filters.COMMAND, self._handlers.message))

    def run(self) -> None:
        self.app.run_polling()
