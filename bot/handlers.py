from __future__ import annotations
import telegram as tg
import telegram.ext as ext
from typing import TYPE_CHECKING

from .dialog import Dialog
from .text import Text

if TYPE_CHECKING:
    from .app import Bot

class Handlers:
    def __init__(self, bot: Bot):
        self._bot = bot

    async def _send(self, update: tg.Update, text: str) -> None:
        assert update.message is not None
        await update.message.reply_text(Text.welcome(), tg.constants.ParseMode.HTML, True)

    async def start(self, update: tg.Update, context: ext.ContextTypes.DEFAULT_TYPE) -> None:
        if update.message is not None:
            await self._send(update, Text.welcome())

    async def message(self, update: tg.Update, context: ext.ContextTypes.DEFAULT_TYPE) -> None:
        if update.message is None or update.effective_chat is None:
            return

        chat_id = update.effective_chat.id

        if chat_id in self._bot.dialogs:
            dialog = self._bot.dialogs[chat_id]
            if not dialog.is_alive():
                del self._bot.dialogs[chat_id]

        if chat_id not in self._bot.dialogs:
            self._bot.dialogs[chat_id] = Dialog(update.effective_chat)

        dialog = self._bot.dialogs[chat_id]

        if not dialog.is_busy():
            await dialog.process_input(update.message.text)
        else:
            await self._send(update, Text.busy())
