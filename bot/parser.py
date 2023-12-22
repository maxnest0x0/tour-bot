import re
import datetime as dt

from ai.ai_parsers.city import CityParser
from ai.re_parsers.date import DateParser

class ParserError(Exception):
    pass

class TooLongTextError(ParserError):
    pass

class Parser:
    MAX_LENGTH = 100

    def __init__(self):
        self.city_parser = CityParser()
        self.date_parser = DateParser()

    async def parse(self, text, state):
        if len(text) > self.MAX_LENGTH:
            raise TooLongTextError("Text is too long")

        text = text.strip()
        text = re.sub(r"\s+", " ", text)

        new_state = state
        new_state = await self.city_parser.parse(text, new_state)
        new_state = self.date_parser.parse(text, new_state)

        state.update(new_state)

    def get_missing_keys(self, state):
        keys = []
        for key in ("origin", "destination", "start"):
            if state[key] is None:
                keys.append(key)

        return keys
