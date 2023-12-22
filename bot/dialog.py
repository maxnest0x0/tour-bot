import datetime as dt
import telegram as tg

from .parser import InputParser, TooLongTextError
from ai.ai_parsers.city import CityParserError
from ai.re_parsers.date import DateParserError
from .tickets import TicketsSearch
from .text import Text

class Dialog:
    LIFETIME = dt.timedelta(minutes=10)

    parser = InputParser()
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
            self.state = await self.parser.parse(text, self.state)
        except CityParserError as error:
            await self.edit(Text.city_error() + "\n" + Text.error_text(str(error)))
            raise error
        except DateParserError as error:
            await self.edit(Text.date_error() + "\n" + Text.error_text(str(error)))
            raise error
        except TooLongTextError as error:
            await self.edit(Text.too_long_error())
            raise error
        except Exception as error:
            await self.edit(Text.unknown_error())
            self.reset_state()
            raise error

        keys = self.parser.get_missing_params(self.state)
        if keys:
            text = Text.current_state(self.state) + "\n\n" + Text.missing_keys(keys)
            await self.edit(text)

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
        message = await self.chat.send_message(text, tg.constants.ParseMode.HTML, True)

        if save:
            self.message = message

    async def edit(self, text):
        await self.message.edit_text(text, tg.constants.ParseMode.HTML, True)
