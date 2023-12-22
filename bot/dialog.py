import datetime as dt
import telegram as tg
from typing import Final, Optional

from .parser import InputParser, TooLongTextError
from parsers.city import CityParserError
from parsers.date import DateParserError
from .aggregator import TicketAggregator
from .text import Text
from .data_types import ParamsState

parser = InputParser()
aggregator = TicketAggregator()

class Dialog:
    LIFETIME: Final = dt.timedelta(minutes=10)

    def __init__(self, chat: tg.Chat):
        self._chat = chat
        self._message: Optional[tg.Message] = None
        self._busy = False
        self._done = False
        self._active()

        self._state: ParamsState = {
            "origin": None,
            "destination": None,
            "start": None,
            "end": None,
        }

    def _active(self) -> None:
        self._last_active = dt.datetime.now()

    def is_alive(self) -> bool:
        now = dt.datetime.now()
        return not self._done and now < self._last_active + self.LIFETIME

    def is_busy(self) -> bool:
        return self._busy

    async def process_input(self, text: str) -> None:
        self._busy = True
        self._active()
        await self._send(Text.processing_input())

        res = await self._parse_text(text)
        if not res:
            self._busy = False
            return

        res = await self._check_for_missing_params()
        if not res:
            self._busy = False
            return

        await self._edit(Text.searching())
        await self._search_tickets()
        self._done = True

    async def _parse_text(self, text: str) -> bool:
        try:
            self._state = await parser.parse(text, self._state)
        except CityParserError as error:
            await self._edit(Text.city_error() + "\n" + Text.error_text(str(error)))
            return False
        except DateParserError as error:
            await self._edit(Text.date_error() + "\n" + Text.error_text(str(error)))
            return False
        except TooLongTextError as error:
            await self._edit(Text.too_long_error())
            return False
        except Exception as error:
            await self._edit(Text.unknown_error())
            self._done = True
            raise error

        return True

    async def _check_for_missing_params(self) -> bool:
        missing_params = parser.get_missing_params(self._state)
        if missing_params:
            text = Text.params_state(self._state) + "\n\n" + Text.missing_params(missing_params)
            await self._edit(text)

            return False

        return True

    async def _search_tickets(self) -> bool:
        try:
            text = await aggregator.search(self._state)
        except Exception as error:
            await self._edit(Text.unknown_error())
            self._done = True
            raise error

        await self._edit(text)
        return True

    async def _send(self, text: str) -> None:
        self._message = await self._chat.send_message(text, tg.constants.ParseMode.HTML, True)

    async def _edit(self, text: str) -> None:
        assert self._message is not None
        await self._message.edit_text(text, tg.constants.ParseMode.HTML, True)
