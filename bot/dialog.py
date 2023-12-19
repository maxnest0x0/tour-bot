import datetime as dt

from .parser import Parser, TooLongTextError, CityParserError, DateParserError
from .tickets import TicketsSearch
from .text import Text

class Dialog:
    LIFETIME = dt.timedelta(minutes=10)

    parser = Parser()
    search = TicketsSearch()

    def __init__(self, chat):
        self.chat = chat
        self.message = None

        self.reset_state()
        self.active()

    def reset_state(self):
        self.state = {
            "origin": None,
            "destination": None,
            "start": None,
            "end": None,
        }

    def active(self):
        self.last_active = dt.datetime.now()

    def is_expired(self):
        now = dt.datetime.now()
        return now > self.last_active + self.LIFETIME

    async def process_text(self, text):
        await self.send(Text.processing_input(), True)

        try:
            await self.parser.parse(text, self.state)
        except CityParserError as error:
            await self.edit(Text.city_error() + "\n> " + error.args[0])
            raise error
        except DateParserError as error:
            await self.edit(Text.date_error() + "\n> " + error.args[0])
            raise error
        except TooLongTextError as error:
            await self.edit(Text.too_long_error())
            raise error
        except Exception as error:
            await self.edit(Text.unknown_error())
            self.reset_state()
            raise error

        keys = self.parser.get_missing_keys(self.state)
        if keys:
            await self.edit(Text.missing_keys(keys))
            self.message = None
            return

        await self.edit(Text.searching())
        try:
            res = await self.search.search(self.state)
            text = await self.search.make_text(res)
        except Exception as error:
            await self.edit(Text.unknown_error())
            self.reset_state()
            raise error

        await self.edit(text)
        self.message = None
        self.reset_state()

    async def send(self, text, save=False):
        message = await self.chat.send_message(text)

        if save:
            self.message = message

    async def edit(self, text):
        await self.message.edit_text(text)
